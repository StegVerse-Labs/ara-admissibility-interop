#!/usr/bin/env node
/** Cross-language parity harness. It compares independent Python and Node implementations without sharing implementation code. */
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { canonicalize } from './canonicalize_steggate_node.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const VECTORS = join(ROOT, 'fixtures', 'canonicalization', 'vectors.json');

function run(command, args) {
  return spawnSync(command, args, { cwd: ROOT, encoding: 'utf8' });
}

function normalizedVerifier(result) {
  return {
    status: result.status,
    cases: result.cases,
    decision_cases: result.decision_cases,
    tamper_cases: result.tamper_cases,
    legacy_fixtures: result.legacy_fixtures,
    authority_effect: result.authority_effect,
    results: result.results.map((item) => ({ case_id: item.case_id, result: item.result, decision: item.decision || null })),
  };
}

const vectors = JSON.parse(readFileSync(VECTORS, 'utf8'));
let positive = 0;
let negative = 0;
const temp = mkdtempSync(join(tmpdir(), 'steggate-track1b-'));
try {
  for (const vector of vectors.fixtures) {
    const path = join(temp, `${vector.fixture_id.replaceAll('/', '_')}.json`);
    writeFileSync(path, JSON.stringify(vector.input), 'utf8');
    const py = run('python', ['tools/canonicalize_steggate.py', path]);
    const js = run('node', ['tools/canonicalize_steggate_node.mjs', path]);
    if (vector.kind === 'positive') {
      positive += 1;
      if (py.status !== 0 || js.status !== 0) throw new Error(`${vector.fixture_id}: canonicalizer unexpectedly rejected positive vector`);
      const pyBytes = py.stdout.replace(/\n$/, '');
      const jsBytes = js.stdout.replace(/\n$/, '');
      if (pyBytes !== jsBytes || jsBytes !== vector.expected_canonical_utf8) throw new Error(`${vector.fixture_id}: canonical byte disagreement`);
      const pyHash = run('python', ['tools/canonicalize_steggate.py', path, '--hash-only']);
      const jsHash = run('node', ['tools/canonicalize_steggate_node.mjs', path, '--hash-only']);
      const independentHash = `sha256:${createHash('sha256').update(canonicalize(vector.input)).digest('hex')}`;
      if (pyHash.status !== 0 || jsHash.status !== 0 || pyHash.stdout.trim() !== jsHash.stdout.trim() || jsHash.stdout.trim() !== vector.expected_sha256 || independentHash !== vector.expected_sha256) {
        throw new Error(`${vector.fixture_id}: canonical hash disagreement`);
      }
    } else if (vector.kind === 'negative') {
      negative += 1;
      if (py.status === 0 || js.status === 0) throw new Error(`${vector.fixture_id}: negative vector acceptance disagreement`);
    } else throw new Error(`${vector.fixture_id}: unsupported vector kind`);
  }

  const pyVerifier = run('python', ['tools/verify_audit_kit.py']);
  const jsVerifier = run('node', ['tools/verify_audit_kit_node.mjs']);
  if (pyVerifier.status !== 0) throw new Error(`Python verifier failed: ${pyVerifier.stderr.trim()}`);
  if (jsVerifier.status !== 0) throw new Error(`Node verifier failed: ${jsVerifier.stderr.trim()}`);
  const pyResult = normalizedVerifier(JSON.parse(pyVerifier.stdout));
  const jsResult = normalizedVerifier(JSON.parse(jsVerifier.stdout));
  if (JSON.stringify(pyResult) !== JSON.stringify(jsResult)) throw new Error('offline verifier decision/rejection result disagreement');

  process.stdout.write(`${JSON.stringify({
    status: 'PASS',
    canonical_positive_agreement: positive,
    canonical_negative_agreement: negative,
    verifier_case_agreement: jsResult.cases,
    decision_case_agreement: jsResult.decision_cases,
    tamper_case_agreement: jsResult.tamper_cases,
    legacy_fixture_agreement: jsResult.legacy_fixtures,
    identical_hashes: true,
    shared_implementation_code: false,
    second_language: 'JavaScript/Node.js',
    authority_effect: false,
  })}\n`);
} finally {
  rmSync(temp, { recursive: true, force: true });
}
