#!/usr/bin/env python3
"""Integrity check for the str-drawing-to-revit skill.

Fails if: a routing-table row in SKILL.md names a missing file, a reference/workflow
is not routed, a relative markdown link is broken, a reference lacks a status legend,
or required frontmatter is missing.  Usage: python check_skill.py
"""
import re, sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
errs = []
skill = (root / "SKILL.md").read_text(encoding="utf-8")

fm = re.match(r"---\n(.*?)\n---\n", skill, re.S)
if not fm:
    errs.append("SKILL.md: missing frontmatter")
else:
    for k in ("name:", "description:", "argument-hint:"):
        if k not in fm.group(1):
            errs.append(f"SKILL.md frontmatter missing {k}")

# routing table section
sec = skill.split("## 2. Routing table", 1)[-1].split("\n## 3.", 1)[0]
routed = set()
keywords = []
for line in sec.splitlines():
    if not line.startswith("| `"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    keywords.append(cells[0])
    for f in re.findall(r"`((?:references|workflows)/[^`]+\.md)`", cells[1]):
        routed.add(f)
        if not (root / f).exists():
            errs.append(f"route '{cells[0]}' -> missing file {f}")
if not keywords:
    errs.append("no routing rows found")

# every reference/workflow (except template) must be routed (directly or via full workflow)
full = (root / "workflows/full-modeling-workflow.md").read_text(encoding="utf-8")
for p in sorted(list((root / "references").glob("*.md")) + list((root / "workflows").glob("*.md"))):
    rel = p.relative_to(root).as_posix()
    if p.name.startswith("_"):
        continue
    if rel not in routed and rel not in full and p.name not in full:
        errs.append(f"unrouted file: {rel}")
    if rel.startswith("references/") and p.name != "lessons-learned.md":
        if "Legend" not in p.read_text(encoding="utf-8")[:600]:
            errs.append(f"{rel}: missing status legend line")

# duplicate aliases
seen = {}
for k in keywords:
    for a in re.findall(r"`([^`]+)`", k):
        if a in seen:
            errs.append(f"duplicate keyword/alias '{a}'")
        seen[a] = True

# broken relative links in all md
for p in root.rglob("*.md"):
    for m in re.finditer(r"\]\((?!http|#)([^)#]+)", p.read_text(encoding="utf-8")):
        if not (p.parent / m.group(1)).exists():
            errs.append(f"{p.relative_to(root)}: broken link {m.group(1)}")

if errs:
    print("FAIL"); [print(" -", e) for e in errs]; sys.exit(1)
print(f"OK: {len(keywords)} routes, {len(seen)} keywords/aliases, {len(routed)} routed files")
