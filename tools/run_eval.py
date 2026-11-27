#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eval harness for the test cases in tests/cases/*.json.

Modes:
  python tools/run_eval.py --check
      Validate every case file (schema + counts). Runnable in CI, deterministic.

  python tools/run_eval.py --skeleton [skill]
      Print a per-host result template (markdown) for a human/agent to fill in
      after running the cases in a real host session. Record results as
      results/<host>/<skill>.md. NO scores are invented: the template ships
      with empty fields.

Activation protocol (per official spec guidance): present the host's skill
catalog (name+description of ALL skills) plus one test prompt to a FRESH
session with no other context; record which skill the host activates.
3 runs per prompt; activation rate = hits/3.
"""
import glob
import json
import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower().replace('-', '') != 'utf8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

REQ_ACT = {"prompt", "expect"}
REQ_EFF = {"task", "rubric"}


def load_cases():
    out = {}
    for p in sorted(glob.glob(os.path.join("tests", "cases", "*.json"))):
        skill = os.path.basename(p)[:-5]
        out[skill] = json.load(open(p, encoding="utf-8"))
    return out


def check():
    bad = 0
    for skill, c in load_cases().items():
        errs = []
        acts = c.get("activation", [])
        effs = c.get("effectiveness", [])
        if len(acts) < 3:
            errs.append("activation cases <3")
        if not any(a.get("expect", "").startswith("no-activate") for a in acts):
            errs.append("missing negative/decoy case")
        for a in acts:
            if not REQ_ACT.issubset(a):
                errs.append("activation case missing keys: %r" % a)
        for e in effs:
            if not REQ_EFF.issubset(e) or len(e["rubric"]) < 3:
                errs.append("effectiveness case weak: %s" % e.get("task", "?")[:40])
        status = "PASS" if not errs else "FAIL"
        print("%s %-36s act=%d eff=%d" % (status, skill, len(acts), len(effs)))
        for x in errs:
            print("     - %s" % x)
            bad += 1
    print("---- case suite %s (%d issue(s)), %d skills" %
          ("VALID" if bad == 0 else "INVALID", bad, len(load_cases())))
    return 0 if bad == 0 else 1


def skeleton(only=None):
    for skill, c in load_cases().items():
        if only and skill != only:
            continue
        print("\n### %s\n" % skill)
        print("| # | prompt | expected | run1 | run2 | run3 | activated |\n|---|---|---|---|---|---|---|")
        for i, a in enumerate(c.get("activation", []), 1):
            q = a["prompt"].replace("|", "/")[:60]
            print("| %d | %s | %s | [ ] | [ ] | [ ] | ______ |" % (i, q, a["expect"].split(" ")[0]))
        for e in c.get("effectiveness", []):
            print("\nTask: %s\n" % e["task"])
            for r in e["rubric"]:
                print("- [ ] %s" % r)
        print("\nhost: ______  model: ______  date: ______  runs by: ______")


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "--check":
        return check()
    if sys.argv[1] == "--skeleton":
        skeleton(sys.argv[2] if len(sys.argv) > 2 else None)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
