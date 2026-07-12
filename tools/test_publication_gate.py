#!/usr/bin/env python3
"""Dependency-free tests for the governed publication gate."""

from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

from check_publication_gate import validate

ROOT = Path(__file__).resolve().parents[1]
BASE = json.loads((ROOT / "publication-manifest.json").read_text(encoding="utf-8"))


def run_case(name: str, manifest: dict, expect_allow: bool, root: Path) -> None:
    errors = validate(manifest, root=root)
    allowed = not errors
    if allowed != expect_allow:
        raise AssertionError(f"{name}: expected allow={expect_allow}, errors={errors}")
    state = "ALLOW" if allowed else "FAIL-CLOSED"
    print(f"{name}: {state}")


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        docs = root / "docs"
        docs.mkdir()
        (docs / "index.md").write_text("# test\n", encoding="utf-8")

        valid = copy.deepcopy(BASE)
        run_case("valid-public-review", valid, True, root)

        canonical_without_review = copy.deepcopy(BASE)
        canonical_without_review["publication_status"] = "canonical"
        canonical_without_review["canonical_status"] = "authorized"
        canonical_without_review["independent_review_status"] = "not_started"
        run_case("canonical-without-review", canonical_without_review, False, root)

        unauthorized_canonical = copy.deepcopy(BASE)
        unauthorized_canonical["publication_status"] = "canonical"
        unauthorized_canonical["canonical_status"] = "not_authorized"
        run_case("canonical-without-authorization", unauthorized_canonical, False, root)

        escaping_root = copy.deepcopy(BASE)
        escaping_root["publish_root"] = "../outside"
        run_case("escaping-publish-root", escaping_root, False, root)

        unsupported_target = copy.deepcopy(BASE)
        unsupported_target["publish_target"] = "external_platform"
        run_case("unsupported-publish-target", unsupported_target, False, root)

        missing_non_claims = copy.deepcopy(BASE)
        missing_non_claims["required_non_claims"] = []
        run_case("missing-non-claims", missing_non_claims, False, root)

    print("publication gate tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
