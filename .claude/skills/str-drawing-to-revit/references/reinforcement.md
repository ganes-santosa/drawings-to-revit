# Reinforcement — rebar modelling

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20 · Revit tested: none. Not part of KPwBI. Content `[THEORY]` / `[OPEN]`.

## 1. Purpose and scope
Modelling documented reinforcement only where tools and drawings support it. Detailing/design excluded.

## 2. Drawing conventions
Bar marks, diameter, spacing (`Ø16-150`), cover notes, section cuts, bar bending schedules, typical details ("TYP. UNO").

## 3. Required inputs
Host element, bar mark/diameter/spacing/length/shape, cover, hook/bend standards, layers.

## 4. Interpretation method
Tie each bar mark to its host and detail; reconcile spacing vs element length; note "typical" rules explicitly.

## 5. Revit procedure `[THEORY]`
`Rebar.CreateFromCurves(document, RebarStyle, RebarBarType, hookStart, hookEnd, host, normal, curves, startOrient, endOrient, useExistingShape, createNewShape)`; `SetLayoutAsFixedNumber` / `SetLayoutAsMaximumSpacing`; set `Cover` via `RebarCoverType`. Check `RebarBarType` availability first (`api` probe). Decide first whether the project requires rebar in the model at all — ask.

## 6. Verification
Bar counts and total length vs schedule; cover; host assignment.

## 7. Failure cases
`[OPEN]`

## 8. Related
`connections.md`, `foundations.md`, `columns.md`, `beams.md`.
