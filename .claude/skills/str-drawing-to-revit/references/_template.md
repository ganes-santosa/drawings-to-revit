# <Element> — <one-line scope> (<OST category>)

> Legend: `[VERIFIED src]` `[IMPORTED src]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` `[CONTESTED]` (defined in SKILL.md §8). Untagged statements are not allowed for procedures.
> Last reviewed: YYYY-MM-DD · Revit tested: <none yet | 2026 …>
> Order of work: `workflows/element-modeling-workflow.md` (Stage A types → gate → Stage B placement → gate). This file supplies the element-specific details for each step.
> Support and connectivity rules (nothing floats): `building-logic.md`.

## 1. Scope
What this file covers and what it deliberately does not (link instead).

---

## A. Types
### A1. Where the types are on the drawings
Schedule names (English + Indonesian), where they usually sit, other sources (plan tags, details). `find_schedules.py --element <x>`.
### A2. What to extract per type
Table: field | notes (mark, level range, dimensions, material, other properties, source).
### A3. Catalog notes
Element-specific reconciliation rules; type identity; naming.
### A4–A5. Make the types in Revit
Family choice, duplication with exact parameter names, loading, building from template, materials. Code snippets with status tags.
### A6. Gate
What to read back to prove every type is correct and placeable.

---

## B. Placement
### B1. Where the positions and heights are
### B2. Instance table columns
### B3. Interpretation rules
### B4–B5. Revit procedure
Snippets, justification/orientation, marks/comments, order (supports first), MCP alternatives and their limits.
### B6. Verification
Programmatic checks and tolerances.

## Field notes and failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|

## Related
