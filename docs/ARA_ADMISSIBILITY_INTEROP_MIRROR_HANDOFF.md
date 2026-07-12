# ARA Admissibility Interop Mirror Handoff

## Current goal

Complete live verification of the `0.2.0-release-candidate` governed public-review publication path.

## Completed

- Confirmed canonical Pages workflow at `.github/workflows/docs-pages.yml`.
- Confirmed iOS-safe mirror at `iosnoperiod/github/workflows/docs-pages.yml`.
- Added `publication-manifest.json` with explicit publication, canonical, independent-review, clinical, regulatory, and reliance states.
- Added dependency-free fail-closed gate at `tools/check_publication_gate.py`.
- Added executable positive and negative gate tests at `tools/test_publication_gate.py`.
- Added inspectable negative fixtures under `publication/fixtures/`.
- Pages deployment requires the publication gate to return `ALLOW`.
- Publish root is read from the manifest instead of being hard-coded.
- Added workflow parity enforcement for canonical and iOS-safe workflows.
- Added `tools/generate_publication_status.py` producing machine-readable and public status outputs.
- Added `tools/generate_publication_receipt.py` with manifest and published-file SHA-256 hashes.
- Added `publication/publication-receipt.schema.json`.
- Added retained artifacts for validation, publication status, receipts, and deployed publication evidence.
- Updated `VERSION`, `CHANGELOG.md`, release manifest, release note, release readiness, and release checklist for `0.2.0-release-candidate`.
- Observed a successful GitHub Pages deployment environment at `https://stegverse-labs.github.io/ara-admissibility-interop/`.
- Diagnosed the prior live root `404`: the workflow uploaded raw Markdown from `docs/`, so the deployed artifact lacked `index.html`.
- Replaced raw docs upload with `actions/jekyll-build-pages@v1` and `_site` deployment.
- Added a fail-closed check requiring `_site/index.html` and the expected site marker before artifact upload.
- Added post-deployment live-root verification with bounded retries, HTTPS enforcement, HTTP 200 enforcement, and expected rendered-content verification.
- Changed deployed receipts to hash the built `_site` artifact rather than only the Markdown source tree.
- Added a deterministic artifact-tree SHA-256 covering deployed paths, file hashes, and sizes.
- Extended the receipt schema to `1.3.0` with artifact identity, structured live HTTP evidence, and exact deployed-commit verification.
- Added `tools/stamp_built_site.py` to write `_site/deployment-identity.json` and inject the current commit into `_site/index.html`.
- The live verifier requires both the rendered root and `deployment-identity.json` to identify the current `GITHUB_SHA`.
- The deployed receipt records verification timestamp, effective URLs, HTTP statuses, marker result, body hashes, response size, and deployed commit identity.
- Added `tools/verify_publication_evidence.py` for dependency-free verification of retained receipts, built-site inventories, artifact-tree hashes, deployment identity, and captured live-root hashes.
- Added `tools/test_publication_evidence_verifier.py` with valid, stale-commit, altered-tree, and tampered-file test cases.
- Added `docs/publication-evidence-verification.md` and linked it from the documentation index.
- Added `tools/evaluate_release_evidence.py` to convert verified evidence into separate public-review and stable-release decisions.
- Added `tools/test_release_evidence_evaluator.py` covering valid public review, stale deployment, invalid reliance posture, and fully explicit stable gates.
- Added `docs/release-evidence-decision.md` and linked it from the documentation index.
- Repo Check tests both independent evidence verification and bounded release-evidence decisions.
- The release-evidence evaluator now accepts the retained `_site`, captured deployment identity, and captured live root so its decision is bound to the complete evidence package.
- Docs Pages now runs the evaluator with `--require-public-review-allow` after live verification and receipt generation.
- The deployed evidence artifact now retains `_site`, captured live root, captured deployment identity, publication receipt, publication status, and JSON/Markdown release decisions.
- Updated `release-manifest.json` to declare the verifier, evaluator, evidence scope, retained outputs, fail-closed public-review posture, and prohibition on automatic stable authorization.
- Resynchronized canonical and iOS-safe Repo Check and Pages workflows.
- Updated `tools/check_docs_site.py` to enforce the complete deployment, evidence, and decision invariants.

## Current publication posture

- publication status: `public_review`
- canonical status: `not_authorized`
- independent review: `not_started`
- clinical status: `not_validated`
- regulatory status: `not_authorized`
- reliance posture: `research_and_review_only`

## Current release gate

- local architecture and checks: built
- canonical/iOS workflow parity: built
- independent evidence verifier and tests: built
- release-evidence evaluator and tests: built
- deployed Pages decision integration: built
- complete retained evidence package: configured
- HTTPS Pages deployment environment and URL: observed
- prior deployed root page: failed with `404` because no rendered `index.html` was present
- Jekyll build correction: installed
- built-site entry-point and marker checks: installed
- current-commit deployment identity: installed
- live deployed-root HTTP, content, and commit verification: installed
- built-artifact hash receipt: installed
- structured live HTTP and identity evidence receipt: installed
- independent retained-evidence verification: installed
- machine-readable public-review versus stable-release decision: installed
- fresh Repo Check and Pages runs: triggered by this handoff update
- corrected Pages workflow live success: pending observed run evidence
- rendered current-commit root page: pending observed evidence
- deployed publication evidence artifact inspection: pending
- stable release tag: blocked

## Boundary

A successful Pages deployment means only that the documentation was permitted under the declared publication posture. It does not establish upstream ARA endorsement, external certification, independent review, clinical validity, regulatory authorization, canonical doctrine status, or execution authority.

A passing independent evidence verification proves internal consistency and integrity of the retained publication evidence. It does not create scientific truth, authority, consent, legality, clinical meaning, or canonical status.

An `ALLOW` public-review decision does not authorize a stable release. Stable release remains separately blocked until every release-gate condition is supported by observed evidence and `stable_release_authorized` is explicitly true.

## Next tasks

1. Confirm `Repo Check` passes with the updated validator, independent verifier, and release-evidence evaluator tests.
2. Confirm `Docs Pages` builds and stamps `_site`, verifies the exact current commit at the live URL, generates the receipt, evaluates the full retained evidence package, and returns public-review `ALLOW`.
3. Open the root Pages URL and confirm a rendered current-commit documentation page replaces the prior `404`.
4. Inspect the `deployed-publication-evidence` artifact and confirm all declared files are present.
5. Run `tools/verify_publication_evidence.py` and `tools/evaluate_release_evidence.py` against the retained deployment evidence.
6. Update `release-manifest.json` release-gate booleans only from observed evidence.
7. Create a stable tag only after explicit release authorization.
8. Add optional downstream Site mirroring only after inspecting `StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md`.

No prior chat context is required to continue from this handoff.
