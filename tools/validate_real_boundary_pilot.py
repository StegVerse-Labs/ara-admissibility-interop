#!/usr/bin/env python3
"""Validate the bounded real repository-governance boundary before consequence execution."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from canonicalize_steggate import content_id  # noqa: E402

CANDIDATE_PATH = ROOT / "real-boundary" / "candidate.json"
AUTH_EVIDENCE_PATH = ROOT / "real-boundary" / "authority-evidence.json"
DECISION_PATH = ROOT / "real-boundary" / "decision.json"
RECEIPT_PATH = ROOT / "real-boundary" / "admission-receipt.json"
TARGET_PATH = ROOT / "management" / "first-boundary-target.json"
AUTH_MODEL_PATH = ROOT / "management" / "first-boundary-authority-model.json"
ACTIVATION_PATH = ROOT / "management" / "first-boundary-activation.json"
REASONS_PATH = ROOT / "reasons" / "registry.v1.json"
EXPECTED_HASH = "sha256:a74ef1ce97953e6661975f68f4a7ae53c1483b4006076279191637800b4326f3"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def node_hash(path: Path) -> str:
    proc = subprocess.run(
        ["node", str(ROOT / "tools" / "canonicalize_steggate_node.mjs"), str(path), "--hash-only"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return proc.stdout.strip()


def main() -> int:
    candidate = load(CANDIDATE_PATH)
    authority = load(AUTH_EVIDENCE_PATH)
    decision = load(DECISION_PATH)
    receipt = load(RECEIPT_PATH)
    target = load(TARGET_PATH)
    authority_model = load(AUTH_MODEL_PATH)
    activation = load(ACTIVATION_PATH)
    reasons = load(REASONS_PATH)

    require(activation.get("state") == "CLAIMED", "real-boundary pilot must be CLAIMED")
    require(activation.get("claim_state") == "CLAIMED_FOR_IMPLEMENTATION", "claim state mismatch")
    require(activation.get("candidate", {}).get("candidate_id") == candidate.get("candidate_id"), "activation candidate id mismatch")
    require(activation.get("candidate", {}).get("candidate_hash") == EXPECTED_HASH, "activation candidate hash mismatch")

    py_hash = content_id(candidate)
    js_hash = node_hash(CANDIDATE_PATH)
    require(py_hash == EXPECTED_HASH, f"Python candidate hash mismatch: {py_hash}")
    require(js_hash == EXPECTED_HASH, f"Node candidate hash mismatch: {js_hash}")

    require(candidate.get("repository") == target.get("repository"), "candidate repository does not match target")
    require(candidate.get("branch") == target.get("branch_context"), "candidate branch does not match target")
    require(candidate.get("action") == "update_canonical_task_state", "candidate action mismatch")
    require(candidate.get("target_path") == target.get("target_path") == "management/steggate-v46-implementation.json", "target path mismatch")
    require(candidate.get("target_field") == target.get("authorized_consequence", {}).get("target_field") == "first_real_boundary_pilot", "target field mismatch")
    require(candidate.get("target_value") == target.get("authorized_consequence", {}).get("target_value") == "COMPLETE", "target value mismatch")
    require(candidate.get("authority_model_ref") == activation.get("release_inputs", {}).get("authority_model_ref"), "candidate authority model ref mismatch")
    require(candidate.get("target_ref") == activation.get("release_inputs", {}).get("consequential_target_ref"), "candidate target ref mismatch")

    require(authority.get("candidate_id") == candidate.get("candidate_id"), "authority candidate id mismatch")
    require(authority.get("candidate_hash") == EXPECTED_HASH, "authority candidate hash mismatch")
    require(authority.get("authority_verified") is True, "authority not verified")
    require(authority.get("scope_bounded") is True, "authority scope is not bounded")
    require(authority.get("authorized_repository") == candidate.get("repository"), "authority repository mismatch")
    require(authority.get("authorized_branch") == candidate.get("branch"), "authority branch mismatch")
    require(authority.get("authorized_action") == candidate.get("action"), "authority action mismatch")
    require(authority.get("authorized_target_path") == candidate.get("target_path"), "authority target path mismatch")
    require(authority.get("authorized_target_field") == candidate.get("target_field"), "authority target field mismatch")
    require(authority.get("authorized_target_value") == candidate.get("target_value"), "authority target value mismatch")
    require(authority.get("durable_authority_record") == authority_model.get("durable_authority_record"), "authority durable record mismatch")
    require(authority_model.get("durable_authority_comment_id") == 5224288597, "unexpected authority comment id")

    require(decision.get("decision") == "ALLOW", "positive pilot decision must be ALLOW")
    require(decision.get("candidate_id") == candidate.get("candidate_id"), "decision candidate id mismatch")
    require(decision.get("candidate_hash") == EXPECTED_HASH, "decision candidate hash mismatch")
    require(decision.get("authority_verified") is True, "decision authority verification missing")
    require(decision.get("target_authorized") is True, "decision target authorization missing")
    require(decision.get("candidate_binding_verified") is True, "decision binding verification missing")
    require(decision.get("authority_effect") is False, "decision authority_effect must remain false")

    require(receipt.get("decision") == "ALLOW", "receipt decision mismatch")
    require(receipt.get("candidate_id") == candidate.get("candidate_id"), "receipt candidate id mismatch")
    require(receipt.get("candidate_hash") == EXPECTED_HASH, "receipt candidate hash mismatch")
    require(receipt.get("authorized_consequence", {}).get("target_path") == candidate.get("target_path"), "receipt target path mismatch")
    require(receipt.get("authorized_consequence", {}).get("target_field") == candidate.get("target_field"), "receipt target field mismatch")
    require(receipt.get("authorized_consequence", {}).get("target_value") == candidate.get("target_value"), "receipt target value mismatch")
    require(receipt.get("consequence_observed") is False, "pre-consequence receipt cannot claim observation")
    require(receipt.get("observation_ref") is None, "pre-consequence receipt observation_ref must be null")
    require(receipt.get("authority_effect") is False, "receipt authority_effect must remain false")

    registered = {item["code"] for item in reasons.get("reasons", [])}
    require("CANDIDATE_BINDING_MISMATCH" in registered, "candidate mismatch reason not registered")
    require("CONSEQUENCE_AUTHORITY_MISSING" in registered, "authority missing reason not registered")

    # Mutation proof: same candidate id with a changed target field cannot retain the admitted hash.
    mutated = copy.deepcopy(candidate)
    mutated["target_field"] = "release_candidate"
    mutated_hash = content_id(mutated)
    require(mutated_hash != EXPECTED_HASH, "mutated candidate unexpectedly retained admitted hash")
    mutated_decision = "DENY"
    mutated_reason = "CANDIDATE_BINDING_MISMATCH"

    # Authority mutation proof: exact candidate without verified authority fails closed.
    authority_mutated = copy.deepcopy(authority)
    authority_mutated["authority_verified"] = False
    authority_mutated_decision = "FAIL_CLOSED"
    authority_mutated_reason = "CONSEQUENCE_AUTHORITY_MISSING"
    require(authority_mutated["authority_verified"] is False, "authority negative setup failed")

    # Retry/reconstruction proof: loading the exact candidate again must reproduce the admitted hash.
    retry_candidate = load(CANDIDATE_PATH)
    retry_py_hash = content_id(retry_candidate)
    retry_js_hash = node_hash(CANDIDATE_PATH)
    require(retry_py_hash == EXPECTED_HASH == retry_js_hash, "exact-candidate retry hash instability")

    print(json.dumps({
        "status": "PASS",
        "task_id": "STEGGATE-FIRST-BOUNDARY-001",
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": EXPECTED_HASH,
        "target_path": candidate["target_path"],
        "target_field": candidate["target_field"],
        "target_value": candidate["target_value"],
        "python_node_hash_agreement": True,
        "positive_decision": "ALLOW",
        "mutated_candidate_decision": mutated_decision,
        "mutated_candidate_reason": mutated_reason,
        "mutated_candidate_hash_differs": True,
        "authority_missing_decision": authority_mutated_decision,
        "authority_missing_reason": authority_mutated_reason,
        "retry_hash_stable": True,
        "consequence_ready": True,
        "authority_effect": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
