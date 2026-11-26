# Drawing analysis workflow (route: `analyze`; also Phase 1)

1. **Locate inputs.** List files provided (PDF/DWG/images/IFC/schedules). Formats: PDF vector vs scanned; CAD. State what cannot be read.
2. **Sheet inventory.** Table: sheet no. | title | revision/date | scale | existing/demo/new | type | zone | page. `pdftotext -layout`, `pdfinfo`, rendered thumbnails.
3. **Scale and units.** Per view, from dimension strings or grid spacing; flag insets.
4. **Reference frame.** Grids (name, spacing), levels (FFL/SFL, datum per sheet group), joints.
5. **Calibrate** plan sheets (`scripts/pdf_calibrate.py`); log residuals.
5b. **Find the schedules** per element: `scripts/find_schedules.py <folder> --element <x>`; list the sheet/page of each table in the inventory.
6. **Extract** element data per category into tables (mark, size, location, level, source, provenance).
7. **Cross-reference** plan ↔ section ↔ detail ↔ schedule; count reconciliation against tables.
8. **Conflict/missing list.** `assets/examples/rfi-log-template.md`: ID | topic | A says | B says | impact | proposed resolution.
9. **Report**: inventory, extracted tables summary, conflicts, proposed modelling strategy and order, questions (2–3 options + recommendation).

Rules: SKILL.md §3 and §5. Do not touch Revit in this workflow except read-only probes.
