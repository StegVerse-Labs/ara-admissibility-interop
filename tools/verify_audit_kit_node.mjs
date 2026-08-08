#!/usr/bin/env node
/** Independent Node.js StegGate Audit Kit verifier. No Python implementation code is imported. */
import { createHash } from 'node:crypto';
import { cpSync, mkdtempSync, readFileSync, rmSync, unlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { canonicalize, contentId } from './canonicalize_steggate_node.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const DEFAULT_CASES = join(ROOT, 'fixtures', 'verifier', 'cases.json');
const REASON_REGISTRY = join(ROOT, 'reasons', 'registry.v1.json');
const REQUIRED_ROLES = new Set(['candidate', 'policy_authority_evidence', 'decision', 'receipt', 'coverage', 'verifier_inputs']);
const FORBIDDEN_KEYS = new Set(['credential', 'credentials', 'password', 'private_prompt', 'provider_response', 'secret', 'token']);
const ALLOWED_DECISIONS = new Set(['ALLOW', 'DENY', 'REVIEW', 'FAIL_CLOSED']);
const ASSURANCE_DIMENSIONS = new Set(['identity', 'signatures', 'trust_anchor', 'source_evidence', 'capability_construction']);

function load(path) {
  const value = JSON.parse(readFileSync(path, 'utf8'));
  if (value === null || Array.isArray(value) || typeof value !== 'object') throw new Error(`JSON root must be an object: ${path}`);
  return value;
}

function shaBytes(bytes) {
  return `sha256:${createHash('sha256').update(bytes).digest('hex')}`;
}

function rawId(path) {
  return shaBytes(readFileSync(path));
}

function writeCanonical(path, value) {
  writeFileSync(path, canonicalize(value));
}

function reasonCodes() {
  const registry = load(REASON_REGISTRY);
  if (registry.schema_version !== 'steggate.reason-registry.v1') throw new Error('reason registry schema mismatch');
  if (registry.authority_effect !== false) throw new Error('reason registry must have authority_effect=false');
  return new Set((registry.reasons || []).map((item) => item.code));
}

function objectIndex(manifest) {
  return Object.fromEntries((manifest.objects || []).map((entry) => [entry.role, entry]));
}

function scanForbidden(value, path = '$') {
  if (Array.isArray(value)) {
    value.forEach((item, index) => scanForbidden(item, `${path}[${index}]`));
  } else if (value && typeof value === 'object') {
    for (const [key, item] of Object.entries(value)) {
      if (FORBIDDEN_KEYS.has(key.toLowerCase())) throw new Error(`forbidden embedded field at ${path}.${key}`);
      scanForbidden(item, `${path}.${key}`);
    }
  }
}

function resolveSafe(base, rel) {
  if (rel.startsWith('/') || rel.split(/[\\/]/).includes('..')) throw new Error(`unsafe evidence path: ${rel}`);
  return join(base, rel);
}

function verifyEvidencePack(manifestPath) {
  const manifest = load(manifestPath);
  if (manifest.schema_version !== 'steggate.evidence-pack-manifest.v1') throw new Error('manifest schema_version mismatch');
  if (manifest.canonicalization_profile !== 'stegverse.jcs.v1') throw new Error('canonicalization profile mismatch');
  if (!Array.isArray(manifest.trust_assumptions) || manifest.trust_assumptions.length === 0 || !Array.isArray(manifest.non_claims) || manifest.non_claims.length === 0) {
    throw new Error('trust assumptions and non-claims are required');
  }
  const assurance = manifest.achieved_assurance;
  if (!assurance || assurance.profile_ref !== 'steggate.assurance-profile.v1') throw new Error('achieved assurance report missing or unbound');
  if (!Array.isArray(manifest.objects)) throw new Error('manifest objects missing');
  const roles = manifest.objects.map((entry) => entry.role);
  if (roles.length !== REQUIRED_ROLES.size || new Set(roles).size !== REQUIRED_ROLES.size || [...REQUIRED_ROLES].some((role) => !roles.includes(role))) {
    throw new Error(`evidence-pack roles mismatch: ${JSON.stringify(roles)}`);
  }
  const base = dirname(manifestPath);
  for (const entry of manifest.objects) {
    const source = resolveSafe(base, entry.path);
    let bytes;
    try { bytes = readFileSync(source); } catch { throw new Error(`missing evidence object: ${entry.path}`); }
    const observed = shaBytes(bytes);
    if (observed !== entry.sha256) throw new Error(`hash mismatch for ${entry.path}: ${observed} != ${entry.sha256}`);
    const data = JSON.parse(bytes.toString('utf8'));
    scanForbidden(data);
    if (entry.role === 'policy_authority_evidence') {
      if (entry.sensitive_handling !== 'commitment_and_refs_only') throw new Error('policy/authority evidence must be commitment_and_refs_only');
      if (data.content_included !== false || data.commitment_only !== true) throw new Error('policy/authority fixture improperly embeds sensitive content');
    }
  }
  return { status: 'PASS', pack_id: manifest.pack_id, objects: manifest.objects.length, authority_effect: false };
}

function verifyCanonicalObject(base, entry) {
  const path = join(base, entry.path);
  const value = load(path);
  const canonicalHash = contentId(value);
  if (canonicalHash !== entry.sha256) throw new Error(`${entry.role} canonical hash mismatch: ${canonicalHash} != ${entry.sha256}`);
  if (rawId(path) !== canonicalHash) throw new Error(`${entry.role} bytes are not canonical stegverse.jcs.v1 bytes`);
  return canonicalHash;
}

export function verifySemantics(manifestPath) {
  const packResult = verifyEvidencePack(manifestPath);
  const manifest = load(manifestPath);
  const base = dirname(manifestPath);
  const objects = objectIndex(manifest);
  for (const role of ['candidate', 'decision', 'receipt', 'verifier_inputs']) if (!objects[role]) throw new Error(`missing required role: ${role}`);

  const candidate = load(join(base, objects.candidate.path));
  const decision = load(join(base, objects.decision.path));
  const receipt = load(join(base, objects.receipt.path));
  const verifierInputs = load(join(base, objects.verifier_inputs.path));

  const candidateHash = verifyCanonicalObject(base, objects.candidate);
  const decisionHash = verifyCanonicalObject(base, objects.decision);
  const receiptHash = verifyCanonicalObject(base, objects.receipt);
  verifyCanonicalObject(base, objects.verifier_inputs);

  const candidateId = candidate.candidate_id;
  if (!candidateId || decision.candidate_id !== candidateId || receipt.candidate_id !== candidateId) throw new Error('candidate_id binding mismatch across candidate/decision/receipt');
  if (!ALLOWED_DECISIONS.has(decision.decision)) throw new Error(`unsupported decision: ${decision.decision}`);
  if (receipt.decision !== decision.decision) throw new Error('receipt decision does not match reconstructed decision');
  if (!reasonCodes().has(decision.reason_code)) throw new Error(`unregistered reason_code: ${decision.reason_code}`);
  if (receipt.authority_effect !== false) throw new Error('receipt authority_effect must remain false');
  if (verifierInputs.canonicalization_profile !== 'stegverse.jcs.v1') throw new Error('verifier input canonicalization profile mismatch');
  if (verifierInputs.reason_registry !== 'reasons/registry.v1.json') throw new Error('verifier input reason registry mismatch');

  const assurance = manifest.achieved_assurance;
  if (!assurance || assurance.profile_ref !== 'steggate.assurance-profile.v1') throw new Error('achieved assurance is missing or unbound');
  const missing = [...ASSURANCE_DIMENSIONS].filter((dimension) => !(dimension in assurance));
  if (missing.length) throw new Error(`achieved assurance dimensions missing: ${JSON.stringify(missing.sort())}`);

  return {
    status: 'PASS', pack_id: packResult.pack_id, candidate_id: candidateId, decision: decision.decision,
    reason_code: decision.reason_code,
    canonical_hashes: { candidate: candidateHash, decision: decisionHash, receipt: receiptHash },
    achieved_assurance_profile: assurance.profile_ref, authority_effect: false,
    limitations: [
      'content integrity does not prove truth of policy or authority assertions',
      'offline verification does not grant consequence execution authority',
      'external identity, signature, and trust-anchor claims remain limited to achieved assurance',
    ],
  };
}

function prepareCase(sourceManifest, decisionValue, reasonCode) {
  const root = mkdtempSync(join(tmpdir(), 'steggate-node-verifier-'));
  const pack = join(root, 'pack');
  cpSync(dirname(sourceManifest), pack, { recursive: true });
  const manifestPath = join(pack, sourceManifest.split(/[\\/]/).pop());
  const manifest = load(manifestPath);
  const objects = objectIndex(manifest);
  const decisionPath = join(pack, objects.decision.path);
  const receiptPath = join(pack, objects.receipt.path);
  const decision = load(decisionPath);
  const receipt = load(receiptPath);
  decision.decision = decisionValue;
  decision.reason_code = reasonCode;
  receipt.decision = decisionValue;
  receipt.authority_effect = false;
  writeCanonical(decisionPath, decision);
  writeCanonical(receiptPath, receipt);
  objects.decision.sha256 = rawId(decisionPath);
  objects.receipt.sha256 = rawId(receiptPath);
  writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
  return { root, manifestPath };
}

function mutateCase(manifestPath, operation) {
  const manifest = load(manifestPath);
  const objects = objectIndex(manifest);
  const base = dirname(manifestPath);
  if (operation === 'candidate_content_without_manifest_update') {
    const path = join(base, objects.candidate.path);
    writeFileSync(path, Buffer.concat([readFileSync(path), Buffer.from(' ')]));
    return;
  }
  let path;
  let value;
  if (operation === 'receipt_decision_mismatch') {
    path = join(base, objects.receipt.path); value = load(path); value.decision = value.decision !== 'DENY' ? 'DENY' : 'ALLOW'; writeCanonical(path, value); objects.receipt.sha256 = rawId(path);
  } else if (operation === 'unregistered_reason') {
    path = join(base, objects.decision.path); value = load(path); value.reason_code = 'UNREGISTERED_TEST_REASON'; writeCanonical(path, value); objects.decision.sha256 = rawId(path);
  } else if (operation === 'receipt_authority_effect_true') {
    path = join(base, objects.receipt.path); value = load(path); value.authority_effect = true; writeCanonical(path, value); objects.receipt.sha256 = rawId(path);
  } else throw new Error(`unknown tamper operation: ${operation}`);
  writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
}

function verifyLegacyFixture(path) {
  const payload = load(path);
  let checked = 0;
  for (const fixture of payload.fixtures || []) {
    const source = fixture.input || {};
    const expected = fixture.expected || {};
    if ('stegcore_decision' in source) {
      const mapping = { allow: 'ALLOW', deny: 'DENY', defer: 'REVIEW' };
      const actual = mapping[source.stegcore_decision];
      if (actual !== expected.steggate_decision) throw new Error(`legacy mapping mismatch: ${fixture.fixture_id}`);
      if (source.stegcore_decision === 'defer' && expected.not === actual) throw new Error(`defer incorrectly mapped to forbidden outcome: ${fixture.fixture_id}`);
    } else if ('legacy_decision' in source) {
      const actual = source.legacy_decision === 'FAIL-CLOSED' ? 'FAIL_CLOSED' : source.legacy_decision;
      if (actual !== expected.steggate_decision) throw new Error(`legacy spelling mismatch: ${fixture.fixture_id}`);
    } else if ('admitted_candidate_hash' in source) {
      const same = source.admitted_candidate_hash === source.consequence_candidate_hash;
      const actual = same ? 'ALLOW' : 'DENY';
      if (actual !== expected.decision) throw new Error(`candidate binding mismatch: ${fixture.fixture_id}`);
      if (!same && expected.reason_code !== 'CANDIDATE_BINDING_MISMATCH') throw new Error(`candidate mismatch reason missing: ${fixture.fixture_id}`);
    } else throw new Error(`unsupported legacy fixture: ${fixture.fixture_id}`);
    checked += 1;
  }
  return { status: 'PASS', fixtures: checked };
}

export function runCases(casesPath = DEFAULT_CASES) {
  const cases = load(casesPath);
  if (cases.schema_version !== 'steggate.offline-verifier-cases.v1') throw new Error('verifier cases schema mismatch');
  const baseManifest = join(ROOT, cases.base_manifest);
  const results = [];
  for (const testCase of cases.decision_cases || []) {
    const { root, manifestPath } = prepareCase(baseManifest, testCase.decision, testCase.reason_code);
    try {
      const result = verifySemantics(manifestPath);
      results.push({ case_id: testCase.case_id, result: result.status, decision: result.decision });
    } finally { rmSync(root, { recursive: true, force: true }); }
  }
  for (const testCase of cases.tamper_cases || []) {
    const { root, manifestPath } = prepareCase(baseManifest, 'ALLOW', 'DECISION_REQUIRED');
    try {
      mutateCase(manifestPath, testCase.operation);
      try { verifySemantics(manifestPath); throw new Error(`tamper case accepted: ${testCase.case_id}`); }
      catch (error) {
        if (String(error.message).startsWith('tamper case accepted:')) throw error;
        results.push({ case_id: testCase.case_id, result: 'REJECT', reason: error.message });
      }
    } finally { rmSync(root, { recursive: true, force: true }); }
  }
  const legacy = verifyLegacyFixture(join(ROOT, cases.legacy_fixture));
  return {
    status: 'PASS', cases: results.length, decision_cases: (cases.decision_cases || []).length,
    tamper_cases: (cases.tamper_cases || []).length, legacy_fixtures: legacy.fixtures,
    results, authority_effect: false, implementation: 'node-independent-v1',
  };
}

function main(argv) {
  const manifestIndex = argv.indexOf('--manifest');
  if (manifestIndex >= 0) return verifySemantics(resolve(argv[manifestIndex + 1]));
  const casesIndex = argv.indexOf('--cases');
  return runCases(casesIndex >= 0 ? resolve(argv[casesIndex + 1]) : DEFAULT_CASES);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  try { process.stdout.write(`${JSON.stringify(main(process.argv.slice(2)))}\n`); }
  catch (error) { process.stderr.write(`verification failed: ${error.message}\n`); process.exitCode = 2; }
}
