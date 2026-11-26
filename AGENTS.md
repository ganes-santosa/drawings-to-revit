# AGENTS.md — rules for any AI working in this repo

## What this repo is
This repo develops **two Claude skills** that turn construction drawings into an accurate Autodesk Revit 2026 model through the Revit MCP server:
- **`str-drawing-to-revit`** (`.claude/skills/str-drawing-to-revit/`): structural drawings → structural model.
- **`ars-to-revit`** (`.claude/skills/ars-to-revit/`): architectural drawings → architectural model. Moved in from the `ars-to-revit` repo on 2026-11-25 (commit 6dc17fe there).

They stay two skills (clear triggers, small rule sets) but share scripts and templates through `shared/`. The user is not a programmer: explain in plain language, keep answers short, ask when a decision is theirs.

Read `HANDOFF.md` first (where we left off), then the `SKILL.md` of the skill you are working on.

## Current focus (do not widen without being asked)
- **STR:** setup (units, levels, grids), columns, beams, slabs, foundations, roof (`roof`, alias `framing`). Walls, stairs, reinforcement, connections and views were removed to stay focused (recoverable from git tag `v1.1.0`).
- **ARS:** setup, walls, floors, ceilings, roofs, door/window families (`openings-create`), door/window placement (`openings-place`). Parked: rooms/finish schedules, stairs, railings, curtain walls, facade cladding, canopies, site, furniture, MEP, interior detailing, sheets/tags.

## Shared files (one original, two copies)
- Originals live in `shared/` (same relative paths as inside a skill, e.g. `shared/scripts/find_schedules.py`). Each skill keeps a copy because an installed skill can only rely on files in its own folder. Copies start with a `SHARED COPY - do not edit here` line.
- **Edit only the original in `shared/`**, then run `python tools/sync_shared.py`. Never edit a copy inside a skill.
- Shared today: `scripts/find_schedules.py` (`--discipline str|ars`, default from the skill folder), `scripts/check_skill.py`, `scripts/pdf_calibrate.py`, `scripts/revit/find_duplicates.cs`, `assets/examples/rfi-log-template.md`, `assets/examples/project-log-template.md` (one log per project for both disciplines).
- To share another file: move it to `shared/<path>`, delete the skill copies, run the sync. A file belongs in `shared/` only when both skills use it unchanged; discipline knowledge stays in its skill.

## Working rules
1. **Develop locally.** GitHub is a backup. **Never push, tag, or move tags unless the user says so.** Commit only when the user says so. Never force-push or rewrite published history.
2. **Never commit `samples/`** (the user's real drawing sets, 6 GB, git-ignored) or `.rfa/.rvt/.dwg/.pdf/.rte/.rft` files.
3. **Revit:** do not call the Revit MCP unless the user says a model is ready for this work, and never test on a model other agents or people are working on (user rule, 2026-11-24). Never use `say_hello` as a connection test: its modal dialog blocks the API (2026-11-24); use the read-only probe in `references/revit-api-and-automation.md` §3 or `get_current_view_info`.
4. **Do not claim a Revit procedure works until it has been run and inspected.** Status tags: `[VERIFIED]` (run here), `[VERIFIED RSUD]` / `[EXPERIMENTAL RSUD]` (STR: RSUD Cakung model, field reports in `assets/field-reports/`), `[IMPORTED KPwBI]` / `[IMPORTED KPwBI-ARS]` (earlier projects, not re-run), `[IMPORTED STR]` / `[IMPORTED ARS]` (from the sister skill), `[THEORY]`, `[EXPERIMENTAL]`, `[LIMIT]`, `[OPEN]`, `[CONTESTED]`. Promote a tag only with evidence; record it in the matching reference file, `references/lessons-learned.md`, and `DEVLOG.md` of that skill.
5. **Integrity:** never invent dimensions, never resolve drawing conflicts silently, flag guesses `LOW CONFIDENCE`. STR: **nothing floats** (every member sits on a support). ARS: architecture vs structure differences are asked, never ranked. **The drawings decide, not the habit** (both skills, user rule 2026-11-25): write every convention learned on a project as a default for when the drawings are silent, name the project it came from, and never as a rule that overrides what is drawn. Full rules: each `SKILL.md` §3.
6. **Core element procedure (both skills):** types first (find schedule → catalog → create → verify), then placement (instance table with supports/hosts → clean the table → pilot one → place → audit and repair → verify). Each skill's `workflows/element-modeling-workflow.md`.
7. Keep each `SKILL.md` short (under ~160 lines); put detail in `references/`. Do not duplicate content across files. Adding a route = one reference file + one routing row.
8. **After any change:** `python tools/sync_shared.py --check` must print OK (shared copies identical, both skill checkers pass). Then add a dated line to the skill's `DEVLOG.md` (and `lessons-learned.md` for tested lessons).
9. Develop references through real tasks on the drawings, not theory.
10. Update `HANDOFF.md` at the end of every working session.
11. Commit messages end with the co-author line given by the session's attribution reminder. Git identity is set per repo (author `bimpc004`); do not change global git config.

## Project decisions
- **One project log per project, shared by both skills:** `<drawing set folder>\_log\project-log.md` (samples: `samples\<project>\_log\`). Setup (units, levels, grids, coordinates) is done once; the second skill reuses it.
- STR: beam segmentation (and slab/column segmentation, roof scope) is chosen per project at setup and recorded in the log; never assume (`str-drawing-to-revit/references/project-setup.md` §3 step 5b).
- ARS: exterior-first and finish modelling choices are per project (ask when the first task needs them).

## Environment (checked 2026-11-20 / 2026-11-24)
- Windows 11, Revit 2026 (26.5.10.38) with the MCP add-in; tools `mcp__mcp-server-for-revit__*` fail with "connect to revit client failed" until Revit is open with the add-in running.
- Python with PyMuPDF (`import pymupdf`); pdfplumber not installed (needed by `pdf_calibrate.py`); `pdftoppm` not on PATH (render with PyMuPDF).
- Revit family templates: full Revit 2026 set (incl. `Metric Window.rft`, `Metric Door.rft`) in `D:\ProgramData\Autodesk\RVT 2026\Family Templates\English\` (found 2026-11-25); structural ones also in `C:\ProgramData\Autodesk\Revit Steel Connections 2026\en-UK\Family Templates\`. Family folder: `families\` in the repo (git-ignored).
- The working directory sometimes jumps into a skill folder: use absolute paths. Python edits with backslashes in strings can mangle paths (`\a` became a bell character once): check with grep after editing.

## Layout
```
.claude/skills/str-drawing-to-revit/   structural skill (SKILL.md, DEVLOG.md, references/, workflows/, scripts/, assets/)
.claude/skills/ars-to-revit/           architectural skill (same layout)
  assets/legacy/ (in each skill)       verbatim copies of the original KPwBI skills: evidence trail
shared/                                originals of the shared scripts and templates (edit here)
tools/sync_shared.py                   copies shared/ into both skills; --check verifies and runs both checkers
samples/                               user's drawing sets (git-ignored); project logs in samples/<project>/_log/
AGENTS.md, CLAUDE.md, HANDOFF.md       this file, pointer, session state
```
