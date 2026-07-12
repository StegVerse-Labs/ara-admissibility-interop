# Independent Publication Evidence Verification

The `deployed-publication-evidence` artifact is intended to be independently inspectable after the workflow that produced it has completed.

## Receipt verifier

Use the dependency-free verifier from the repository root:

```bash
python3 tools/verify_publication_evidence.py \
  status/publication-receipt.json
```

This validates the receipt structure, gate result, hashes, file inventory metadata, live HTTP evidence, and deployed-commit identity.

When the built site and fetched live evidence files are available, perform full verification:

```bash
python3 tools/verify_publication_evidence.py \
  status/publication-receipt.json \
  --artifact-root _site \
  --identity-file status/deployed-identity.json \
  --live-root-file status/deployed-live-root.html
```

## Evidence-bundle manifest

A successful Pages run also creates:

```text
status/deployed-evidence-bundle.json
```

This manifest binds the publication status, receipt, release decision, captured live root, captured deployment identity, and human-readable status into one deterministic bundle hash.

Verify the complete retained package with:

```bash
python3 tools/verify_evidence_bundle_manifest.py \
  status/deployed-evidence-bundle.json \
  --root .
```

The verifier recalculates every declared file hash and size, rejects duplicate or escaping paths, and reproduces the bundle SHA-256.

## What full verification proves

- The retained built-site inventory matches the receipt.
- The deterministic artifact-tree SHA-256 can be reproduced.
- The deployment identity file hashes to the recorded value.
- The identity commit equals the receipt commit.
- The live root response hashes to the recorded HTTP body hash.
- The live deployment claimed as current is not merely a stale prior Pages deployment.
- The retained evidence files form the exact bundle identified by `bundle_sha256`.

## What verification does not prove

Passing receipt or bundle verification does not establish:

- canonical doctrine authorization;
- upstream ARA endorsement;
- independent scientific or field review;
- clinical validity or utility;
- regulatory authorization;
- legal authority, consent, or person-specific admissibility;
- execution authority for any external system.

The verifiers prove consistency and integrity of the declared publication evidence. They do not manufacture standing that the evidence and governance state do not otherwise possess.
