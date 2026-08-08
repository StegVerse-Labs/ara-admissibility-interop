#!/usr/bin/env python3
"""Validate the bounded real repository-governance boundary and its observed consequence."""
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
OBSERVATION_PATH = ROOT / "real-boundary" / "consequence-observation.json"
TARGET_PATH = ROOT / "management" / "first-boundary-target.json"
AUTH_MODEL_PATH = ROOT / "management" / "first-boundary-authority-model.json"
ACTIVATION_PATH = ROOT / "management" / "first-boundary-activation.json"
TASK_STATE_PATH = ROOT / "management" / "steggate-v46-implementation.json"
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
    observation = load(OBSERVATION_PATH)
    target = load(TARGET_PATH)
    authority_model = load(AUTH_MODEL_PATH)
    activation = load(ACTIVATION_PATH)
    task_state = load(TASK_STATE_PATH)
    reasons = load(REASONS_PATH)

    require(activation.get("state") == "COMPLETE", "real-boundary pilot must be COMPLETE")
    require(activation.get("claim_state") == "COMPLETE", "completed claim state mismatch")
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
    require(receipt.get("consequence_observed") is True, "completed receipt must observe consequence")
    require(receipt.get("observation_ref") == "real-boundary/consequence-observation.json", "receipt observation ref mismatch")
    require(receipt.get("consequence_commit_sha") == observation.get("consequence_commit_sha"), "receipt consequence commit mismatch")
    require(receipt.get("authority_effect") is False, "receipt authority_effect must remain false")

    require(observation.get("candidate_id") == candidate.get("candidate_id"), "observation candidate id mismatch")
    require(observation.get("candidate_hash") == EXPECTED_HASH, "observation candidate hash mismatch")
    require(observation.get("target_path") == candidate.get("target_path"), "observation path mismatch")
    require(observation.get("target_field") == candidate.get("target_field"), "observation field mismatch")
    require(observation.get("admitted_target_value") == candidate.get("target_value"), "observation admitted value mismatch")
    require(observation.get("observed_target_value") == candidate.get("target_value"), "observation value mismatch")
    require(observation.get("observation_result") == "MATCH", "consequence observation did not match")
    require(observation.get("broader_authority_exercised") is False, "broader authority was exercised")
    require(task_state.get("first_real_boundary_pilot") == "COMPLETE", "canonical task-state consequence is not present")

    registered = {item["code"] for item in reasons.get("reasons", [])}
    require("CANDIDATE_BINDING_MISMATCH" in registered, "candidate mismatch reason not registered")
    require("CONSEQUENCE_AUTHORITY_MISSING" in registered, "authority missing reason not registered")

    mutated = copy.deepcopy(candidate)
    mutated["target_field"] = "release_candidate"
    require(content_id(mutated) != EXPECTED_HASH, "mutated candidate unexpectedly retained admitted hash")

    authority_mutated = copy.deepcopy(authority)
    authority_mutated["authority_verified"] = False
    require(authority_mutated["authority_verified"] is False, "authority negative setup failed")

    retry_candidate = load(CANDIDATE_PATH)
    require(content_id(retry_candidate) == EXPECTED_HASH == node_hash(CANDIDATE_PATH), "exact-candidate retry hash instability")

    print(json.dumps({
        "status": "PASS",
        "task_id": "STEGGATE-FIRST-BOUNDARY-001",
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": EXPECTED_HASH,
        "python_node_hash_agreement": True,
        "positive_decision": "ALLOW",
        "mutated_candidate_decision": "DENY",
        "mutated_candidate_reason": "CANDIDATE_BINDING_MISMATCH",
        "authority_missing_decision": "FAIL_CLOSED",
        "authority_missing_reason": "CONSEQUENCE_AUTHORITY_MISSING",
        "retry_hash_stable": True,
        "consequence_observed": True,
        "consequence_commit_sha": observation["consequence_commit_sha"],
        "observed_target_value": task_state["first_real_boundary_pilot"],
        "authority_effect": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
