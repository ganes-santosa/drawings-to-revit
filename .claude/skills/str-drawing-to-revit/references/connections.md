# Connections — steel and concrete connections

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: none. Content `[THEORY]` / `[OPEN]`.

## 1. Purpose and scope
Representing documented connections (base plates, gusset plates, bolted/welded joints, cast-in plates). Connection design is out of scope.

## 2. Drawing conventions
Detail bubbles on framing plans, connection detail sheets, weld/bolt symbols, plate schedules.

## 3. Required inputs
Plate sizes/thickness, bolt count/diameter, weld types, member ends joined, location.

## 4. Interpretation method
Map each connection detail to the members it applies to; count instances from plans.

## 5. Revit procedure `[THEORY]`
Structural Connections category (`OST_StructConnections`) via Steel Connections for Revit tools where installed (`StructuralConnectionHandler`), or plate/bolt families, or DirectShape plates when out of scope. Probe availability first; document what level of detail the project expects (LOD) — ask.

## 6. Verification
Instance counts vs plan callouts; no connection hosts missing.

## 7. Failure cases
`[OPEN]`

## 8. Related
`structural-framing.md`, `reinforcement.md`.
