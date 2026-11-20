# Element modelling workflow (all element routes)

Precondition: levels, grids, units and conversion exist (else run `setup`). The element reference for the route has been **read**.

1. **Scope** from the task text (levels, zones, marks). Confirm what is existing/new.
2. **Extract** the element table from drawings: mark | type/size | plan position | base/top | orientation | source | provenance (`EXPLICIT/DERIVED/MEASURED/ASSUMED`). Cross-check counts with schedules. Record conflicts.
3. **Resolve types/families** (`references/revit-families.md`): existing → duplicate → DirectShape. Flag substitutions.
4. **Pilot:** place **one** element. Read back location, size, level, offsets, parameters, solid/bounding box. Compare to the drawing. Fix method until correct; if the method is new, note it for documentation.
5. **Batch** in small scripts (one level / one group). Each element gets Mark + Comments (sheet, tag, provenance, `LOW CONFIDENCE`). try/catch per element; return an id|mark|result table.
6. **Verify** the batch via the element reference's *Verification* section and `quality-control-workflow.md` (subset).
7. **Log** to the project log (counts, assumptions, conflicts, not-modelled).
8. **Learn:** if anything failed, surprised, or a new method worked → SKILL.md §8 (update reference + lessons-learned with tested evidence and status tag).
9. Report per SKILL.md §7 (short).
