# Release Readiness

## Candidate

Version: `0.2.0-release-candidate`

Release manifest: [`../release-manifest.json`](../release-manifest.json)

Release checklist: [`release-checklist.md`](release-checklist.md)

Release note: [`release-note-0.2.0-rc.md`](release-note-0.2.0-rc.md)

Publication status: [`publication-status.md`](publication-status.md)

Canonical activation handoff: [`ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md`](ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md)

Release owner: issue `#121`.

## Purpose

This release candidate provides a manifest-governed, fail-closed ARA admissibility interoperability prototype with deterministic validation, governed GitHub Pages publication, retained deployment evidence, and explicit separation between evidence gates and stable-release authority.

## Current evidence state

The source/integration implementation is merged and validated. Runtime execution responsibility has transferred to `StegVerse-Labs/StegCore`; continuity preservation/reconstruction responsibility is satisfied in `StegVerse-Labs/Continuity`.

Hosted Docs Pages run `32593976088` on commit `9ed565df9eff2d03772b766b7fd53c398efbb0e1` proved the following deployment sub-gates before a later notification-generation failure caused the overall workflow to conclude failure:

- Pages deployment succeeded.
- The live Pages root returned HTTP 200 and contained the expected ARA documentation marker and exact commit identity.
- The deployed identity endpoint returned HTTP 200 and matched the deployed commit.
- An HTTPS Pages URL was produced: `https://stegverse-labs.github.io/ara-admissibility-interop/`.
- A deployment-bound publication receipt was created.
- `RELEASE_EVIDENCE_DECISION=ALLOW` was produced.
- The deployed evidence bundle verified with zero problems and bundle SHA-256 `76b43b4fbd0c9dfb9caac86d1cf7d5d78c624c5f3219b115f50bc1907e06d80d`.

That run is **not** counted as a successful Docs Pages workflow because `Generate handoff-backed deployment notification` failed after those evidence steps. PRs #123 and #124 repaired the canonical handoff contract and added regression coverage against the real handoff. PR #126 changed the existing Docs Pages workflow so `deployed-publication-evidence` is retained immediately after evidence-bundle verification, before notification transport can fail.

## Workflow governance

The repository workflow ceiling is enforced by `management/workflow-governance.json` and `tools/check_workflow_governance.py`.

The baseline is two activation-authoritative workflows:

- `.github/workflows/repo-check.yml`
- `.github/workflows/steggate-schema-foundation.yml`

Three service workflows exist only under explicit non-authority exceptions:

- `ARA-WF-EX-001` — `.github/workflows/docs-pages.yml`
- `ARA-WF-EX-002` — `.github/workflows/deployment-notification.yml`
- `ARA-WF-EX-003` — `.github/workflows/deployment-mailbox-monitor.yml`

Repo Check fails closed on undeclared workflow additions, missing exceptions, or exception authority creep.

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
| Workflow ceiling and discrete exceptions are enforced | Ready |
| Pages deployment is gated by publication state | Ready |
| HTTPS Pages deployment has been observed and live-verified | Proven on run `32593976088` |
| Deployment-bound publication receipt generation works | Proven on run `32593976088` |
| Release-evidence evaluator/verifier accepts retained deployment evidence | Proven on run `32593976088` |
| Evidence-bundle verification succeeds | Proven on run `32593976088` |
| Repository-check workflow succeeds on the release candidate state | Requires exact final candidate evidence reconciliation in issue `#121` |
| Overall Docs Pages workflow succeeds on the repaired release candidate state | Pending repaired main-branch run consumption |
| `deployed-publication-evidence` is retained for that successful repaired run | Pending repaired main-branch run consumption |
| Stable release authorization is explicit | No |
| Stable tag/formal release exists | No |

## Required local checks

Run:

```bash
python3 tools/generate_validation_report.py
python3 tools/check_publication_gate.py
python3 tools/test_publication_gate.py
python3 tools/check_workflow_parity.py
python3 tools/check_workflow_governance.py
python3 tools/generate_publication_status.py
python3 tools/generate_publication_receipt.py
```

Expected states include:

```text
self-check-pass
PUBLICATION_GATE=ALLOW
publication gate tests: PASS
workflow parity: PASS
workflow governance: PASS
PUBLICATION_STATUS=ALLOW
PUBLICATION_RECEIPT=CREATED
```

## Live release verification

Issue `#121` owns the remaining release activation gate. Stable release remains blocked until the same final candidate state has machine-visible evidence that:

1. `Repo Check` succeeds.
2. the repaired `Docs Pages` workflow succeeds end-to-end;
3. the deployment output contains an HTTPS Pages URL;
4. retained `deployed-publication-evidence` contains a receipt bound to that candidate commit and URL;
5. release-evidence and evidence-bundle verification pass; and
6. `stable_release_authorized` is explicitly authorized through the protected release boundary.

The existing evidence-bounded promotion mechanism may promote only its declared non-authority fields. It may not set `repo_check_workflow_verified`, `stable_release_authorized`, or create a tag.

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

## Current release statement

`0.2.0-release-candidate` is source/integration complete and has proven HTTPS deployment, deployment-bound receipt generation, release-evidence ALLOW evaluation, and evidence-bundle verification. Stable release remains blocked only on exact final-candidate hosted workflow/evidence reconciliation and explicit stable-release authorization; no stable tag or formal release is currently claimed.
