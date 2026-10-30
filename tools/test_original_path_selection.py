#!/usr/bin/env python3
"""tools/tasks/select_original_paths.py: a folded job keeps its original events and paths.

G17 (StegVerse-org/.github#166): the steggate-schema-foundation job in repo-check.yml runs on every
pull request and push. On a pull request it records NOT_SELECTED (a successful job, never a skipped
one) unless a path of the original steggate-schema-foundation.yml changed; push stays SELECTED by
ruling because the job is activation_authoritative. Stdlib only; nothing
here reaches the network. Run: python3 tools/test_original_path_selection.py
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/tasks/select_original_paths.py"
SPEC = importlib.util.spec_from_file_location("select_original_paths", TOOL)
sel = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sel)
MANIFEST = sel.load()
JOB = "steggate-schema-foundation"
ENTRY = MANIFEST["jobs"][JOB]


def decide(event, files):
    return sel.decide(MANIFEST, JOB, event, files)[0]


class GlobTests(unittest.TestCase):
    def test_star_stops_at_slash_and_double_star_does_not(self):
        self.assertTrue(sel.glob_regex("data/*.json").match("data/a.json"))
        self.assertFalse(sel.glob_regex("data/*.json").match("data/x/a.json"))
        self.assertTrue(sel.glob_regex("data/**").match("data/x/y/a.json"))

    def test_later_negation_removes_an_earlier_match(self):
        self.assertFalse(sel.path_matches(["docs/**", "!docs/skip.md"], "docs/skip.md"))


class SelectionTests(unittest.TestCase):
    def test_an_unrelated_change_is_not_selected(self):
        self.assertFalse(decide("pull_request", ["README.md", "docs/index.md", "tools/generate_validation_report.py"]))

    def test_each_original_path_selects_the_job(self):
        for pattern in ENTRY["original_paths"]["pull_request"]:
            sample = pattern.replace("**", "x/y").replace("*", "z")
            self.assertTrue(decide("pull_request", [sample]), pattern)

    def test_the_host_workflow_that_now_carries_the_job_selects_it(self):
        self.assertTrue(decide("pull_request", [".github/workflows/repo-check.yml"]))

    def test_push_stays_selected_for_the_activation_authoritative_job(self):
        self.assertEqual(ENTRY["always_selected_events"], ["push"])
        self.assertTrue(decide("push", ["README.md"]))
        self.assertTrue(decide("push", ["tools/lint_invariants.py"]))

    def test_an_event_the_original_did_not_have_and_is_not_ruled_selected_is_not_selected(self):
        self.assertFalse(decide("schedule", ["tools/lint_invariants.py"]))

    def test_an_undeterminable_diff_selects_the_job(self):
        self.assertTrue(decide("pull_request", None))

    def test_the_recorded_paths_equal_the_archived_original(self):
        self.assertEqual(sel.verify(), [])

    def test_the_cli_records_not_selected_for_an_empty_diff_and_exits_zero(self):
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        env = dict(os.environ, CATALOG_PR_BASE_SHA=head, CATALOG_PR_HEAD_SHA=head)
        done = subprocess.run([sys.executable, str(TOOL), "select", "--job", JOB, "--event", "pull_request"],
                              cwd=ROOT, env=env, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        self.assertEqual(done.stdout.strip(), "selected=false")
        self.assertIn("NOT_SELECTED", done.stderr)


class WorkflowShapeTests(unittest.TestCase):
    def setUp(self):
        text = (ROOT / ".github/workflows/repo-check.yml").read_text(encoding="utf-8")
        self.block = text[text.index("\n  " + JOB + ":"):]
        self.steps = re.split(r"^      - ", self.block, flags=re.M)[1:]

    def test_the_job_has_no_job_level_if(self):
        self.assertIsNone(re.search(r"^    if:", self.block, re.M))

    def test_every_step_after_checkout_and_selection_is_gated_on_the_selection_step(self):
        gate = "if: steps.selection.outputs.selected == 'true'"
        self.assertIn("id: selection", self.steps[1])
        for step in self.steps[2:]:
            self.assertIn(gate, step, step.splitlines()[0])
        self.assertNotIn(gate, self.steps[0] + self.steps[1])

    def test_the_canonical_workflow_and_its_ios_safe_mirror_stay_identical(self):
        self.assertEqual((ROOT / ".github/workflows/repo-check.yml").read_bytes(),
                         (ROOT / "iosnoperiod/github/workflows/repo-check.yml").read_bytes())


if __name__ == "__main__":
    unittest.main()
