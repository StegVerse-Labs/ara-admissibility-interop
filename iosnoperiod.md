# iOS No-Period Mirror

Some mobile workflows make leading-period paths difficult to create or move directly.

This repository therefore provides an iOS-safe mirror under `iosnoperiod/`.

## Mapping

| iOS-safe path | Canonical path |
| --- | --- |
| `iosnoperiod/github/workflows/repo-check.yml` | `.github/workflows/repo-check.yml` |

The canonical path shown above begins with a leading period. It is displayed here for accuracy; elsewhere it may be shown without the leading period when required by iOS-safe instructions.

## Use

Move or copy:

```text
iosnoperiod/github/workflows/repo-check.yml
```

to:

```text
.github/workflows/repo-check.yml
```

when canonical GitHub Actions activation is needed.
