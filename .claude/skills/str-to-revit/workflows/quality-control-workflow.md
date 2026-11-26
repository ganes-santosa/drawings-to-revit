# Quality control workflow (route: `review`; also Phase 4)

Run per level/group and as a full audit. "Check the entire model for anything suspicious" or "final gloss over" from the user = the full audit (all checks, all levels). Catalogue and tolerances: `references/model-validation.md`.

1. **Scope**: which levels/categories. Read the project log (conversion, conflicts, LOW CONFIDENCE list).
2. **Extract model data** programmatically: id, category, family/type, mark, comments, level, location (mm), size, bbox. Save as a table.
3. **Run checks** #1–#16 in model-validation.md. For each: result, count, offenders (ids/marks).
4. **Compare to drawings**: counts vs schedules; positions vs calibrated geometry; levels/elevations; slab outlines; foundation positions.
5. **Classify findings**: model error (fix) · drawing discrepancy (report, do not "fix") · noise within tolerance · accepted as-drawn.
6. **Fix model errors** only within the stated task scope; confirm before bulk or destructive changes; re-run the failed checks.
7. **Report**: checks run (pass/fail table), findings, discrepancies for the engineer, LOW CONFIDENCE list, remaining items.
8. **Learn**: new failure modes → `troubleshooting.md` + element file.
