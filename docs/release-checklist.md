# Release Checklist

Use this checklist before tagging, citing, or presenting the repository as a release candidate.

## Candidate identity

- [ ] `VERSION` exists.
- [ ] `VERSION` matches the intended release candidate.
- [ ] `CHANGELOG.md` has an entry for the candidate.
- [ ] `docs/release-readiness.md` names the same candidate.

## Boundary

- [ ] `admissibility/non-claims.md` is present.
- [ ] README states that this repository does not replace ARA.
- [ ] Release notes avoid endorsement, certification, upstream acceptance, or production authority claims.

## Dependency policy

- [ ] `docs/dependency-policy.md` is present.
- [ ] Baseline validation remains dependency-free.
- [ ] No required dependencies are declared for the default validation path.
- [ ] Optional dependencies are documented before use.
- [ ] Missing optional dependencies return a clean skip with exit code `0`.
- [ ] Validation does not install packages or require network access.

## Validation

- [ ] Run:

```bash
python3 tools/generate_validation_report.py
```

- [ ] `status/generated-status.json` is generated.
- [ ] `status/validation-report.md` is generated.
- [ ] Generated state is `self-check-pass`.
- [ ] Validation report shows zero problems for required checks.
- [ ] Optional strict validation is visible in generated status.
- [ ] If `jsonschema` is absent, optional strict validation reports `skip` with exit code `0`.
- [ ] If `jsonschema` is installed, optional strict validation reports `pass` or `fail` according to full schema validation.

## Optional strict validation

Optional strict validation can be run directly:

```bash
python3 tools/validate_with_jsonschema_optional.py
```

This check is not a required dependency gate unless project dependency policy changes.

## Workflow

- [ ] Canonical workflow exists at the leading-period path:

```text
.github/workflows/repo-check.yml
```

- [ ] iOS-safe mirror exists at:

```text
iosnoperiod/github/workflows/repo-check.yml
```

- [ ] Both workflows run:

```text
python3 tools/generate_validation_report.py
```

- [ ] Both workflows publish the validation report to the GitHub Actions step summary.

## Release-readiness review

- [ ] `docs/dependency-policy.md` explains dependency classes and promotion rules.
- [ ] `docs/optional-strict-validation.md` explains optional strict validation.
- [ ] `docs/validation-report-guide.md` explains validation outputs.
- [ ] `docs/workflow-artifact-retention.md` explains optional artifact retention.
- [ ] `docs/release-readiness.md` lists criteria and non-release claims.
- [ ] Next-version candidates are documented.

## Public positioning

Recommended framing:

> This repository is an independent interoperability prototype exploring whether ARA-style artifacts can be presented as commitment candidates and evaluated under a commit-time admissibility model.

Avoid claiming:

- ARA author endorsement;
- certification of external artifacts;
- production Standing Proof Engine behavior;
- journal, conference, lab, or platform acceptance;
- execution authority;
- required full JSON Schema conformance when the optional dependency is absent.

## Release outcome

When all required checks pass, the repository may be treated as `0.1.0-release-candidate` for review and citation as an independent StegVerse-Labs interoperability prototype.
