#!/usr/bin/env python3
"""Validate the machine-observable activation state for the first real StegGate boundary."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "management" / "first-boundary-activation.json"
ALLOWED_STATES = {"BLOCKED", "READY", "CLAIMED", "COMPLETE", "FAILED", "REVIEW_REQUIRED", "SUPERSEDED", "MERGED"}


def main() -> int:
    data = json.loads(STATE.read_text(encoding="utf-8"))
    if data.get("schema_version") != "steggate.first-boundary-activation.v1":
        raise SystemExit("first-boundary activation schema mismatch")
    state = data.get("state")
    if state not in ALLOWED_STATES:
        raise SystemExit(f"invalid first-boundary state: {state!r}")
    if data.get("authority_effect") is not False:
        raise SystemExit("first-boundary activation record must have authority_effect=false")
    prerequisites = data.get("completed_prerequisites")
    if not isinstance(prerequisites, dict) or not prerequisites or not all(prerequisites.values()):
        raise SystemExit("first-boundary prerequisite evidence is incomplete")
    release = data.get("release_inputs")
    if not isinstance(release, dict):
        raise SystemExit("first-boundary release_inputs missing")
    target = release.get("consequential_target_ref")
    authority = release.get("authority_model_ref")
    if bool(target) != bool(authority):
        raise SystemExit("partial first-boundary release input is forbidden")
    if state == "BLOCKED":
        if target or authority:
            raise SystemExit("BLOCKED state must not carry satisfied release inputs; transition to READY")
        result = "BLOCKED"
    elif state == "READY":
        if not target or not authority:
            raise SystemExit("READY requires consequential_target_ref and authority_model_ref")
        if data.get("claim_state") != "UNCLAIMED":
            raise SystemExit("READY state must remain UNCLAIMED until a finite implementation claim is created")
        result = "READY"
    elif state == "CLAIMED":
        if not target or not authority:
            raise SystemExit("CLAIMED requires satisfied release inputs")
        claim = data.get("active_claim")
        required = {"claim_id", "claimed_at", "expires_at", "expected_evidence", "collision_boundaries"}
        if not isinstance(claim, dict) or not required.issubset(claim):
            raise SystemExit("CLAIMED requires a finite active_claim record")
        result = "CLAIMED"
    else:
        result = state
    print(json.dumps({
        "status": "PASS",
        "task_id": data["task_id"],
        "activation_state": result,
        "release_inputs_satisfied": bool(target and authority),
        "next_action": data.get("next_action_when_ready"),
        "authority_effect": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
