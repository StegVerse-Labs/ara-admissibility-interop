#!/usr/bin/env python3
"""Validate StegGate decision-state reconstruction semantics using stdlib only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "decision-state.v1.json"
FIXTURES = ROOT / "fixtures" / "decision-state" / "reconstruction-cases.json"


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    schema = load(SCHEMA)
    data = load(FIXTURES)
    require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "schema draft mismatch")
    require(schema.get("$id"), "schema id missing")
    required = set(schema.get("required", []))
    for field in (
        "candidate_hash", "evidence_refs", "authority_refs", "policy_refs",
        "predicate_results", "disposition", "commit_state", "observation_state",
        "reconciliation_state",
    ):
        require(field in required, f"schema missing required field {field}")

    cases = data.get("fixtures", [])
    require(len(cases) == 5, "decision-state fixture count must be 5")
    ids = set()
    decisions = set()
    for case in cases:
        fid = case.get("fixture_id")
        require(fid and fid not in ids, f"invalid or duplicate fixture id {fid}")
        ids.add(fid)
        for field in required:
            require(field in case, f"{fid} missing {field}")
        require(case.get("evidence_refs"), f"{fid} missing evidence refs")
        require(case.get("authority_refs"), f"{fid} missing authority refs")
        require(case.get("policy_refs"), f"{fid} missing policy refs")
        require(case.get("predicate_results"), f"{fid} missing predicate results")
        decisions.add(case["disposition"])

        if case["disposition"] in {"DENY", "REVIEW", "FAIL_CLOSED"}:
            require(case.get("executor_invoked") is False, f"{fid} non-ALLOW executor invocation")
            require(case.get("commit_state") in {"NOT_ATTEMPTED", "NOT_COMMITTED"}, f"{fid} non-ALLOW commit state invalid")
        if case["disposition"] == "REVIEW":
            require(case.get("successor_transition_id"), f"{fid} REVIEW successor missing")
            require(case["successor_transition_id"] != case["transition_id"], f"{fid} REVIEW overwrote original transition")
        if case["disposition"] == "FAIL_CLOSED":
            require(case.get("unresolved_conditions"), f"{fid} FAIL_CLOSED lacks unresolved condition")
        if case.get("reconciliation_state") == "GOVERNANCE_BYPASS":
            require(case["disposition"] != "ALLOW", f"{fid} bypass must originate from non-ALLOW")
            require(case["observation_state"] == "OBSERVED_EFFECT", f"{fid} bypass lacks observed effect")
        if case.get("reconciliation_state") == "DIVERGENT":
            require(case["disposition"] == "ALLOW", f"{fid} divergence fixture must preserve ALLOW decision")
            require(case["commit_state"] == "COMMITTED", f"{fid} divergence fixture must preserve committed execution")

    require(decisions == {"ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"}, "fixtures must cover all terminal dispositions")
    require("decision_state.deny.no_effect" in ids, "DENY no-effect fixture missing")
    require("decision_state.fail_closed.no_effect" in ids, "FAIL_CLOSED no-effect fixture missing")
    require("decision_state.review.successor" in ids, "REVIEW successor fixture missing")
    require("decision_state.allow.divergent_observation" in ids, "ALLOW divergence fixture missing")
    require("decision_state.deny.observed_effect_bypass" in ids, "DENY bypass fixture missing")

    print(json.dumps({
        "status": "PASS",
        "schema": "steggate.decision-state.v1",
        "fixtures": len(cases),
        "terminal_dispositions": sorted(decisions),
        "non_allow_non_execution": True,
        "fail_closed_distinct": True,
        "review_successor_distinct": True,
        "divergence_preserved": True,
        "governance_bypass_detectable": True
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
