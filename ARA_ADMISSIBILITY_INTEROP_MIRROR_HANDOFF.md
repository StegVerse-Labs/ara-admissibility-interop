# ARA Admissibility Interop Mirror Handoff

Repository: `StegVerse-Labs/ara-admissibility-interop`

## Source-of-truth rule

Read this file before continuing repository work. This handoff authorizes only bounded, repository-local validation and documentation repairs. It does not authorize releases, tags, deployments, external repository changes, policy changes, evaluator replacement, publication, or authority expansion.

## Current state

- Goal activation remains repository-local validation readiness only.
- Formal release and publication remain policy-gated.
- Latest observed commit: `c0315cc05628e2cf59e953449bd664b61c52868a` on `main`.
- Latest observed workflow: `Repo Check`, run `29178009373`.
- Job: `repo-check`.
- First failing step: `Generate validation report`.

## Failure classification

`tools/check_docs_site.py` requires the literal workflow phrase `path: docs`, while both Pages workflows use the governed dynamic publish root `${{ needs.publication-gate.outputs.publish_root }}` obtained from `publication-manifest.json`.

The remaining repository self-checks passed. The failure is a stale validator assertion, not evidence that the publication gate or dynamic publish-root boundary failed.

## Authorized bounded repair

The next permitted task is to align `tools/check_docs_site.py` with the governed dynamic publish-root workflow while preserving checks that:

- `actions/upload-pages-artifact@v3` remains present;
- the artifact path remains `${{ needs.publication-gate.outputs.publish_root }}`;
- the publication gate continues to derive the root from `publication-manifest.json`;
- canonical and iOS-safe workflow copies remain equivalent;
- no release, deployment, tag, external example, dependency-policy, or evaluator authority is changed.

## Verification requirement

Run or observe `Repo Check` on the repair commit. Completion requires `check_docs_site.py` and the complete generated-status check set to pass.

## Next task after verification

If and only if the full repository check passes, record the passing commit and run receipt here. Do not begin a formal release or publication task without a maintainer release decision.

## Remaining modules or work

- Policy-gated full JSON Schema dependency decision.
- Permission-gated external examples.
- Explicitly scoped evaluator replacement, if later authorized.
- Maintainer-controlled release checklist and release decision.

## Archive readiness

This handoff records the current failure, authority boundary, exact bounded repair, verification condition, and blocked later work. The complete thread is ready for archiving without any additional context needed to move forward.
