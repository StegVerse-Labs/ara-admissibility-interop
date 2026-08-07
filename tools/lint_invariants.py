#!/usr/bin/env python3
"""Validate StegGate registries, fixtures, reasons, algebra, and schemas using stdlib only.

Registry .yaml files intentionally use JSON syntax, which is valid YAML 1.2,
so the repository does not acquire a parser dependency for this foundation.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REASON_CODE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"invalid JSON/YAML-subset file {path.relative_to(ROOT)}: {exc}")


def load_reason_registry() -> set[str]:
    path = ROOT / "reasons" / "registry.v1.json"
    data = load_json(path)
    if data.get("schema_version") != "steggate.reason-registry.v1":
        raise SystemExit("reason registry schema_version mismatch")
    if data.get("authority_effect") is not False:
        raise SystemExit("reason registry must remain authority_effect=false")
    reasons = data.get("reasons")
    if not isinstance(reasons, list) or not reasons:
        raise SystemExit("reason registry has no reasons")
    codes: set[str] = set()
    for item in reasons:
        code = item.get("code")
        if not isinstance(code, str) or not REASON_CODE.fullmatch(code):
            raise SystemExit(f"invalid reason code: {code!r}")
        if code in codes:
            raise SystemExit(f"duplicate reason code: {code}")
        if not item.get("class") or not item.get("description"):
            raise SystemExit(f"incomplete reason registry entry: {code}")
        codes.add(code)
    return codes


def collect_fixture_ids_and_reasons() -> tuple[set[str], set[str]]:
    ids: set[str] = set()
    reasons: set[str] = set()
    for path in sorted((ROOT / "fixtures").rglob("*.json")):
        data = load_json(path)
        for item in data.get("fixtures", []):
            fixture_id = item.get("fixture_id")
            if not fixture_id:
                raise SystemExit(f"fixture missing fixture_id: {path.relative_to(ROOT)}")
            if fixture_id in ids:
                raise SystemExit(f"duplicate fixture_id: {fixture_id}")
            ids.add(fixture_id)
            expected = item.get("expected")
            if isinstance(expected, dict):
                reason = expected.get("reason_code")
                if reason is not None:
                    if not isinstance(reason, str) or not REASON_CODE.fullmatch(reason):
                        raise SystemExit(f"invalid fixture reason_code in {fixture_id}: {reason!r}")
                    reasons.add(reason)
    vectors = load_json(ROOT / "algebra" / "compose-vectors.json")
    for item in vectors.get("vectors", []):
        fixture_id = item.get("fixture_id")
        if not fixture_id:
            raise SystemExit("composition vector missing fixture_id")
        if fixture_id in ids:
            raise SystemExit(f"duplicate fixture/vector id: {fixture_id}")
        ids.add(fixture_id)
    return ids, reasons


def lint_registries(fixture_ids: set[str]) -> tuple[int, int, set[str]]:
    seen: set[str] = set()
    reasons: set[str] = set()
    invariant_count = 0
    reference_count = 0
    for path in sorted((ROOT / "invariants").glob("*.yaml")):
        data = load_json(path)
        profile = data.get("profile")
        if not profile:
            raise SystemExit(f"registry missing profile: {path.relative_to(ROOT)}")
        for inv in data.get("invariants", []):
            invariant_count += 1
            iid = inv.get("invariant_id")
            statement = inv.get("normative_statement")
            refs = inv.get("required_fixture_ids")
            reason = inv.get("failure_reason_code")
            if not iid or not statement or not refs or not reason:
                raise SystemExit(f"incomplete invariant in {path.relative_to(ROOT)}: {iid!r}")
            if iid in seen:
                raise SystemExit(f"duplicate invariant_id: {iid}")
            if not isinstance(reason, str) or not REASON_CODE.fullmatch(reason):
                raise SystemExit(f"invalid invariant failure_reason_code for {iid}: {reason!r}")
            seen.add(iid)
            reasons.add(reason)
            for ref in refs:
                reference_count += 1
                if ref not in fixture_ids:
                    raise SystemExit(f"invariant {iid} references missing fixture {ref}")
    if invariant_count == 0:
        raise SystemExit("no invariants found")
    return invariant_count, reference_count, reasons


def validate_reason_coverage(registered: set[str], normative: set[str]) -> None:
    missing = sorted(normative - registered)
    unused = sorted(registered - normative)
    if missing:
        raise SystemExit(f"unregistered normative reason codes: {missing}")
    if unused:
        raise SystemExit(f"reason registry contains unused v1 codes: {unused}")


def run_algebra_vectors() -> int:
    data = load_json(ROOT / "algebra" / "compose-vectors.json")
    count = 0
    for v in data.get("vectors", []):
        count += 1
        op = v["operator"]
        vals = [v[k] for k in ("a", "b", "c") if k in v]
        if op == "intersection":
            result = sorted(set(vals[0]).intersection(*map(set, vals[1:])))
        elif op == "min":
            result = min(vals)
        elif op == "latest":
            result = max(vals)
        elif op == "and":
            result = all(vals)
        else:
            raise SystemExit(f"unsupported test operator: {op}")
        if result != v["expected"]:
            raise SystemExit(f"vector {v['fixture_id']} failed: {result!r} != {v['expected']!r}")
    return count


def lint_schemas() -> int:
    count = 0
    for path in sorted((ROOT / "schemas").glob("*.json")):
        data = load_json(path)
        count += 1
        if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            raise SystemExit(f"schema draft mismatch: {path.relative_to(ROOT)}")
        if not data.get("$id") or data.get("type") != "object":
            raise SystemExit(f"schema foundation incomplete: {path.relative_to(ROOT)}")
    if count == 0:
        raise SystemExit("no schemas found")
    return count


def main() -> int:
    registered_reasons = load_reason_registry()
    fixture_ids, fixture_reasons = collect_fixture_ids_and_reasons()
    invariants, references, invariant_reasons = lint_registries(fixture_ids)
    normative_reasons = fixture_reasons | invariant_reasons
    validate_reason_coverage(registered_reasons, normative_reasons)
    vectors = run_algebra_vectors()
    schemas = lint_schemas()
    print(json.dumps({
        "status": "PASS",
        "invariants": invariants,
        "fixture_ids": len(fixture_ids),
        "fixture_references": references,
        "reason_codes": len(registered_reasons),
        "normative_reason_codes": len(normative_reasons),
        "algebra_vectors": vectors,
        "schemas": schemas,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
