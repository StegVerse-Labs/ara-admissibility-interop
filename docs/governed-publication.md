# Governed publication

The documentation site is published by GitHub Pages only after the repository's publication manifest passes a fail-closed gate.

## Publication flow

```text
repository change
    ↓
publication-manifest.json
    ↓
tools/check_publication_gate.py
    ↓
ALLOW | FAIL-CLOSED
    ↓
GitHub Pages artifact
    ↓
Pages deployment
```

## Current posture

The current manifest declares:

- publication status: `public_review`
- canonical status: `not_authorized`
- independent review: `not_started`
- clinical status: `not_validated`
- regulatory status: `not_authorized`
- reliance posture: `research_and_review_only`

This permits publication for public inspection without presenting the material as canonical doctrine, clinical validation, regulatory authorization, or execution authority.

## Gate behavior

The gate blocks publication when:

- the manifest is missing or malformed;
- a required field is absent;
- the publication status is not allowed;
- the publish root is missing or escapes the repository;
- the publish root has no site entry point;
- canonical publication is requested without canonical authorization and completed independent review;
- the declared target is not supported by the workflow.

Run the gate locally with:

```bash
python3 tools/check_publication_gate.py
```

Expected output for the present repository state:

```text
PUBLICATION_GATE=ALLOW
publication_status=public_review
canonical_status=not_authorized
reliance_posture=research_and_review_only
publish_root=docs
```

## Boundary

Passing the publication gate means the artifact may be deployed under its declared publication posture. It does not certify external artifacts, establish truth, grant execution authority, or authorize stronger reliance than the manifest declares.
