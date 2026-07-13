#!/usr/bin/env python3
"""Generate governed deployment notification body from repository evidence and handoff sections."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HANDOFF = ROOT / "docs" / "ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md"
DEFAULT_BUNDLE = ROOT / "status" / "deployed-evidence-bundle.json"
DEFAULT_DECISION = ROOT / "status" / "release-evidence-decision.json"
DEFAULT_MARKDOWN = ROOT / "status" / "deployment-notification-email.md"
DEFAULT_JSON = ROOT / "status" / "deployment-notification-envelope.json"
REQUIRED_SECTIONS = (
    "Current goal",
    "Current publication posture",
    "Current release gate",
    "Boundary",
    "Next tasks",
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def repository_path(path: Path) -> Path:
    """Resolve a CLI path against the repository root without changing its boundary."""
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def extract_sections(markdown: str) -> dict[str, str]:
    lines = markdown.splitlines()
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        if line.startswith("## "):
            heading = line[3:].strip()
            current = heading if heading in REQUIRED_SECTIONS else None
            if current is not None:
                sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    result = {name: "\n".join(sections.get(name, [])).strip() for name in REQUIRED_SECTIONS}
    missing = [name for name, body in result.items() if not body]
    if missing:
        raise ValueError("missing required handoff sections: " + ", ".join(missing))
    return result


def render(subject: str, envelope: dict, sections: dict[str, str]) -> str:
    lines = [
        f"Subject: {subject}",
        "",
        "# Governed Deployment Evidence Notification",
        "",
        f"- Repository: `{envelope['repository']}`",
        f"- Commit: `{envelope['commit_sha']}`",
        f"- Workflow run: `{envelope['workflow_run_id']}`",
        f"- Evidence bundle SHA-256: `{envelope['bundle_sha256']}`",
        f"- Public-review decision: **{envelope['public_review_decision']}**",
        f"- Stable-release decision: **{envelope['stable_release_decision']}**",
        "",
        "This message is a signal, not release authority. It reports that a governed deployment-evidence candidate is available and does not itself authorize release-gate promotion or stable release.",
        "",
    ]
    for heading in REQUIRED_SECTIONS:
        lines.extend([f"## Handoff — {heading}", "", sections[heading], ""])
    lines.extend([
        "## Monitoring instruction",
        "",
        "Retrieve the retained `deployed-publication-evidence` artifact, verify its bundle SHA-256 and internal evidence, then create the next governed task only if verification passes.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--handoff", type=Path, default=DEFAULT_HANDOFF)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--decision", type=Path, default=DEFAULT_DECISION)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args()

    handoff_path = repository_path(args.handoff)
    bundle_path = repository_path(args.bundle)
    decision_path = repository_path(args.decision)
    markdown_path = repository_path(args.markdown)
    json_path = repository_path(args.json)

    try:
        handoff_relative_path = handoff_path.relative_to(ROOT).as_posix()
        handoff_text = handoff_path.read_text(encoding="utf-8")
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        sections = extract_sections(handoff_text)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"DEPLOYMENT_NOTIFICATION=FAIL-CLOSED\nreason={exc}")
        return 1

    commit = bundle.get("commit_sha")
    if not commit or decision.get("commit_sha") != commit:
        print("DEPLOYMENT_NOTIFICATION=FAIL-CLOSED\nreason=bundle and decision commit mismatch")
        return 1

    repository = bundle.get("repository") or os.getenv("GITHUB_REPOSITORY", "StegVerse-Labs/ara-admissibility-interop")
    short_commit = str(commit)[:12]
    subject = (
        f"[StegVerse][DEPLOYMENT-EVIDENCE][ARA]"
        f"[{decision.get('public_review_decision', 'UNKNOWN')}] {short_commit}"
    )
    envelope = {
        "schema_version": "1.0.0",
        "notification_type": "governed-deployment-evidence-available",
        "subject": subject,
        "repository": repository,
        "commit_sha": commit,
        "workflow_run_id": bundle.get("workflow_run_id"),
        "workflow_run_attempt": bundle.get("workflow_run_attempt"),
        "artifact_name": "deployed-publication-evidence",
        "bundle_sha256": bundle.get("bundle_sha256"),
        "public_review_decision": decision.get("public_review_decision"),
        "stable_release_decision": decision.get("stable_release_decision"),
        "handoff_path": handoff_relative_path,
        "handoff_sha256": sha256_text(handoff_text),
        "included_handoff_sections": list(REQUIRED_SECTIONS),
        "next_action": "retrieve-and-independently-verify",
        "authority_boundary": "Email notification is a signal, not release authority.",
    }
    body = render(subject, envelope, sections)
    envelope["body_sha256"] = sha256_text(body)

    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(body, encoding="utf-8")
    json_path.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
    print("DEPLOYMENT_NOTIFICATION=CREATED")
    print(f"subject={subject}")
    print(f"body={markdown_path}")
    print(f"envelope={json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
