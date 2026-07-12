# Governed Release Evidence Decision

`tools/evaluate_release_evidence.py` converts a publication receipt and the repository release manifest into two separate decisions:

- **Public-review decision** — whether the supplied evidence supports the declared `public_review` deployment.
- **Stable-release decision** — whether every explicit release gate, including separate authorization, is satisfied.

The evaluator does not modify `release-manifest.json`, create a tag, grant canonical status, or authorize a stable release.

## Inputs

- `status/publication-receipt.json`
- `release-manifest.json`

## Outputs

- `status/release-evidence-decision.json`
- `status/release-evidence-decision.md`

## Commands

```bash
python3 tools/test_release_evidence_evaluator.py
python3 tools/evaluate_release_evidence.py
```

To make a workflow fail unless the supplied evidence permits public-review publication:

```bash
python3 tools/evaluate_release_evidence.py --require-public-review-allow
```

A verified public-review deployment does not automatically satisfy stable-release gates. Stable release remains blocked until all release-gate booleans are supported by observed evidence and `stable_release_authorized` is explicitly true.

## Boundary

An `ALLOW` public-review decision establishes only that the evaluated receipt is structurally consistent with the declared research-and-review publication posture. It does not establish upstream endorsement, independent review, canonical doctrine status, clinical validity, regulatory authorization, or execution authority.
