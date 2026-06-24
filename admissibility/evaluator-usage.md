# Evaluator Usage

`evaluator_stub.py` is a minimal demonstration evaluator.

It does not implement the full Standing Proof Engine. It only shows how a commitment candidate can be reduced to one of three outcomes:

```text
ALLOW | DENY | FAIL-CLOSED
```

## Run

From the repository root:

```bash
python3 admissibility/evaluator_stub.py admissibility/examples/sample-commitment-candidate.json
```

The expected result is an `ALLOW` result because the sample candidate is citation-only, includes explicit limitations, and includes non-claims.

## Stub behavior

The evaluator currently applies only three simple rules:

1. Missing required candidate fields return `FAIL-CLOSED`.
2. Execution, integration, or downstream reliance requests return `DENY`.
3. Citation-style requests with explicit limitations and non-claims return `ALLOW`.

## Boundary

This stub is intentionally conservative. It should not be used to certify artifacts, validate external research, approve execution, or imply upstream ARA compatibility.

Its purpose is to demonstrate the bridge:

```text
ARA-style artifact
        ↓
commitment candidate
        ↓
standing result
```
