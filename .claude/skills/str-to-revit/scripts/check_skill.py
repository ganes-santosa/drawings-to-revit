#!/usr/bin/env python3
# SHARED COPY - do not edit here. Edit shared/scripts/check_skill.py in the repo, then run tools/sync_shared.py
"""Integrity check for a drawing-to-revit skill (the skill this file sits in).

Fails if: required frontmatter is missing, a routing-table row in SKILL.md names a missing
file, a reference/workflow is not routed, a reference lacks a status legend line, a
keyword/alias is duplicated, the argument-hint names an unknown route, a relative markdown
link is broken, or SKILL.md grows past 500 lines.  Usage: python check_skill.py
"""
import re, sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
errs = []
skill = (root / "SKILL.md").read_text(encoding="utf-8")

fm = re.match(r"---\n(.*?)\n---\n", skill, re.S)
hint = ""
if not fm:
    errs.append("SKILL.md: missing frontmatter")
else:
    for k in ("name:", "description:", "argument-hint:"):
        if k not in fm.group(1):
            errs.append(f"SKILL.md frontmatter missing {k}")
    m = re.search(r'argument-hint:\s*"\[([^\]]*)\]', fm.group(1))
    hint = m.group(1) if m else ""
if len(skill.splitlines()) > 500:
    errs.append("SKILL.md over 500 lines")

sec = skill.split("## 2. Routing table", 1)[-1].split("\n## 3.", 1)[0]
routed, keywords, seen = set(), [], {}
for line in sec.splitlines():
    if not line.startswith("| `"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    keywords.append(cells[0])
    for f in re.findall(r"`((?:references|workflows)/[^`]+\.md)`", cells[1]):
        routed.add(f)
        if not (root / f).exists():
            errs.append(f"route '{cells[0]}' -> missing file {f}")
    for a in re.findall(r"`([^`]+)`", cells[0]):
        if a in seen:
            errs.append(f"duplicate keyword/alias '{a}'")
        seen[a] = True
if not keywords:
    errs.append("no routing rows found")
for h in filter(None, hint.split("|")):
    if h not in seen:
        errs.append(f"argument-hint names unknown route '{h}'")

full_p = root / "workflows/full-modeling-workflow.md"
full = full_p.read_text(encoding="utf-8") if full_p.exists() else ""
for p in sorted(list((root / "references").glob("*.md")) + list((root / "workflows").glob("*.md"))):
    rel = p.relative_to(root).as_posix()
    if p.name.startswith("_"):
        continue
    if rel not in routed and rel not in full and p.name not in full:
        errs.append(f"unrouted file: {rel}")
    if rel.startswith("references/") and p.name != "lessons-learned.md":
        if "Legend" not in p.read_text(encoding="utf-8")[:600]:
            errs.append(f"{rel}: missing status legend line")

for p in root.rglob("*.md"):
    for m in re.finditer(r"\]\((?!http|#)([^)#]+)", p.read_text(encoding="utf-8")):
        if not (p.parent / m.group(1)).exists():
            errs.append(f"{p.relative_to(root)}: broken link {m.group(1)}")

if errs:
    print("FAIL"); [print(" -", e) for e in errs]; sys.exit(1)
print(f"OK: {len(keywords)} routes, {len(seen)} keywords/aliases, {len(routed)} routed files")
