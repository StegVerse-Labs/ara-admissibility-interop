# Dependency Policy

This repository preserves dependency-free validation as the default operating posture.

## Policy classes

| Class | Meaning | Current use |
| --- | --- | --- |
| Required dependency | A package or tool that must be installed for baseline validation to pass. | None |
| Optional dependency | A package or tool that enables stricter checks but must not be required for baseline validation. | `jsonschema` |
| Prohibited dependency | A package or tool that silently changes baseline behavior, introduces network dependence, or makes CI non-reproducible without explicit policy approval. | Any undeclared validation dependency |

## Baseline rule

The following command must remain dependency-free:

```bash
python3 tools/generate_validation_report.py
```

It may call optional checks only when those checks return a clean skip if their optional dependency is absent.

## Optional dependency rule

Optional dependencies are allowed only when all of the following are true:

1. the dependency is documented;
2. the dependency is not required for default CI success;
3. absence of the dependency exits with code `0`;
4. generated status clearly reports `skip`, `pass`, or `fail`;
5. the boundary between dependency-free and stricter validation is explicit.

## Current optional dependency

| Dependency | Tool | Absent behavior | Present behavior |
| --- | --- | --- | --- |
| `jsonschema` | `tools/validate_with_jsonschema_optional.py` | `skip`, exit code `0` | full JSON Schema validation with pass/fail result |

## Promotion rule

An optional dependency may become required only after a dependency-policy update that states:

- why the stricter dependency is required;
- what environments are expected to install it;
- how CI installs it;
- what failure behavior changes;
- whether the repository still supports dependency-free local validation.

## Prohibited behavior

Do not add tools that:

- install packages during validation without explicit user action;
- require network access during validation;
- fail default CI only because an optional package is missing;
- silently replace dependency-free checks with stricter dependency-backed checks;
- make external artifact certification claims because stricter validation passed.

## Boundary

Dependency policy is a validation policy only. It does not change the repository's claims, non-claims, or authority model.
