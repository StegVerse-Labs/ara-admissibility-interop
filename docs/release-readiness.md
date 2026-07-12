# Release Readiness

## Candidate

Version: `0.2.0-release-candidate`

Release manifest: [`../release-manifest.json`](../release-manifest.json)

Release checklist: [`release-checklist.md`](release-checklist.md)

Release note: [`release-note-0.2.0-rc.md`](release-note-0.2.0-rc.md)

Publication status: [`publication-status.md`](publication-status.md)

## Purpose

This release candidate adds manifest-governed, fail-closed automated publication to the ARA admissibility interoperability prototype. It is intended to be inspectable without chat history and to preserve publication posture, non-claims, workflow identity, file hashes, and deployment evidence.

## Release candidate criteria

| Criterion | Status |
| --- | --- |
| Boundary and non-claims are explicit | Ready |
| ARA-style artifact concepts are mapped to standing concepts | Ready |
| Commitment-candidate and standing-result schemas exist | Ready |
| ALLOW, DENY, and FAIL-CLOSED examples exist | Ready |
| Dependency-free validation path exists | Ready |
| Publication manifest declares current posture | Ready |
| Fail-closed publication gate exists | Ready |
| Negative publication tests exist | Ready |
| Publication receipt schema and generator exist | Ready |
| Publication status generator exists | Ready |
| Canonical/iOS-safe workflow parity is enforced | Ready |
| Pages deployment is gated by publication state | Ready |
| Validation and publication artifacts are retained | Ready |
| Repository-check workflow has completed successfully for the candidate | Pending live verification |
| Pages workflow has completed successfully for the candidate | Pending live verification |
| Verified HTTPS deployment URL is present in a deployed receipt | Pending live verification |
| Stable release tag is authorized | No |

## Required local checks

Run:

```bash
python3 tools/generate_validation_report.py
python3 tools/check_publication_gate.py
python3 tools/test_publication_gate.py
python3 tools/check_workflow_parity.py
python3 tools/generate_publication_status.py
python3 tools/generate_publication_receipt.py
```

Expected generated files:

```text
status/generated-status.json
status/validation-report.md
status/publication-status.json
status/publication-receipt.json
docs/publication-status.md
```

Expected states:

```text
self-check-pass
PUBLICATION_GATE=ALLOW
publication gate tests: PASS
workflow parity: PASS
PUBLICATION_STATUS=ALLOW
PUBLICATION_RECEIPT=CREATED
```

## Live release verification

The candidate remains untagged until GitHub Actions provides evidence that:

1. `Repo Check` succeeds on the candidate commit.
2. `Docs Pages` succeeds on the candidate commit.
3. The deployment output contains an HTTPS Pages URL.
4. `deployed-publication-evidence` contains a receipt bound to that commit and URL.

## Non-release claims

This release candidate does not claim:

- upstream ARA endorsement;
- certification of external artifacts;
- journal, conference, lab, or platform acceptance;
- production Standing Proof Engine behavior;
- canonical doctrine status;
- independent review, clinical validation, or regulatory authorization;
- execution authority for any external system;
- required full JSON Schema conformance when the optional dependency is absent.

## Suggested release statement

`0.2.0-release-candidate` establishes a dependency-free interoperability prototype with manifest-governed GitHub Pages publication, fail-closed boundary tests, workflow parity checks, and hash-bound publication receipts. Stable release remains blocked pending live workflow and deployment verification.
