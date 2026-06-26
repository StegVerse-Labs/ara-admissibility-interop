# Optional Strict Validation

The repository keeps dependency-free validation as its default path.

An optional stricter path is available through:

```bash
python3 tools/validate_with_jsonschema_optional.py
```

## Why optional

The default repository validation must work without installing external packages. This keeps the interop prototype easy to run in local, CI, and constrained environments.

Full JSON Schema validation is useful, but it depends on the `jsonschema` Python package. The optional validator therefore behaves as follows:

| Environment | Result |
| --- | --- |
| `jsonschema` is not installed | Clean `skip`, exit code `0` |
| `jsonschema` is installed and examples are valid | `pass`, exit code `0` |
| `jsonschema` is installed and examples are invalid | `fail`, exit code `1` |

## Enable strict validation locally

Install the optional dependency in your preferred environment:

```bash
python3 -m pip install jsonschema
```

Then run:

```bash
python3 tools/validate_with_jsonschema_optional.py
```

## CI behavior

`tools/generate_status.py` includes the optional strict validator. Because the validator returns a clean skip when `jsonschema` is absent, CI remains dependency-free by default.

The generated status will still show that the optional strict check ran and whether it skipped, passed, or failed.

## Boundary

A skipped strict validation check does not mean full JSON Schema validation passed. It means the repository preserved its dependency-free baseline and did not require optional packages.

A passing strict validation check means the current examples passed validation under the installed `jsonschema` package.

## Future policy decision

If the project later adopts a dependency policy, this optional path can become required by changing CI setup and treating strict validation as a hard gate.
