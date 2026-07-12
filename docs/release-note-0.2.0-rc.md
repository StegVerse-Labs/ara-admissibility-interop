# Release note — 0.2.0 release candidate

`0.2.0-release-candidate` adds governed automated publication to the ARA Admissibility Interop prototype.

## Added

- Explicit `publication-manifest.json` publication posture.
- Fail-closed publication gate for GitHub Pages.
- Negative publication fixtures and executable gate tests.
- Hash-bound publication receipts with file inventory and deployment identity.
- Machine-readable and human-readable publication status generation.
- Deployment URL verification.
- Canonical/iOS-safe workflow parity enforcement.
- Retained workflow artifacts for validation, publication status, and publication receipts.

## Current publication posture

- publication: `public_review`
- canonical: `not_authorized`
- independent review: `not_started`
- clinical validation: `not_validated`
- regulatory authorization: `not_authorized`
- reliance: `research_and_review_only`

## Boundary

Passing the publication gate authorizes deployment only under the declared posture. It does not establish upstream ARA endorsement, certification of external artifacts, canonical doctrine, clinical validity, regulatory authorization, or execution authority.

## Release gate

The candidate should not be tagged as a stable release until the repository-check and Pages workflows complete successfully and a deployed publication receipt records a verified HTTPS Pages URL.
