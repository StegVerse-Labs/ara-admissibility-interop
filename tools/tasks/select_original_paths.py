#!/usr/bin/env python3
"""Decide whether a folded workflow's ORIGINAL trigger filter would have started it.

G17 (StegVerse-org/.github#166) folded workflows into jobs of a host workflow, and the
host runs on every pull_request and push. The folded original ran only on the events
and paths recorded in tools/tasks/original_path_selection.json (copied verbatim from the
archived original under tools/tasks/folded/). This tool computes that selection for one
job so the job can always run and end in success: it prints SELECTED or NOT_SELECTED,
and the job gates its remaining steps on the `selected` output. No job-level `if`, so no
job is ever reported as skipped.

stdlib only. Usage:
  select_original_paths.py select --job ID --event EVENT   write `selected=true|false`
                                                           to stdout, the record to stderr
  select_original_paths.py verify                          the manifest matches its archived originals

The changed files come from CATALOG_PR_BASE_SHA/CATALOG_PR_HEAD_SHA (pull_request) or
CATALOG_EVENT_BEFORE/CATALOG_EVENT_AFTER (push). When the diff cannot be determined the
job is SELECTED (fail toward running the check), and the record says so.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tools/tasks/original_path_selection.json"


def glob_regex(pattern):
    """GitHub Actions path-filter glob: * (no /), ** (any), ? and + (apply to the previous char), [set]."""
    out, i = [], 0
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
            continue
        if pattern.startswith("**", i):
            out.append(".*")
            i += 2
            continue
        if c == "*":
            out.append("[^/]*")
        elif c in "?+":
            out.append(c)
        elif c == "[":
            j = pattern.find("]", i + 1)
            if j == -1:
                out.append(re.escape(c))
            else:
                out.append(pattern[i:j + 1])
                i = j
        else:
            out.append(re.escape(c))
        i += 1
    return re.compile("^" + "".join(out) + "$")


def path_matches(patterns, path):
    """Ordered include/exclude semantics of `paths`: a later `!` pattern removes an earlier match."""
    hit = False
    for pattern in patterns:
        if pattern.startswith("!"):
            if glob_regex(pattern[1:]).match(path):
                hit = False
        elif glob_regex(pattern).match(path):
            hit = True
    return hit


def filter_selects(filt, files):
    """True when the original workflow's own paths / paths-ignore filter would have started it."""
    if files is None or not filt:
        return True
    if "paths" in filt:
        return any(path_matches(filt["paths"], f) for f in files)
    if "paths_ignore" in filt:
        return any(not any(glob_regex(pat).match(f) for pat in filt["paths_ignore"]) for f in files)
    return True


def changed_files(event, env=None):
    """Files this event changed, or None when it cannot be determined."""
    env = os.environ if env is None else env
    if event == "push":
        before, after = env.get("CATALOG_EVENT_BEFORE", ""), env.get("CATALOG_EVENT_AFTER", "")
        if not before or set(before) == {"0"} or not after:
            return None
        spec = [before, after]
    elif event == "pull_request":
        base, head = env.get("CATALOG_PR_BASE_SHA", ""), env.get("CATALOG_PR_HEAD_SHA", "")
        if not base or not head:
            return None
        spec = [base + "..." + head]
    else:
        return None
    try:
        out = subprocess.run(["git", "diff", "--name-only", *spec], cwd=ROOT, check=True,
                             capture_output=True, text=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return [line for line in out.splitlines() if line]


def job_filter(entry, event):
    """The paths that select this job: the original's paths plus the host workflow that now carries the job text."""
    return {"paths": list(entry["original_paths"].get(event, [])) + list(entry.get("host_paths", []))}


def decide(manifest, job, event, files):
    """(selected, reason) for one job on one event with the given changed files."""
    entry = manifest["jobs"][job]
    original_events = entry["original_events"]
    if event in entry.get("always_selected_events", []):
        return True, f"{event} stays selected by ruling: {entry.get('always_selected_reason', 'no reason recorded')}"
    if event not in original_events:
        return False, f"the original workflow did not trigger on {event} (it ran on: {', '.join(original_events)})"
    if files is None:
        return True, "the changed files could not be determined; selecting the check (fail toward running it)"
    if filter_selects(job_filter(entry, event), files):
        return True, f"a changed file matches the original {event} paths ({len(files)} changed)"
    return False, f"no changed file matches the original {event} paths ({len(files)} changed)"


def load():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def workflow_filters(text):
    """Parse the `on:` paths of an archived original without PyYAML: {event: [paths]}."""
    events, current, in_paths, in_on = {}, None, False, False
    for line in text.splitlines():
        if re.match(r"^on:\s*$", line):
            in_on = True
            continue
        if in_on and re.match(r"^\S", line):
            break
        if not in_on:
            continue
        m = re.match(r"^  (\w+):\s*$", line)
        if m:
            current, in_paths = m.group(1), False
            events.setdefault(current, [])
            continue
        if re.match(r"^  \w+:", line):
            current, in_paths = None, False
            continue
        if current and re.match(r"^    paths:\s*$", line):
            in_paths = True
            continue
        if current and re.match(r"^    \S", line):
            in_paths = False
            continue
        m = re.match(r"^      - '?(.*?)'?\s*$", line)
        if current and in_paths and m:
            events[current].append(m.group(1))
    return events


def verify():
    problems = []
    manifest = load()
    for job, entry in manifest["jobs"].items():
        record = ROOT / entry["record"]
        if not record.is_file():
            problems.append(f"{job}: missing archived original {entry['record']}")
            continue
        parsed = workflow_filters(record.read_text(encoding="utf-8"))
        for ev in entry["original_events"]:
            if parsed.get(ev) != entry["original_paths"].get(ev):
                problems.append(f"{job}: {ev} paths differ from the archived original {entry['record']}")
        extra = sorted(set(parsed) - set(entry["original_events"]) - {"workflow_dispatch"})
        if extra:
            problems.append(f"{job}: the archived original also triggers on {extra}")
        if entry["own_workflow_path"] not in entry["original_paths"].get("pull_request", []):
            problems.append(f"{job}: own workflow path {entry['own_workflow_path']} is not in the original paths")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select")
    s.add_argument("--job", required=True)
    s.add_argument("--event", required=True)
    sub.add_parser("verify")
    args = ap.parse_args(argv)
    if args.cmd == "verify":
        problems = verify()
        for p in problems:
            print("DENY " + p)
        print("ORIGINAL_PATH_SELECTION " + ("DENY" if problems else "ALLOW"))
        return 1 if problems else 0
    manifest = load()
    if args.job not in manifest["jobs"]:
        print("FAIL_CLOSED UNKNOWN_JOB " + args.job, file=sys.stderr)
        return 1
    files = changed_files(args.event)
    selected, reason = decide(manifest, args.job, args.event, files)
    print(f"{'SELECTED' if selected else 'NOT_SELECTED'} job={args.job} event={args.event}: {reason}", file=sys.stderr)
    print("selected=" + ("true" if selected else "false"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
