# `stegverse.jcs.v1` canonicalization profile

Status: fixture-backed Audit Kit profile; not a standards-body claim.

This profile defines the canonical bytes used by the StegGate Audit Kit for candidate, derivation, receipt, and evidence-manifest hashing.

Normative requirements are enforced by `SG-CORE-009` and the golden vectors in `fixtures/canonicalization/vectors.json`.

## Domain

The input value MUST be JSON data consisting only of objects, arrays, strings, booleans, null, and integers in the inclusive interoperable range `[-9007199254740991, 9007199254740991]`.

Floating-point values are outside this v1 profile and MUST be rejected rather than rounded or reinterpreted.

Object member names MUST be strings. Strings MUST be valid Unicode scalar-value sequences; unpaired surrogates are rejected.

## Serialization

- emit UTF-8 without a BOM;
- emit no insignificant whitespace;
- serialize `null`, booleans, and integers in their JSON forms;
- preserve string code points exactly; **do not perform Unicode normalization**;
- escape strings using JSON escaping while leaving ordinary Unicode scalar values as UTF-8;
- order object member names lexicographically by their UTF-16 code-unit sequences, matching the ordering required by the declared JCS-compatible profile;
- recursively apply the same rules to nested values.

The profile deliberately keeps NFC and canonically equivalent decomposed strings distinct. If a producer wants normalized text, normalization occurs before the governed candidate is constructed and becomes part of that candidate's semantics; the canonicalizer never changes it.

## Identifier

The content identifier is:

```text
sha256:<lowercase-hex SHA-256 of canonical UTF-8 bytes>
```

A valid signature or hash proves integrity of the exact canonical bytes. It does not make assertions inside those bytes true.

## Fail-closed behavior

Unsupported numbers, invalid Unicode scalar strings, non-string object keys, or values outside the supported JSON domain cause canonicalization failure. A caller MUST NOT substitute a different serialization and continue under the same profile identifier.

## Conformance

The golden vectors cover ordinary ordering, nested values, exact string preservation, UTF-16 member ordering, safe integer bounds, and negative numeric/unicode cases. A conforming independent implementation must reproduce the positive canonical UTF-8 bytes and SHA-256 identifiers exactly and reject every negative vector.
