#!/usr/bin/env python3
"""Evaluate verified publication evidence into bounded release-gate decisions.

This tool never authorizes or creates a stable release. It reports whether the
provided evidence supports the declared public-review deployment and whether
all separately declared stable-release gates are satisfied.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from verify_publication_evidence import verify

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECEIPT = ROOT / "status" / "publication-receipt.json"
DEFAULT_MANIFEST = ROOT / "release-manifest.json"
DEFAULT_OUTPUT = ROOT / "status" / "release-evidence-decision.json"
DEFAULT_MARKDOWN = ROOT / "status" / "release-evidence-decision.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(
    receipt: dict,
    manifest: dict,
    artifact_root: Path | None = None,
    identity_file: Path | None = None,
    live_root_file: Path | None = None,
) -> dict:
    verification_problems = verify(
        receipt,
        artifact_root=artifact_root,
        identity_file=identity_file,
        live_root_file=live_root_file,
    )
    live = receipt.get("live_root_verification", {})
    release_gate = manifest.get("release_gate", {})
    blockers: list[str] = []

    if verification_problems:
        blockers.extend(f"evidence:{problem}" for problem in verification_problems)
    if live.get("result") != "passed":
        blockers.append("live-deployment-not-verified")
    if receipt.get("publication_status") != "public_review":
        blockers.append("publication-status-not-public-review")
    if receipt.get("canonical_status") != "not_authorized":
        blockers.append("unexpected-canonical-status")
    if receipt.get("reliance_posture") != "research_and_review_only":
        blockers.append("unexpected-reliance-posture")

    public_review_ready = not blockers

    stable_blockers: list[str] = []
    if not public_review_ready:
        stable_blockers.append("public-review-evidence-not-verified")
    for field in (
        "repo_check_workflow_verified",
        "pages_workflow_verified",
        "https_deployment_url_verified",
        "built_entrypoint_verified",
        "live_root_page_verified",
        "deployed_publication_receipt_verified",
        "stable_release_authorized",
    ):
        if release_gate.get(field) is not True:
            stable_blockers.append(f"release-gate:{field}")

    evidence_scope = {
        "receipt": True,
        "artifact_root": artifact_root is not None,
        "identity_file": identity_file is not None,
        "live_root_file": live_root_file is not None,
    }

    return {
        "schema_version": "1.1.0",
        "decision_type": "governed-release-evidence-decision",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": receipt.get("repository"),
        "candidate": manifest.get("candidate"),
        "commit_sha": receipt.get("commit_sha"),
        "artifact_tree_sha256": receipt.get("artifact_tree_sha256"),
        "manifest_sha256": receipt.get("manifest_sha256"),
        "deployment_url": receipt.get("deployment_url"),
        "deployed_commit_sha": live.get("deployed_commit_sha"),
        "evidence_scope": evidence_scope,
        "evidence_verification": "pass" if not verification_problems else "fail",
        "evidence_problems": verification_problems,
        "public_review_decision": "ALLOW" if public_review_ready else "BLOCK",
        "public_review_blockers": blockers,
        "stable_release_decision": "ALLOW" if not stable_blockers else "BLOCK",
        "stable_release_blockers": stable_blockers,
        "stable_release_automatically_authorized": False,
        "boundary": (
            "Verified public-review deployment evidence does not establish canonical status, "
            "independent review, clinical validity, regulatory authorization, or execution authority."
        ),
    }


def render_markdown(decision: dict) -> str:
    scope = decision.get("evidence_scope", {})
    lines = [
        "# Release Evidence Decision",
        "",
        f"- Candidate: `{decision.get('candidate')}`",
        f"- Commit: `{decision.get('commit_sha')}`",
        f"- Evidence verification: **{decision['evidence_verification']}**",
        f"- Public-review decision: **{decision['public_review_decision']}**",
        f"- Stable-release decision: **{decision['stable_release_decision']}**",
        "",
        "## Evidence scope",
        "",
        f"- Receipt checked: `{scope.get('receipt', False)}`",
        f"- Built artifact checked: `{scope.get('artifact_root', False)}`",
        f"- Deployment identity checked: `{scope.get('identity_file', False)}`",
        f"- Captured live root checked: `{scope.get('live_root_file', False)}`",
        "",
        "## Public-review blockers",
    ]
    blockers = decision["public_review_blockers"]
    lines.extend([f"- `{item}`" for item in blockers] or ["- None"])
    lines.extend(["", "## Stable-release blockers"])
    stable = decision["stable_release_blockers"]
    lines.extend([f"- `{item}`" for item in stable] or ["- None"])
    lines.extend(["", "## Boundary", "", decision["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--identity-file", type=Path)
    parser.add_argument("--live-root-file", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--require-public-review-allow", action="store_true")
    args = parser.parse_args()

    try:
        receipt = load_json(args.receipt)
        manifest = load_json(args.manifest)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"RELEASE_EVIDENCE_DECISION=FAIL-CLOSED\nreason={exc}")
        return 1

    decision = evaluate(
        receipt,
        manifest,
        artifact_root=args.artifact_root,
        identity_file=args.identity_file,
        live_root_file=args.live_root_file,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(render_markdown(decision), encoding="utf-8")

    print(f"RELEASE_EVIDENCE_DECISION={decision['public_review_decision']}")
    print(f"stable_release={decision['stable_release_decision']}")
    print(f"output={args.output}")
    if args.require_public_review_allow and decision["public_review_decision"] != "ALLOW":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
