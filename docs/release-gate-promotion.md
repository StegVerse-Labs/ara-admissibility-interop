# Evidence-Bounded Release Gate Promotion

`tools/promote_release_gates.py` converts a verified deployment evidence package into a bounded proposal for `release-manifest.json`.

The tool may promote only evidence-backed, non-authority fields:

- `pages_workflow_verified`
- `https_deployment_url_verified`
- `built_entrypoint_verified`
- `live_root_page_verified`
- `deployed_publication_receipt_verified`
- `deployed_evidence_bundle_verified`

It cannot set:

- `repo_check_workflow_verified`
- `stable_release_authorized`

It also cannot create a release tag.

## Default proposal mode

```bash
python3 tools/promote_release_gates.py
```

This writes:

```text
status/release-manifest.promoted.json
status/release-gate-promotion.json
```

The repository manifest is not changed.

## Explicit write mode

```bash
python3 tools/promote_release_gates.py --write-manifest
```

The manifest is written only when all of the following agree:

- the retained evidence bundle verifies;
- the public-review decision is `ALLOW`;
- evidence verification is `pass`;
- the live root and identity return HTTP 200;
- receipt, decision, bundle, and deployed identity name the same commit;
- publication status remains `public_review`;
- canonical status remains `not_authorized`;
- reliance posture remains `research_and_review_only`.

Any mismatch fails closed and produces no promoted gate changes.

## Tests

```bash
python3 tools/test_release_gate_promotion.py
```

The tests verify valid promotion, stale-deployment blocking, blocked public-review decisions, bundle tamper blocking, commit mismatch blocking, input immutability, and preservation of explicit authority-bearing fields.

## Boundary

Gate promotion records observed technical evidence. It does not establish Repo Check completion, canonical authority, independent review, clinical validity, regulatory authorization, execution authority, or stable-release authorization.
