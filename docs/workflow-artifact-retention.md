# Workflow Artifact Retention

The repository workflow currently generates validation outputs during CI by running:

```text
python3 tools/generate_validation_report.py
```

That command writes:

```text
status/generated-status.json
status/validation-report.md
```

## Purpose

Artifact retention allows downstream maintainers, reviewers, and ecosystem management tools to retrieve the generated status and validation report from a workflow run.

## Drop-in workflow extension

Add these steps after the validation report generation step in the canonical workflow path:

```text
.github/workflows/repo-check.yml
```

The same change should be mirrored to the iOS-safe path:

```text
iosnoperiod/github/workflows/repo-check.yml
```

Suggested steps:

```yaml
      - name: Upload generated status
        uses: actions/upload-artifact@v4
        with:
          name: generated-status
          path: status/generated-status.json

      - name: Upload validation report
        uses: actions/upload-artifact@v4
        with:
          name: validation-report
          path: status/validation-report.md
```

## Boundary

The workflow can pass without artifact upload as long as validation completes successfully. Artifact upload is a retention and inspection improvement, not a validation requirement.

## Handoff rule

If an ecosystem task runner manages workflow hardening, it should keep the canonical and iOS-safe workflow paths aligned whenever artifact retention is added.
