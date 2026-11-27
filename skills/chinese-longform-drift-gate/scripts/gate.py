#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Two-layer drift gate for long-form Chinese writing.

Usage:
    python gate.py <file.md> [--names 书名1,书名2] [--max-short 5.0]

Mechanical checks (human audit still required for what scripts cannot catch):
  CJK char count, Latin-letter intrusions, "——不" self-correction tic,
  book-title self-reference, short-sentence (<=6 CJK) ratio.
Exit 0 if all mechanical gates pass, 1 otherwise. Output is concise.
"""
import argparse
import re
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--names", default="", help="comma-separated book titles to flag as self-reference")
    ap.add_argument("--max-short", type=float, default=5.0, help="max allowed %% of <=6-CJK sentences")
    a = ap.parse_args()
    try:
        t = open(a.file, encoding="utf-8").read()
    except OSError as e:
        print("FAIL read: %s" % e)
        return 1
    cjk = len(re.findall(r"[\u4e00-\u9fff]", t))
    latin = re.findall(r"[A-Za-z]+", t)
    dash = t.count("——不")
    names = [n for n in a.names.split(",") if n.strip()]
    selfref = {n: t.count(n) for n in names}
    sents = [s for s in re.split(r"[。！？]", t) if re.search(r"[\u4e00-\u9fff]", s)]
    short = [s for s in sents if len(re.findall(r"[\u4e00-\u9fff]", s)) <= 6]
    ratio = 100.0 * len(short) / len(sents) if sents else 0.0
    chapters = len(re.findall(r"^##\s*第[一二三四五六七八九十百]+回", t, re.M))

    ok = True
    print("CJK chars      : %d" % cjk)
    print("chapters (回)  : %d" % chapters)
    print("Latin tokens   : %d %s" % (len(latin), latin[:8]))
    ok &= len(latin) == 0
    print("——不 tic       : %d" % dash)
    ok &= dash == 0
    for n, c in selfref.items():
        print("self-ref %-8s: %d" % (n, c))
    print("short<=6 ratio : %.1f%% (max %.1f%%)" % (ratio, a.max_short))
    ok &= ratio <= a.max_short
    print("MECHANICAL GATE: %s" % ("PASS" if ok else "FAIL"))
    print("NOTE: still human-audit 电报体/论断开篇/简历式起笔/穿帮预知/外→内视角 against the source text.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
