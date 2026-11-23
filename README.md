# str-to-revit

One Claude skill, `str-drawing-to-revit`: structural construction drawings (PDF) -> accurate Revit 2026 structural model.
Focus: setup (units, levels, grids), columns, beams, slabs, foundations, roof. Start with `AGENTS.md` and `HANDOFF.md`.

## Layout

- `.claude/skills/str-drawing-to-revit/` - the skill (`SKILL.md`, `references/`, `workflows/`, `scripts/`, `assets/`)
- `samples/` - real drawing sets (git-ignored; keep client files out of the repo)
- `AGENTS.md`, `CLAUDE.md`, `HANDOFF.md` - working rules and session state

## How it works

`/str-drawing-to-revit <route> <task>`: the route (e.g. `columns`, `beams`, `slabs`) picks the reference files to read; the rest is the task. Each element is built in two stages: **types** (find the schedule, catalog, create, verify), then **placement** (instance table with supports, pilot one, batch, verify).
