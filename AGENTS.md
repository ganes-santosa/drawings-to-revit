# AGENTS.md — rules for any AI working in this repo

## What this repo is
`str-to-revit` develops one Claude skill, **`str-drawing-to-revit`** (`.claude/skills/str-drawing-to-revit/`), that turns structural construction drawings into an accurate Autodesk Revit 2026 structural model through the Revit MCP server. The user is not a programmer: explain in plain language, keep answers short, ask when a decision is theirs.

Read `HANDOFF.md` first (where we left off), then `.claude/skills/str-drawing-to-revit/SKILL.md`.

## Current focus (do not widen without being asked)
Setup (units, levels, grids), **columns, beams, slabs, foundations, roof (`roof`, alias `framing`)**. Walls, stairs, reinforcement, connections and views were removed from the repo to stay focused (recoverable from git tag `v1.1.0`); do not re-add them unless asked.

## Working rules
1. **Develop locally.** GitHub is a backup. **Never push, tag, or move tags unless the user says so.** Never force-push or rewrite published history.
2. **Never commit `samples/`** (the user's real drawing sets, 6 GB, git-ignored) or `.rfa/.rvt/.dwg/.pdf` files.
3. **Do not claim a Revit procedure works until it has been run and inspected.** Status tags: `[VERIFIED]` (run here), `[VERIFIED RSUD]` / `[EXPERIMENTAL RSUD]` (run in Revit on the RSUD Cakung model, field report in `assets/field-reports/`), `[IMPORTED KPwBI]` (from the earlier project, not re-run), `[THEORY]`, `[EXPERIMENTAL]`, `[LIMIT]`, `[OPEN]`. Promote a tag only with evidence; record it in the matching reference file, `references/lessons-learned.md`, and `DEVLOG.md`.
4. **Engineering integrity:** never invent dimensions, never resolve drawing conflicts silently, flag guesses `LOW CONFIDENCE`, **nothing floats** (every member sits on a support). Full rules: `SKILL.md` §3.
5. **Core element procedure:** types first (find schedule → catalog → create → verify), then placement (instance table with supports → pilot one → batch → verify). `workflows/element-modeling-workflow.md`.
6. Keep `SKILL.md` short (under ~160 lines); put detail in `references/`. Do not duplicate content across files. Adding a route = one reference file + one routing row.
7. After any change to the skill: `python .claude/skills/str-drawing-to-revit/scripts/check_skill.py` must print OK. Then add a dated line to `DEVLOG.md` (and `lessons-learned.md` for tested lessons).
8. Update `HANDOFF.md` at the end of every working session.
9. Commit messages end with the co-author line given by the session's attribution reminder. Git identity is set per repo (author `bimpc004`); do not change global git config.

## Project decisions
Beam segmentation (and slab/column segmentation) is chosen **per project** at setup and recorded in the project log; never assume continuous or split (`references/project-setup.md` §3 step 5b).

## Environment (checked 2026-11-20)
- Windows 11, Revit 2026 installed; the Revit MCP tools (`mcp__mcp-server-for-revit__*`) fail with "connect to revit client failed" until Revit is open with the MCP add-in running. Run `say_hello` first.
- Python available (`python`); PyMuPDF installed (`import pymupdf`); pdfplumber not installed; `pdftoppm` not on PATH.
- Revit family templates: `C:\ProgramData\Autodesk\Revit Steel Connections 2026\en-UK\Family Templates\` (Metric Structural Column.rft, Metric Structural Framing - Beams and Braces.rft). The standard Revit content library was not found.

## Layout
```
.claude/skills/str-drawing-to-revit/   the skill (SKILL.md, references/, workflows/, scripts/, assets/)
assets/legacy/ (inside the skill)      verbatim copy of the original KPwBI skill: evidence trail
samples/                               user's drawing sets (git-ignored); project logs in samples/<project>/_log/
AGENTS.md, CLAUDE.md, HANDOFF.md       this file, pointer, session state
```
