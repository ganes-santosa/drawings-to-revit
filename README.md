# str-to-revit

Claude skills for pipeline: structural construction drawings (PDF/DWG) -> Revit model.

## Layout

- `.claude/skills/<name>/SKILL.md` - one skill per pipeline stage (Claude Code auto-loads)
- `samples/` - test drawings (git-ignored; keep client files out of repo)

## Pipeline (draft)

1. `drawing-extract` - read sheets, pull grids, levels, member tags, schedules
2. (next) map extracted data to Revit families/types
3. (next) generate Revit API / Dynamo / pyRevit script to build model
