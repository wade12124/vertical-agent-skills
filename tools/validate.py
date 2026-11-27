#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spec conformance validator for the Agent Skills open standard.

Usage:
    python tools/validate.py [skills_root]        # default: ./skills

Checks per skill directory:
  1. SKILL.md exists with YAML frontmatter delimited by --- lines.
  2. `name` present: lowercase letters/digits/hyphens, <=64 chars, equals directory name.
  3. `description` present, flattened length <=1024 chars (folded '>' scalars unfolded).
  4. Body <=500 lines (progressive-disclosure guidance).
  5. references/<file> and scripts/<file> mentioned in SKILL.md actually exist.
  6. Every .py under the skill compiles (AST); non-UTF8 files are flagged.
  7. Secret/PII tripwires: private keys, token-looking assignments, absolute user paths
     (C:\\Users\\..., drive-letter paths) are flagged.

Exit 0 = all pass. Output is a per-skill PASS/FAIL table plus issue lines.
"""
import ast
import os
import re
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower().replace('-', '') != 'utf8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TRIPWIRE = re.compile(
    r"(BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY"
    r"|(api[_-]?key|access[_-]?token|secret|password|passwd)\s*[:=]\s*['\"][^'\"]{12,}['\"]"
    r"|[A-Za-z]:[\\/](Users|home)[\\/])", re.I)
REF_RE = re.compile(r"(references|scripts)/([\w.\-]+\.(?:md|json|py|sh|txt|yaml|yml|csv))")


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return None, None
    return m.group(1), m.group(2)


def get_field(fm, key):
    m = re.search(r"^%s:\s*(.+)$" % key, fm, re.M)
    if m and m.group(1).strip() not in (">", ">-", "|", "|-"):
        return m.group(1).strip()
    m = re.search(r"^%s:\s*[|>]-?\n((?:[ \t]+.*\n?)+)" % key, fm, re.M)
    if m:
        return " ".join(x.strip() for x in m.group(1).splitlines())
    return None


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "skills"
    if not os.path.isdir(root):
        print("skills root not found: %s" % root)
        return 2
    failures = 0
    for skill in sorted(os.listdir(root)):
        d = os.path.join(root, skill)
        if not os.path.isdir(d):
            continue
        issues = []
        p = os.path.join(d, "SKILL.md")
        if not os.path.exists(p):
            print("FAIL %-36s missing SKILL.md" % skill)
            failures += 1
            continue
        text = open(p, encoding="utf-8").read()
        fm, body = parse_frontmatter(text)
        if fm is None:
            issues.append("no frontmatter block")
        else:
            name = get_field(fm, "name")
            desc = get_field(fm, "description")
            if not name:
                issues.append("missing name")
            else:
                if len(name) > 64 or not NAME_RE.match(name):
                    issues.append("name invalid: %r" % name)
                if name != skill:
                    issues.append("name %r != dir %r" % (name, skill))
            if not desc:
                issues.append("missing description")
            elif len(desc) > 1024:
                issues.append("description %d > 1024" % len(desc))
        if body and body.count("\n") > 500:
            issues.append("body %d lines > 500" % body.count("\n"))
        for sub, f in REF_RE.findall(text):
            if not os.path.exists(os.path.join(d, sub, f)):
                issues.append("dangling %s/%s" % (sub, f))
        for dirpath, _, files in os.walk(d):
            for fn in files:
                fp = os.path.join(dirpath, fn)
                if fn.endswith(".py"):
                    try:
                        ast.parse(open(fp, encoding="utf-8").read())
                    except SyntaxError as e:
                        issues.append("py syntax %s: %s" % (fn, e))
                elif fn.endswith((".md", ".py", ".sh", ".json", ".txt")):
                    try:
                        t = open(fp, encoding="utf-8").read()
                    except (OSError, UnicodeDecodeError):
                        issues.append("non-utf8/unreadable %s" % fn)
                        continue
                    if TRIPWIRE.search(t):
                        issues.append("tripwire in %s" % fn)
        status = "PASS" if not issues else "FAIL"
        print("%s %-36s" % (status, skill))
        for i in issues:
            print("     - %s" % i)
            failures += 1
    print("---- %s (%d issue(s))" % ("ALL PASS" if failures == 0 else "FAILURES", failures))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
