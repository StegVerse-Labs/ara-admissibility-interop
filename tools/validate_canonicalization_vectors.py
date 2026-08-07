#!/usr/bin/env python3
"""Validate stegverse.jcs.v1 golden vectors against the canonicalizer implementation."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "fixtures" / "canonicalization" / "vectors.json"
CANON = ROOT / "tools" / "canonicalize_steggate.py"


def run_cli(value: object, *, hash_only: bool) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as tmp:
        json.dump(value, tmp, ensure_ascii=False)
        path = Path(tmp.name)
    try:
        cmd = [sys.executable, str(CANON), str(path)]
        if hash_only:
            cmd.append("--hash-only")
        return subprocess.run(cmd, text=True, capture_output=True, check=False)
    finally:
        path.unlink(missing_ok=True)


def main() -> int:
    data = json.loads(VECTORS.read_text(encoding="utf-8"))
    if data.get("profile") != "stegverse.jcs.v1":
        raise SystemExit("canonicalization vector profile mismatch")
    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise SystemExit("canonicalization vectors missing fixtures")

    seen: set[str] = set()
    positives = negatives = 0
    for fixture in fixtures:
        fid = fixture.get("fixture_id")
        if not fid or fid in seen:
            raise SystemExit(f"missing/duplicate canonicalization fixture_id: {fid!r}")
        seen.add(fid)
        kind = fixture.get("kind")
        value = fixture.get("input")
        if kind == "positive":
            positives += 1
            canonical = run_cli(value, hash_only=False)
            if canonical.returncode != 0:
                raise SystemExit(f"{fid}: canonicalizer failed: {canonical.stderr.strip()}")
            observed = canonical.stdout.rstrip("\n")
            expected = fixture.get("expected_canonical_utf8")
            if observed != expected:
                raise SystemExit(f"{fid}: canonical bytes mismatch: {observed!r} != {expected!r}")
            digest = "sha256:" + hashlib.sha256(observed.encode("utf-8")).hexdigest()
            if digest != fixture.get("expected_sha256"):
                raise SystemExit(f"{fid}: digest mismatch: {digest}")
            hash_run = run_cli(value, hash_only=True)
            if hash_run.returncode != 0 or hash_run.stdout.strip() != digest:
                raise SystemExit(f"{fid}: --hash-only mismatch")
        elif kind == "negative":
            negatives += 1
            result = run_cli(value, hash_only=False)
            if result.returncode == 0:
                raise SystemExit(f"{fid}: invalid input was accepted")
            marker = fixture.get("expected_error_contains")
            if not marker or marker not in result.stderr:
                raise SystemExit(f"{fid}: expected error marker absent: {result.stderr.strip()}")
        else:
            raise SystemExit(f"{fid}: unknown vector kind {kind!r}")

    if positives < 5 or negatives < 3:
        raise SystemExit("canonicalization vector coverage below required positive/negative floor")
    print(json.dumps({"status":"PASS","profile":"stegverse.jcs.v1","positive":positives,"negative":negatives,"total":len(fixtures)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
