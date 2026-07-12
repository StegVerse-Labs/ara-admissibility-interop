# Independent Publication Evidence Verification

The `deployed-publication-evidence` artifact is intended to be independently inspectable after the workflow that produced it has completed.

## Verifier

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
  --identity-file _site/deployment-identity.json \
  --live-root-file evidence/live-root.html
```

## What full verification proves

- The retained built-site inventory matches the receipt.
- The deterministic artifact-tree SHA-256 can be reproduced.
- The deployment identity file hashes to the recorded value.
- The identity commit equals the receipt commit.
- The live root response hashes to the recorded HTTP body hash.
- The live deployment claimed as current is not merely a stale prior Pages deployment.

## What verification does not prove

Passing receipt verification does not establish:

- canonical doctrine authorization;
- upstream ARA endorsement;
- independent scientific or field review;
- clinical validity or utility;
- regulatory authorization;
- legal authority, consent, or person-specific admissibility;
- execution authority for any external system.

The verifier proves consistency and integrity of the declared publication evidence. It does not manufacture standing that the evidence and governance state do not otherwise possess.
