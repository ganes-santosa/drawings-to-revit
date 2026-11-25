# Element modelling workflow — the core procedure (walls, floors, ceilings, roofs, doors/windows)

Every element route follows three stages, in order. **Do not place until Stage A has passed its gate.** The element reference supplies the details for each step; this file is the order and the gates. Doors and windows split the stages over two files: Stage A = `references/openings-families.md`, Stage B = `references/openings-placement.md`.

```
Stage 0  Scope and prerequisites
Stage A  TYPES      find the schedule → extract → reconcile and catalogue → map to Revit → create → verify (gate)
Stage B  PLACEMENT  find the layout → instance table with hosts → clean the table → pilot one → place once → audit and repair → verify (gate)
Stage C  CLOSE-OUT  log, learn, report
```

## Stage 0 — Scope and prerequisites
1. Scope from the task text: element, levels, zones, codes. Sheet status (existing / demolition / new).
2. **Right model:** the user has named the Revit model for this work; `document.Title` matches (`references/project-setup.md` §2). Levels, grids, units and the conversion exist (else `setup`). Never `say_hello`; use the read-only probe.
3. Hosts exist: walls before doors/windows; walls before floors and ceilings.
4. Read the element reference and `references/building-logic.md`.

## Stage A — Types
### A1. Find the type source
`python ${CLAUDE_SKILL_DIR}/scripts/find_schedules.py <folder|pdf> --element <openings|walls|finishes|ceilings|floors|roofs>`; `--sheets` for the sheet map. Open the top candidates visually (render 200–300 dpi) and confirm. Outlined text is common (sizes inside KPwBI schedules; whole RSUD/Hunver sets): read visually. Nothing found or several candidates → ask the user to point to the sheet. No schedule → types from plan tags, sections, details; record that. Latest revision; conflicts logged.
### A2. Extract every type
Fields per element: reference §A2. Read digits at 300 dpi; re-read any you are unsure of.
### A3. Reconcile and catalogue
1. Codes on plans/keyplans vs codes in the schedule: list both mismatch directions.
2. Cross-check schedule vs sections/details/elevations; never resolve silently.
3. Type identity: one Revit type per code (openings) or per unique build-up (walls/floors/ceilings/roofs), named per `references/types-and-materials.md` §5.
4. Write the catalog (`assets/examples/type-catalog-template.csv`, saved with the project log).
### A4. Map to what Revit has
`get_available_family_types` / collector per category; status per row: `exists` / `duplicate` / `load` / `new family` / `blocked`. No silent "close enough" substitutions.
### A5. Create
Order: exists → duplicate → load → new family → DirectShape (ask). One concern per call (create, then set, then use); try/catch per type; return `name | id | result`.
### A6. Gate
Read every type back (parameters, not names) against the catalog; placeable; unique Type Marks; persistence in a later call. Report the table. **Stop here** until it passes or the user accepts the exceptions.

## Stage B — Placement
### B1. Layout drawings
Plans per level + sections/elevations for heights; calibrate each sheet on its own grid; check against a known element.
### B2. Instance table
One row per instance with its **host/support** (`references/building-logic.md` §3), position, level, heights, source, provenance. Element columns: reference §B2.
### B2b. Clean the table (required)
De-duplicate; merge collinear walls; snap ends/hosts; clamp inserts inside wall length; overlap check; counts vs schedule. Reference §B2b.
### B3. Cross-check
Every instance's type passed A6; every host filled; heights follow the chain (`building-logic.md` §4). Unresolved → log and ask.
### B4. Pilot one
Place one typical instance; read back in a **later call**: exists, location, level, offsets, type, facing/cut. Fix the method until exact.
### B5. Place once
One level per call; scripts ≲ 4k characters; hosts before inserts; Mark + Comments on every element; try/catch per instance; return `mark | id | result`.
### B5b. Audit and repair (required)
Run the element audit (reference §B5b); repair only what it lists; fix the class, not the instance.
### B6. Gate
`references/model-validation.md` checks for this element; warnings delta; counts vs schedule. Model errors fixed; drawing discrepancies reported, not "fixed".

## Stage C — Close-out
Log (final catalog, counts, assumptions, conflicts, not modelled + why) · Learn (reference + `lessons-learned.md` + `troubleshooting.md`) · Report (SKILL.md §7) + "please save the Revit model".
