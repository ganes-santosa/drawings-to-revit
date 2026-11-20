# Revit families and types — selection, duplication, creation

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: 2026 (KPwBI imported)

## 1. Purpose and scope
Choosing the right family/type, duplicating types for missing sizes, when to use DirectShape.

## 2. Decision order
1. Existing project type that matches exactly → use it.
2. Existing family, missing size → duplicate type and set parameters.
3. Family loadable from library (ask user for path; never assume network access).
4. No family fits → DirectShape in the correct category (state why; flag).
Steel: **use families wherever they exist** (user rule `[VERIFIED KPwBI]`); DirectShape for foundations (company convention) and for items with no family (angles, CNP).

## 3. Procedure
- Inventory first: `new FilteredElementCollector(document).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_StructuralFraming)` `[THEORY]`; list family+type names and parameters.
- Duplicate: `symbol.Duplicate("NEW NAME")` → cast to `FamilySymbol`; set parameters (b, h, t, s, r…) **in a separate call** `[VERIFIED KPwBI]` (doing create+set+swap in one script threw).
- Activate before placing: `if(!symbol.IsActive) symbol.Activate();` `[THEORY]`.
- Naming: `BEAM CONCRETE bxhmm`, steel by profile `WF350x175x7x11`.
- Concrete family flexes only one face with `b` → Y justification Center on instances (`beams.md`) `[VERIFIED KPwBI]`.
- Editing a family document (`EditFamily`) from the MCP execution context: `[LIMIT]` a transaction is always open, so family-document editing via the API was not possible in KPwBI; use type parameters/instance parameters.

## 4. Verification
Type dimensions read back equal schedule values (mm); material assigned; category correct.

## 5. Failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| Exception creating+editing a type in one call | Combined operations | Split into create / set / swap calls with try/catch | [VERIFIED KPwBI] |
| Wrong profile silently used | Nearest-size substitution | Create exact type or flag LOW CONFIDENCE | [VERIFIED KPwBI] |

## 6. Related
`beams.md`, `columns.md`, `structural-framing.md`, `revit-api-and-automation.md`.
