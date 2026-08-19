#!/usr/bin/env node
/** Independent second-language conformance for governed-transition protocol fixtures.
 *
 * This implementation deliberately does not import or invoke the Python validator.
 * It independently evaluates the same public fixture semantics and emits its own
 * deterministic result surface. It has no runtime or execution authority.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const load = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));
const fixtures = load('fixtures/protocol/governed-transition-cases.json').fixtures;
const discoverySchema = load('schemas/gateway-discovery.v1.json');
const envelopeSchema = load('schemas/governed-transition-envelope.v1.json');
const authorityProfile = load('profiles/authority-rar-bound.v1.yaml');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function discoveryValid(value) {
  const required = [
    'gateway_id', 'protocol_versions', 'decision_states', 'canonicalization_profiles',
    'identity_profiles', 'authority_profiles', 'assurance_profiles', 'trust_anchor_refs', 'bindings'
  ];
  if (!required.every((key) => Object.hasOwn(value, key))) return false;
  const states = new Set(value.decision_states || []);
  return states.size === 4 && ['ALLOW', 'DENY', 'REVIEW', 'FAIL_CLOSED'].every((v) => states.has(v));
}

function monotonicGatePath(gates) {
  for (const gate of gates) {
    const upstream = new Set(gate.input_scope || []);
    const effective = new Set(gate.effective_scope || []);
    const subset = [...effective].every((item) => upstream.has(item));
    if (gate.broadened === true || !subset) return [false, 'AUTHORITY_BROADENING'];
  }
  return [true, null];
}

assert(discoverySchema.$schema === 'https://json-schema.org/draft/2020-12/schema', 'gateway discovery schema draft mismatch');
assert(envelopeSchema.$schema === 'https://json-schema.org/draft/2020-12/schema', 'envelope schema draft mismatch');
assert(authorityProfile.semantic_substrate === 'RFC 9396 authorization_details', 'RAR semantic substrate mismatch');
assert(authorityProfile.required_binding?.portable_authority_proof_required === true, 'portable authority proof must be required');
assert(authorityProfile.authority_effect === false, 'authority profile must remain authority_effect=false');

const results = [];
for (const fixture of fixtures) {
  const { fixture_id: fid, input, expected } = fixture;
  let actual;
  if (fid === 'protocol.allow.local_discovery') {
    actual = { valid: discoveryValid(input) };
  } else if (fid === 'protocol.allow.authority_narrows_across_gates' || fid === 'protocol.deny.authority_broadens_across_gates') {
    const [valid, reason] = monotonicGatePath(input.gate_path);
    actual = { valid, monotonic_authority: valid };
    if (!valid) Object.assign(actual, { decision: 'DENY', reason_code: reason });
  } else if (fid === 'protocol.fail_closed.unsupported_major_version') {
    const valid = new Set(input.supported || []).has(input.protocol_version);
    actual = { valid };
    if (!valid) actual.decision = 'FAIL_CLOSED';
  } else if (fid === 'protocol.fail_closed.rar_without_bound_authority_proof' || fid === 'protocol.allow.rar_with_bound_authority_proof') {
    const valid = Boolean(input.authorization_details_present && input.portable_authority_proof_present);
    actual = { valid };
    if (!valid) actual.decision = 'FAIL_CLOSED';
  } else {
    throw new Error(`unknown protocol fixture ${fid}`);
  }
  for (const [key, expectedValue] of Object.entries(expected)) {
    assert(actual[key] === expectedValue, `${fid}: ${key} mismatch ${JSON.stringify(actual[key])} != ${JSON.stringify(expectedValue)}`);
  }
  results.push({ fixture_id: fid, result: 'PASS', ...actual });
}

console.log(JSON.stringify({
  status: 'PASS',
  profile: 'steggate.governed-transition-protocol.v1',
  implementation: 'node-independent-v1',
  shared_implementation_code: false,
  fixtures: results.length,
  monotonic_authority_enforced: true,
  rar_requires_bound_authority_proof: true,
  unsupported_major_fails_closed: true,
  discovery_profile_validated: true,
  runtime_authority_effect: false,
  results,
}));
