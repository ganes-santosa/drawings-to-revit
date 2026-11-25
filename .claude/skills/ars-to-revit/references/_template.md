# <Element> — <one-line scope> (<OST category>)

> Legend: `[VERIFIED src]` `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` `[CONTESTED]` (SKILL.md §8). Untagged statements are not allowed for procedures.
> Last reviewed: YYYY-MM-DD · Revit tested: <none yet | 2026 …>
> Order of work: `workflows/element-modeling-workflow.md` (Stage A types → gate → Stage B placement → gate). This file supplies the element-specific details.
> Hosting, joins, enclosure and heights: `building-logic.md`. Type naming, layers, materials: `types-and-materials.md`.

## 1. Scope
What this file covers and what it deliberately does not (link instead).

---

## A. Types
### A1. Where the types are on the drawings
Schedule / legend names (English + Indonesian), sheet series, other sources (sections, details, specs). `find_schedules.py --element <x>`.
### A2. What to extract per type
Table: field | notes.
### A3. Catalog notes
Element-specific reconciliation rules; type identity; naming.
### A4–A5. Make the types in Revit
Duplicate / load / build; exact parameter names; snippets with status tags.
### A6. Gate
What to read back to prove every type is correct and placeable.

---

## B. Placement
### B1. Where the positions and heights are
### B2. Instance table columns
### B2b. Clean the table before placing
### B3. Interpretation rules
### B4–B5. Revit procedure
### B5b. Audit and repair
### B6. Verification

## Field notes and failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|

## Related
