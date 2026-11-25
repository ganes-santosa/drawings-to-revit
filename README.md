# drawings-to-revit

Two Claude skills that turn construction drawings (PDF) into accurate Revit 2026 models through the Revit MCP:
- `str-drawing-to-revit`: structural (setup, columns, beams, slabs, foundations, roof framing).
- `ars-to-revit`: architectural (setup, walls, floors, ceilings, roofs, door/window families and placement).

Start with `AGENTS.md` and `HANDOFF.md`.

## Layout

- `.claude/skills/str-drawing-to-revit/`, `.claude/skills/ars-to-revit/` - the skills (`SKILL.md`, `references/`, `workflows/`, `scripts/`, `assets/`)
- `shared/` - the one original of scripts and templates both skills use (schedule finder, skill checker, calibration, duplicate finder, project log and RFI templates)
- `tools/sync_shared.py` - copies `shared/` into both skills; `--check` verifies the copies and runs both skill checkers
- `samples/` - real drawing sets (git-ignored; keep client files out of the repo)
- `AGENTS.md`, `CLAUDE.md`, `HANDOFF.md` - working rules and session state

## How it works

`/str-drawing-to-revit <route> <task>` or `/ars-to-revit <route> <task>`: the route (e.g. `beams`, `roof`, `walls`, `openings`) picks the reference files to read; the rest is the task. `help` lists the routes. Each element is built in two stages: **types** (find the schedule, catalog, create, verify), then **placement** (instance table, clean, pilot one, place, audit, verify). Both skills write to one project log per project.

After any edit: `python tools/sync_shared.py --check`. Shared files are edited only in `shared/`, then `python tools/sync_shared.py`.
