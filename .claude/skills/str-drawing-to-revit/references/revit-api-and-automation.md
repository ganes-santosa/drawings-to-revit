# Revit API and automation — probing, patterns, limits

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20
> **Environment record (2026-11-20, local Windows 11 machine):** Revit 2026 installed (`C:/Program Files/Autodesk/Revit 2026`) `[VERIFIED]`; Revit was NOT running, so every `mcp-server-for-revit` call returned `connect to revit client failed` `[VERIFIED]` -> open Revit + the project and start the MCP add-in first (`say_hello` confirms). MCP tool names here are `mcp__mcp-server-for-revit__<tool>` (not the `remote-devices` prefix used in KPwBI). Local tools: `python`/`py`, `pdftotext` present; `pdftoppm` not on PATH; pdfplumber/PyMuPDF not yet checked `[VERIFIED]`. Dynamo/pyRevit not probed `[OPEN]`. All Revit API items below are `[THEORY]` or `[IMPORTED KPwBI]` until run via `assets/examples/live-test-plan.md`.

## 1. Purpose and scope
How to discover and use the automation environment safely; known behaviour of the MCP bridge.

## 2. Candidate mechanisms
| Mechanism | State | Notes |
|---|---|---|
| `mcp-server-for-revit` (`send_code_to_revit`, `get_selected_elements`, …) | Used in KPwBI `[IMPORTED KPwBI]` | KPwBI tool name: `mcp__remote-devices__mcp-server-for-revit__send_code_to_revit`; here: `mcp__mcp-server-for-revit__send_code_to_revit` (load schema with ToolSearch `select:<full name>` if deferred) |
| Revit API C# via MCP | Same | Code runs in `Execute` with `document` in scope and **a transaction already open** |
| Python (pyRevit / RevitPythonShell) / Dynamo | `[OPEN]` not probed | Probe if installed |
| External PDF processing (Python) | `[IMPORTED container]` (earlier Linux container; re-check locally) | Used for calibration/extraction, not Revit |

## 3. Probe procedure (run first in every new environment)
1. List available tools (ToolSearch for `revit`). Record names.
2. Run a read-only probe. `[THEORY]` standard API:
```csharp
var sb = new System.Text.StringBuilder();
sb.AppendLine("Title: " + document.Title);
sb.AppendLine("Revit: " + document.Application.VersionNumber);
sb.AppendLine("Levels: " + new FilteredElementCollector(document).OfClass(typeof(Level)).GetElementCount());
sb.AppendLine("Grids: " + new FilteredElementCollector(document).OfClass(typeof(Grid)).GetElementCount());
sb.AppendLine("BeamTypes: " + new FilteredElementCollector(document).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_StructuralFraming).GetElementCount());
return sb.ToString();
```
3. Test a trivial write + rollback behaviour (create/delete a model line) to learn transaction semantics.
4. Record results in the *Environment record* above and in `DEVLOG.md`.

## 4. Imported bridge behaviour `[IMPORTED KPwBI, Revit 2026]`
- Script runs in `Execute` with `document`; a transaction is already open; `return` a string; build reports with `StringBuilder`.
- **Keep scripts ≲ 4k characters.** A ~9k script with many local functions timed out (~80 s) three times with nothing committed; the same logic as three ~4k scripts ran in <1 s.
- Errors come back in Chinese: `执行失败: Exception has been thrown by the target of an invocation` = runtime error → wrap risky parts in try/catch and return `(ex.InnerException??ex).Message`; `代码编译错误` = compile error with a line number.
- Compiler quirks: `int[]` literals failed (use `double[]`); prefer `Func<>` lambdas over local functions.
- Some BuiltInParameters absent in 2026 (e.g. `ROOF_CURVE_OVERHANG`): guard with `?.`/try-catch or use object methods (`FootPrintRoof.get_Overhang`).
- Multi-step type work (create type + set params + swap) must be separate calls.
- Clash checks: `ElementIntersectsElementFilter`-style scripts threw; **bounding-box overlap checks were reliable**.
- `ElementTransformUtils.MoveElement` works for bulk moves.
- Rename views with `v.Name = …` inside try/catch per view (unique names).
- A hanging call may be a **modal dialog** in Revit (e.g. floor-overlap warning).
- `[LIMIT]` Editing family documents through the bridge is not possible (transaction already open).

## 5. Patterns
- Small scripts; one concern each; return structured text (id | mark | result).
- Read-back after every write. Report counts.
- Batch size: tens to low hundreds of elements per call; tune after measuring.
- Keep reusable scripts under `assets/examples/scripts/` once **verified**; header comment: Revit version, date, what was verified.
- Units: API lengths in feet (mm/304.8).

## 6. Untested capabilities to probe (backlog)
`Floor.Create` signature on the installed version; `Rebar.CreateFromCurves`; `StructuralConnectionHandler`; view creation (`ViewPlan.Create`, `View3D.CreateIsometric`); schedule creation (`ViewSchedule.CreateSchedule`); `document.GetWarnings()`; DWG/PDF underlay import via `ImportInstance`/`Document.Link` — see live-test plan.

## 7. Failure cases
See `troubleshooting.md` (rows tagged "API").

## 8. Related
`model-validation.md`, `revit-families.md`, `assets/examples/live-test-plan.md`.
