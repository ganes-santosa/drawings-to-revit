# Structural framing systems — steel frames, roof trusses, bracing, purlins, canopies

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: 2026 (KPwBI imported)
> Plain concrete/steel floor beams: `beams.md`.

## 1. Purpose and scope
Truss geometry, rafters, purlins, braces, hip/valley members, double angles, canopies.

## 2. Drawing conventions
Roof framing plan with profile-letter tables (A…E), truss elevations/sections, connection details. Check end-on members in sections. Heights often come from architectural elevation/section.

## 3. Required inputs
Support heights, ridge/eave heights, panel points, chord centreline levels, diagonal pattern (Pratt etc.), profile per member letter, purlin sections and orientation.

## 4. Interpretation method
Keep the truss geometry record in the project log: support y, ridge, heel z, chord centreline z, panel points, diagonal direction, sizes per member type `[VERIFIED KPwBI]`. Read the profile letter on every member including extensions `[VERIFIED KPwBI]`.

## 5. Revit procedure
1. Use steel families where they exist (wide-flange beam, UC-based column) `[VERIFIED KPwBI]`.
2. Missing size: `FamilySymbol.Duplicate(name)` then set h, b, t, s, r in a **separate** call `[VERIFIED KPwBI]`.
3. **No angle or CNP family existed**: double angles and purlins as DirectShape in Structural Framing, via `GeometryCreationUtilities.CreateExtrusionGeometry` with I, 2L (12 mm gusset gap) or 12-point CNP profile `[VERIFIED KPwBI]`. CNP150x65x20x3.2: web on rafter top, flanges up, lips in, web centre 46 mm outboard at eave tips.
4. Sloped members: Beam structural type, not Brace `[VERIFIED KPwBI]`.
5. If substituting nearest family size: LOW CONFIDENCE.

## 6. Verification
Member counts per letter vs plan; chord/ridge heights; no members at end-on-misread heights; thin outline members (eave-tip purlins) not missed.

## 7. Failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| Hip extensions wrong profile | Assumed D | Read letter (A) | [VERIFIED KPwBI] |
| Eave-tip purlins missing | Thin outer lines overlooked | Model them; ask what a user circle means | [VERIFIED KPwBI] |

## 8. Related
`beams.md`, `connections.md`, `revit-families.md`.
