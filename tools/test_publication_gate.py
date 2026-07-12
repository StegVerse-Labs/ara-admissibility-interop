#!/usr/bin/env python3
"""Dependency-free tests for the governed publication gate."""

from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

from check_publication_gate import validate

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "publication" / "fixtures"
BASE = json.loads((ROOT / "publication-manifest.json").read_text(encoding="utf-8"))


def run_case(name: str, manifest: dict, expect_allow: bool, root: Path) -> None:
    errors = validate(manifest, root=root)
    allowed = not errors
    if allowed != expect_allow:
        raise AssertionError(f"{name}: expected allow={expect_allow}, errors={errors}")
    state = "ALLOW" if allowed else "FAIL-CLOSED"
    print(f"{name}: {state}")


def load_fixture(name: str) -> dict:
    path = FIXTURES / name
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise AssertionError(f"fixture must be a JSON object: {path}")
    return data


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        docs = root / "docs"
        docs.mkdir()
        (docs / "index.md").write_text("# test\n", encoding="utf-8")

        valid = copy.deepcopy(BASE)
        run_case("valid-public-review", valid, True, root)

        valid_canonical = copy.deepcopy(BASE)
        valid_canonical["publication_status"] = "canonical"
        valid_canonical["canonical_status"] = "authorized"
        valid_canonical["independent_review_status"] = "complete"
        run_case("valid-canonical-after-review", valid_canonical, True, root)

        fixture_names = [
            "deny-canonical-without-review.json",
            "deny-escaping-publish-root.json",
            "deny-unsupported-target.json",
            "deny-missing-required-field.json",
            "deny-empty-non-claims.json",
        ]
        for fixture_name in fixture_names:
            run_case(fixture_name.removesuffix(".json"), load_fixture(fixture_name), False, root)

        unauthorized_canonical = copy.deepcopy(BASE)
        unauthorized_canonical["publication_status"] = "canonical"
        unauthorized_canonical["canonical_status"] = "not_authorized"
        run_case("canonical-without-authorization", unauthorized_canonical, False, root)

        missing_root = copy.deepcopy(BASE)
        missing_root["publish_root"] = "missing-docs"
        run_case("missing-publish-root", missing_root, False, root)

        no_index = copy.deepcopy(BASE)
        empty_root = root / "empty-docs"
        empty_root.mkdir()
        no_index["publish_root"] = "empty-docs"
        run_case("publish-root-without-index", no_index, False, root)

        invalid_allowed_statuses = copy.deepcopy(BASE)
        invalid_allowed_statuses["allowed_publication_statuses"] = []
        run_case("empty-allowed-statuses", invalid_allowed_statuses, False, root)

        invalid_policy = copy.deepcopy(BASE)
        invalid_policy["gate_policy"] = []
        run_case("invalid-gate-policy", invalid_policy, False, root)

        clinical_overreach = copy.deepcopy(BASE)
        clinical_overreach["clinical_status"] = "validated"
        clinical_overreach["regulatory_status"] = "not_authorized"
        clinical_overreach["reliance_posture"] = "clinical_reliance"
        run_case("clinical-reliance-without-authorization", clinical_overreach, False, root)

    print("publication gate tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
