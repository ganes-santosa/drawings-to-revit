# Building logic — load path, supports and connectivity

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: none yet. The rules are standard structural logic `[THEORY]`. The problem they solve is user-reported: beams placed by Claude did not touch each other or the columns they sit on.
> Read this before placing **any** structural member. It applies to columns, beams, slabs, foundations and roof steel.

## 1. The one rule
**Nothing floats.** Every member carries its load into another member, all the way down to the foundation:

```
roof purlins → rafters / trusses → roof beams / columns
slab → secondary beams → primary beams (girders) → columns / walls → foundations → ground
```

If a member has nothing under (or at the end of) it, one of three things is true:
1. a supporting member is **missing** from the model (not modelled yet, or missed on the drawing);
2. it is a **drawn cantilever** (deliberate, shown on the drawing);
3. the drawing was **misread** (wrong level, wrong position, wrong end point).

Never leave it silently. Decide which of the three it is, fix or flag it, and log it.

## 2. Valid supports per element

| Element | Each end / base must land on | Allowed exception |
|---|---|---|
| Primary beam (girder) | column, structural wall, or another primary beam | drawn cantilever with a back-span over a support |
| Secondary beam | a primary beam, column or wall | drawn cantilever |
| Column (base) | foundation (cap/footing), column below, transfer beam, wall | none without asking |
| Column (top) | beam, slab or roof member framing into it | top storey column ending at roof beam |
| Slab | beams or walls along its edges, or columns (flat slab) | drawn cantilever edge, void edge, joint face |
| Pile cap / footing | piles / ground, with a column or wall on top | none: a cap with nothing on it is an orphan (ask) |
| Rafter / truss | column, wall, ring beam or roof beam at both supports | drawn overhang (eave) |
| Purlin | rafters / trusses at every crossing | end overhang past the last rafter, if drawn |
| Brace | members at both ends | none |

## 3. Plan the supports before placing (support table)
Before creating anything, extend the element table from the drawing with a **supported-by** column for each end:

| Mark | Start support | End support | Notes |
|---|---|---|---|
| B1 (A/1–A/2) | column K-A/1 | column K-A/2 | |
| B5 (secondary) | girder B1 | girder B2 | |
| B9 | column K-C/3 | — (drawn cantilever 1.5 m) | CANTILEVER, back-span B8 |

Rules:
- Every end must name a support or say "drawn cantilever". An empty cell = stop and check the drawing.
- **Model supports before the members they carry:** columns → primary beams → secondary beams → slab; roof columns → rafters/trusses → purlins. That way the support already exists when the end point is computed.

## 4. Where the end points go (geometry rules)
The drawing gives the beam's **line** (its plan position). The **ends** come from the supports, not from where the drawn line happens to stop. Drafted beam lines usually stop at the column face, short of it, or with a gap for clarity.

1. **Lateral position** = from the drawing (centreline from the face pair, eccentric offsets kept exactly). Never move a beam sideways to meet a support.
2. **End point** = extend or trim the beam **along its own axis** to the support:
   - support is a column → end at the point on the beam line nearest the column's centre (inside the column footprint). Revit trims the physical beam back to the column face when the join is kept `[THEORY]`.
   - support is a girder → end on the girder's **centreline** (the location line).
   - support is a wall → end on the wall's location line.
   - drawn cantilever → end where the drawing ends it (dimensioned), Comments contains `CANTILEVER`.
3. **Elevation**: beam top = SFL of the slab it supports (beams.md). Check that the support actually reaches that height: the column top must be at or above the beam soffit; a girder's top must be at or above the secondary's soffit.
4. This is **not** "snapping to a grid". The beam stays where it is drawn; only its length is resolved to the member it frames into. If extending along the axis does not reach any support within ~1 bay, the plan read is wrong: stop and re-read.

### Joins
- Keep auto-join at column ends (clean trim at the column face).
- KPwBI disallowed joins (`StructuralFramingUtils.DisallowJoinAtEnd`) at ends **not** inside a column to stop strange notching `[IMPORTED KPwBI]`. A disallowed join does not mean a gap: the end point must still sit on the girder centreline. The member is connected geometrically even without the Revit join.

## 5. Placing members with the MCP tools
- `create_line_based_element` places a line with the coordinates you give it. It does not look for supports `[THEORY]`. Compute end points from the support table first; then run the connectivity check (§6) after every batch.
- With `send_code_to_revit`, read the support's actual location from the model (column `LocationPoint`, girder `LocationCurve`) and compute the end point from it, instead of re-typing coordinates from the drawing.

## 6. Connectivity check (run after every batch and in every review)
Script: `scripts/revit/check_connectivity.cs` (`[THEORY]` until run on a test model). Paste it into `send_code_to_revit`. It reports:
- **Beam ends** that do not touch a column, wall or other beam within tolerance (default 50 mm to columns/walls, 200 mm to another beam's centreline), excluding ends whose Comments contain `CANTILEVER`.
- **Column bases** with no foundation, column, beam or wall just below.
- Planned, not in the script yet: columns whose top is lower than a beam framing into them `[OPEN]`.

Every floating member in the report must end up as: fixed, a documented drawn cantilever, or an open question for the user. Target: 0 unexplained.

## 7. Failure cases
| Symptom | Likely cause | Fix | Status |
|---|---|---|---|
| Beam ends short of the column | End point taken from where the drawn line stops (at the face or with a drafting gap) | Extend along the axis to the column centre (§4.2) | [THEORY] (user-reported problem) |
| Secondary beam stops short of / runs past the girder | End point from the drawing instead of the girder centreline | End on the girder location line | [THEORY] (user-reported problem) |
| Beam at the right plan position but floating above/below the column | Wrong level/offset; column top lower than beam soffit | Fix level/offset; check the height chain (slab → beam → column) | [THEORY] |
| Beam placed before its girder exists | Wrong modelling order | Supports first (§3) | [THEORY] |
| Beam ends off by ~300× or far away | mm passed as feet | Convert (÷304.8) | [THEORY] |
| Cap with no column on it | Demolished structure on an "existing" plan | Ask; foundations.md | [IMPORTED KPwBI] |

## 8. Related
`beams.md`, `columns.md`, `slabs.md`, `foundations.md`, `structural-framing.md`, `model-validation.md` (#17), `troubleshooting.md`.
