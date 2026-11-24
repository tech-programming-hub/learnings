#!/usr/bin/env python3
"""Check that every practice question in this repo has an answer.

Standard library only (re = regular expressions, pathlib = file paths).
Usage:  python3 tools/validate.py
Exit code 0 = all good, 1 = problems found (handy for CI).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
Q_HEADING = re.compile(r"^### (Q\d+\.\d+)\b", re.M)      # e.g. ### Q3.14 · L3 · ...
M_HEADING = re.compile(r"^### (M\d\.\d+)\s*$", re.M)      # e.g. ### M1.07
ANSWER = re.compile(r"\*\*(Answer: [A-D](?: and [A-D])?|\d Yes|\d No)")

problems, total = [], 0
print(f"{'File':40} {'Questions':>9}")
for md in sorted(p for p in ROOT.glob("*.md") if p.name != "README.md"):
    text = md.read_text(encoding="utf-8")
    ids = Q_HEADING.findall(text)
    if ids:
        # Split the file at each question heading and check each chunk.
        chunks = Q_HEADING.split(text)[1:]          # [id, body, id, body, ...]
        for qid, body in zip(chunks[0::2], chunks[1::2]):
            if "<details>" not in body or not ANSWER.search(body):
                problems.append(f"{md.name}: {qid} has no answer block")
        if len(ids) != len(set(ids)):
            problems.append(f"{md.name}: duplicate question IDs")
    mids = M_HEADING.findall(text)
    if mids:
        key = text.split("## Answer key", 1)[-1]
        for mid in mids:
            if f"| {mid} |" not in key:
                problems.append(f"{md.name}: {mid} missing from answer key")
    count = len(ids) + len(mids)
    total += count
    if count:
        print(f"{md.name:40} {count:>9}")

print(f"{'TOTAL':40} {total:>9}")
if problems:
    print("\nProblems:")
    print("\n".join(f"  - {p}" for p in problems))
    sys.exit(1)
print("\nAll questions have answers. ✅")
