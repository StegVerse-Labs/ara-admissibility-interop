# Governed Release Evidence Decision

`tools/evaluate_release_evidence.py` converts a publication receipt and the repository release manifest into two separate decisions:

- **Public-review decision** — whether the supplied evidence supports the declared `public_review` deployment.
- **Stable-release decision** — whether every explicit release gate, including separate authorization, is satisfied.

The evaluator does not modify `release-manifest.json`, create a tag, grant canonical status, or authorize a stable release.

## Inputs

Minimum evaluation:

- `status/publication-receipt.json`
- `release-manifest.json`

Full deployed-evidence evaluation additionally checks:

- `_site/` — the built artifact retained from the Pages run
- `status/deployed-identity.json` — the captured live deployment identity
- `status/deployed-live-root.html` — the captured rendered live root

The full form recalculates the built-site inventory and artifact-tree hash, verifies the deployment identity hash and commit, and verifies the captured live-root body hash before producing the decision.

## Outputs

- `status/release-evidence-decision.json`
- `status/release-evidence-decision.md`

The JSON output includes an `evidence_scope` object so reviewers can see whether the decision checked only the receipt or also checked the retained built artifact and captured live evidence.

## Commands

Run evaluator tests:

```bash
python3 tools/test_release_evidence_evaluator.py
```

Evaluate the default receipt and manifest:

```bash
python3 tools/evaluate_release_evidence.py
```

Evaluate the complete retained deployment package and fail unless public review is supported:

```bash
python3 tools/evaluate_release_evidence.py \
  --artifact-root _site \
  --identity-file status/deployed-identity.json \
  --live-root-file status/deployed-live-root.html \
  --require-public-review-allow
```

The Docs Pages workflow runs this complete command after live commit-bound verification and receipt generation. Its `deployed-publication-evidence` artifact retains the built site, captured live files, receipt, publication status, and both decision outputs.

## Stable-release boundary

A verified public-review deployment does not automatically satisfy stable-release gates. Stable release remains blocked until all release-gate booleans are supported by observed evidence and `stable_release_authorized` is explicitly true.

An `ALLOW` public-review decision establishes only that the evaluated evidence package is internally consistent with the declared research-and-review publication posture. It does not establish upstream endorsement, independent review, canonical doctrine status, clinical validity, regulatory authorization, or execution authority.
