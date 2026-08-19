#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures/action-first/reconstruction-cases.json"
SCHEMA = ROOT / "schemas/action-first-reconstruction.v1.json"
REPORT = ROOT / "reports/action-first-reconstruction-validation.json"

REQUIRED_CASES = {
    "model-correct-observation-complete",
    "model-correct-observation-incomplete",
    "model-incomplete-observation-complete",
    "model-incomplete-observation-incomplete",
    "admissible-but-unrealized",
    "candidate-loses-admissibility-before-irreversibility",
    "unobserved-realized-transition",
    "later-observation-only-transition",
    "repeated-identifiable-latent-constraint",
    "non-identifiable-competing-latent-causes",
    "intentional-terminal-state",
}
REQUIRED_INVARIANTS = {
    "ALLOW != execution",
    "ALLOW != continuity",
    "unobserved != nonexistent",
    "FAIL_CLOSED applies to unsupported reliance, not reality itself",
    "prediction != causal reconstruction",
    "residual correlation != discovered constraint",
    "model(reality) != reality",
    "reconstruction success != execution authority",
}


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    fixtures = json.loads(FIXTURES.read_text())
    errors = []

    if schema.get("properties", {}).get("schema_version", {}).get("const") != "stegverse.action-first-reconstruction.v1":
        errors.append("schema-version")
    required = set(schema.get("required", []))
    for key in {"admissibility_matrix_ref", "irreversibility", "calculated_state", "realized_state", "observed_state", "model_reality_delta", "reality_observation_delta", "observation_profile", "constraint_partition", "reconstruction", "continuity_consequence", "viability"}:
        if key not in required:
            errors.append(f"missing-required:{key}")

    case_ids = {case.get("id") for case in fixtures.get("cases", [])}
    missing_cases = sorted(REQUIRED_CASES - case_ids)
    if missing_cases:
        errors.append("missing-cases:" + ",".join(missing_cases))

    invariants = set(fixtures.get("invariants", []))
    missing_invariants = sorted(REQUIRED_INVARIANTS - invariants)
    if missing_invariants:
        errors.append("missing-invariants:" + "|".join(missing_invariants))

    by_id = {case["id"]: case["expected"] for case in fixtures["cases"]}
    if by_id["unobserved-realized-transition"].get("dependent_reliance") != "FAIL_CLOSED":
        errors.append("unobserved-reliance-must-fail-closed")
    if by_id["later-observation-only-transition"].get("ontic_change") is not False:
        errors.append("observation-only-transition-must-preserve-ontic-state")
    if by_id["non-identifiable-competing-latent-causes"].get("constraint_promotion") != "NONE":
        errors.append("non-identifiable-cause-must-not-promote")
    if by_id["intentional-terminal-state"].get("continuity_failure") is not False:
        errors.append("declared-terminal-state-must-not-auto-fail-continuity")

    report = {
        "validator": "validate_action_first_reconstruction.py",
        "schema": str(SCHEMA.relative_to(ROOT)),
        "fixtures": str(FIXTURES.relative_to(ROOT)),
        "case_count": len(case_ids),
        "required_case_count": len(REQUIRED_CASES),
        "invariant_count": len(invariants),
        "required_invariant_count": len(REQUIRED_INVARIANTS),
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "authority_effect": False,
        "runtime_activation": False,
        "publication_activation": False
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
