#!/usr/bin/env python3
"""Canonicalize StegGate JSON under stegverse.jcs.v1 using stdlib only."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

PROFILE = "stegverse.jcs.v1"
MAX_SAFE_INTEGER = 9007199254740991


class CanonicalizationError(ValueError):
    pass


def _validate_string(value: str) -> None:
    for ch in value:
        cp = ord(ch)
        if 0xD800 <= cp <= 0xDFFF:
            raise CanonicalizationError("unpaired surrogate is outside stegverse.jcs.v1")


def _member_sort_key(value: str) -> bytes:
    _validate_string(value)
    return value.encode("utf-16-be")


def _serialize(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        if abs(value) > MAX_SAFE_INTEGER:
            raise CanonicalizationError("integer exceeds stegverse.jcs.v1 interoperable range")
        return str(value)
    if isinstance(value, float):
        raise CanonicalizationError("floating-point values are outside stegverse.jcs.v1")
    if isinstance(value, str):
        _validate_string(value)
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        return "[" + ",".join(_serialize(item) for item in value) + "]"
    if isinstance(value, dict):
        for key in value:
            if not isinstance(key, str):
                raise CanonicalizationError("object member names must be strings")
            _validate_string(key)
        keys = sorted(value.keys(), key=_member_sort_key)
        return "{" + ",".join(_serialize(key) + ":" + _serialize(value[key]) for key in keys) + "}"
    raise CanonicalizationError(f"unsupported value type: {type(value).__name__}")


def canonicalize(value: Any) -> bytes:
    return _serialize(value).encode("utf-8")


def content_id(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonicalize(value)).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="JSON input file")
    parser.add_argument("--hash-only", action="store_true", help="print only sha256:<hex>")
    args = parser.parse_args()
    try:
        value = json.loads(args.path.read_text(encoding="utf-8"))
        data = canonicalize(value)
    except (OSError, json.JSONDecodeError, CanonicalizationError) as exc:
        print(f"canonicalization failed: {exc}", file=sys.stderr)
        return 2
    if args.hash_only:
        print("sha256:" + hashlib.sha256(data).hexdigest())
    else:
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.write(b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
