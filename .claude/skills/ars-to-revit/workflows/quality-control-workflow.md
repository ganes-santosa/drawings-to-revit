# Quality-control workflow (route: `review`)

1. **Scope:** one element group / level (after each group) or the whole model (final audit, "check everything once more").
2. **Run the checks** in `references/model-validation.md` §2 that apply: always 1 (persistence), 2 (warnings delta), 12 (marks), 13 (LOW list); plus 3–4 for doors/windows, 6 for walls, 7 for floors/ceilings, 8 for roofs, 9–11 and 14 for the final audit. Read-only scripts, separate from any modelling call.
3. **Classify findings:** model error (fix: the whole class, every level) · drawing discrepancy (report with sources, ask) · accepted exception (list).
4. **Re-run** the failed checks after repairs.
5. **Report:** SKILL.md §7 with the check table (check | result | count) and the LOW CONFIDENCE list.
