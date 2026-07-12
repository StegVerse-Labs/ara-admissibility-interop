# Release Checklist

Use this checklist before tagging, citing, or presenting the repository as a release candidate.

## Candidate identity

- [ ] `VERSION` is `0.2.0-release-candidate`.
- [ ] `CHANGELOG.md` has a `0.2.0-release-candidate` entry.
- [ ] `release-manifest.json` names the same candidate.
- [ ] `docs/release-readiness.md` names the same candidate.
- [ ] `docs/release-note-0.2.0-rc.md` exists.

## Boundary

- [ ] `admissibility/non-claims.md` is present.
- [ ] README states that this repository does not replace ARA.
- [ ] `publication-manifest.json` declares `public_review` unless canonical release is separately authorized.
- [ ] Release notes avoid endorsement, certification, canonical, clinical, regulatory, or execution-authority overclaims.

## Dependency policy

- [ ] Baseline validation remains dependency-free.
- [ ] No required dependencies are declared for the default validation path.
- [ ] Missing optional dependencies return a clean skip with exit code `0`.
- [ ] Validation does not install packages or require network access.

## Local validation

Run:

```bash
python3 tools/generate_validation_report.py
python3 tools/check_publication_gate.py
python3 tools/test_publication_gate.py
python3 tools/check_workflow_parity.py
python3 tools/generate_publication_status.py
python3 tools/generate_publication_receipt.py
```

Confirm:

- [ ] `status/generated-status.json` exists.
- [ ] `status/validation-report.md` exists.
- [ ] Generated state is `self-check-pass`.
- [ ] Publication gate is `ALLOW`.
- [ ] Negative gate tests pass.
- [ ] Workflow parity passes.
- [ ] `status/publication-status.json` exists.
- [ ] `docs/publication-status.md` exists.
- [ ] `status/publication-receipt.json` exists.
- [ ] Receipt manifest hash and file inventory are populated.

## Publication fixtures

- [ ] Canonical publication without review fails closed.
- [ ] Canonical publication without authorization fails closed.
- [ ] Escaping publish root fails closed.
- [ ] Missing publish root fails closed.
- [ ] Publish root without an index fails closed.
- [ ] Unsupported target fails closed.
- [ ] Missing required fields fail closed.
- [ ] Empty non-claims fail closed.
- [ ] Invalid gate policy fails closed.
- [ ] Clinical reliance without authorization fails closed.
- [ ] Fully reviewed and authorized canonical state passes the gate test without changing the repository's current posture.

## Workflow parity

- [ ] `.github/workflows/repo-check.yml` matches `iosnoperiod/github/workflows/repo-check.yml`.
- [ ] `.github/workflows/docs-pages.yml` matches `iosnoperiod/github/workflows/docs-pages.yml`.
- [ ] `tools/check_workflow_parity.py` enforces both comparisons.

## Live GitHub Actions verification

- [ ] `Repo Check` succeeds on the candidate commit.
- [ ] Validation report artifact is retained.
- [ ] Publication status artifact is retained.
- [ ] Publication receipt artifact is retained.
- [ ] `Docs Pages` publication-gate job succeeds.
- [ ] `Docs Pages` publish-docs job succeeds.
- [ ] Deployment URL is HTTPS.
- [ ] `deployed-publication-evidence` artifact is retained.
- [ ] Deployed receipt commit matches the deployed commit.
- [ ] Deployed receipt URL matches the Pages deployment output.

## Stable release gate

- [ ] All required local checks pass.
- [ ] All live GitHub Actions checks pass.
- [ ] Deployed publication evidence is inspected.
- [ ] `release-manifest.json` release-gate booleans are updated from evidence.
- [ ] Stable release authorization is explicitly recorded.
- [ ] Only then create a stable release tag.

## Public positioning

Recommended framing:

> This repository is an independent interoperability prototype with manifest-governed public-review publication and hash-bound deployment evidence.

Avoid claiming:

- ARA author endorsement;
- certification of external artifacts;
- production Standing Proof Engine behavior;
- canonical doctrine;
- independent review, clinical validation, or regulatory authorization;
- execution authority;
- required full JSON Schema conformance when the optional dependency is absent.

## Release outcome

When local and live checks pass, the repository may be treated as `0.2.0-release-candidate` for public review and citation. Stable release remains separately gated.
