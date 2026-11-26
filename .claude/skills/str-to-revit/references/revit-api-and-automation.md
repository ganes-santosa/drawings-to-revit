# Revit API and automation — probing, patterns, limits

> Legend: SKILL.md §8 · Last reviewed: 2026-11-20
> **Environment record (2026-11-20, local Windows 11 machine):** Revit 2026 installed (`C:/Program Files/Autodesk/Revit 2026`) `[VERIFIED]`; Revit was NOT running, so every `mcp-server-for-revit` call returned `connect to revit client failed` `[VERIFIED]` -> open Revit + the project and start the MCP add-in first. **Do not use `say_hello` to test the connection:** it opens a modal dialog and the call timed out while it waited (architecture skill, 2026-11-24) `[IMPORTED ARS]`; use the read-only probe (§3) or `get_current_view_info`. MCP tool names here are `mcp__mcp-server-for-revit__<tool>` (not the `remote-devices` prefix used in KPwBI). Local tools: `python`/`py`, `pdftotext` present; `pdftoppm` not on PATH; pdfplumber/PyMuPDF not yet checked `[VERIFIED]`. Dynamo/pyRevit not probed `[OPEN]`. All Revit API items below are `[THEORY]` or `[IMPORTED KPwBI]` until run via `assets/examples/live-test-plan.md`.

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

### Bridge behaviour confirmed on RSUD Cakung `[VERIFIED RSUD, Revit 2026]`
- **Any modal warning dialog freezes the API and looks exactly like a timeout**, not only the floor-overlap one: also "There are identical instances in the same place" (duplicate placement) and "Can't keep elements joined" (merging/trimming joined beams). The next call times out too. Ask the user to dismiss it (**Unjoin / OK, never Delete**), then **count what committed before retrying**: the change usually did commit.
- A timed-out script's result can come back as the reply to the *next* call. Do not trust a reply that does not match the script just sent.
- **Speed:** copy element data (end points, widths) into plain arrays, do the maths, write only changed elements. Nested loops of API calls time out; the array method handled 700 × 700 beams and four floors in one call in under a second.
- Do not touch elements after deleting them in the same script (`InvalidObject`): collect, delete, then edit.
- `out` is a C# keyword: not usable as a variable name.
- LINQ (`.Any(...)`) worked in the host on RSUD.
- Moving/trimming via `((LocationCurve)el.Location).Curve = Line.CreateBound(a, b)` works at scale, **but resets the beam's `STRUCTURAL_BEAM_END0/1_ELEVATION` to 0**: read the offsets first and write them back.

### Bridge behaviour confirmed on RSUD roofs and voids (2026-11-25) `[VERIFIED RSUD, Revit 2026]`
- Modal warnings that also block the API: "Highlighted floors overlap", **moving or changing a model group**. After a timeout: user closes the dialog, then re-query what committed (32 of 32 rods existed after one "timeout").
- Avoid overlap warnings by construction: a new slab's outline never overlaps a neighbour, even briefly; or delete the old one first in the same call.
- The MCP template always has a transaction open: `document.IsModifiable == true`, so `SketchEditScope` cannot start (no script edits of slab sketches). `Document.HasOpenTransaction` does not exist.
- Compile quirks in Revit 2026: `ElementId.Value` (long) works, `IntegerValue` fails; `new ElementId(long)`; only `double[]` literals are safe; `Element` has no `SketchId`, cast to `Floor` first.
- `File.WriteAllText` to the project folder works for exports (void outlines).
- Deleting an element and reusing it in the same script throws: split into two calls and re-query by Mark.
- `StructuralType.Brace` lets Revit re-attach member ends (moved up to 15 m); place all steel as Beam (`roof-framing.md` B4–B5).

### Bridge behaviour confirmed on RSUD slabs (2026-11-24) `[VERIFIED RSUD, Revit 2026]`
- **One level per call** for heavy rebuilds: several levels in one call raised "insufficient memory" and rolled back everything.
- After an exception, edits made **before** the error stayed committed (seen after an InvalidObject from iterating a cached list after `Delete`). Delete last or re-collect, then read back what committed.
- An exception in the **reporting** part of a script (e.g. reading warnings) rolled back the whole call, modelling included. Keep reporting in a separate read-only call.
- Computed values such as `HOST_AREA_COMPUTED` read 0 until `document.Regenerate()`.
- **File hand-off:** Python writes geometry to a text file, C# reads it with `File.ReadAllLines`. Keeps each script under ~4 kB whatever the element count.
- Hosted floor openings raised the modal "There is a circular chain of references"; shaft openings (`NewOpening(baseLevel, topLevel, CurveArray)`) did not.

## 5. Patterns
- Small scripts; one concern each; return structured text (id | mark | result).
- Read-back after every write. Report counts.
- Batch size: tens to low hundreds of elements per call; tune after measuring.
- Keep reusable scripts under `assets/examples/scripts/` once **verified**; header comment: Revit version, date, what was verified.
- Units: API lengths in feet (mm/304.8).
- **Re-runnable placement** `[THEORY]`: a batch must be safe to run twice. Read the Marks already in the model and skip those rows, so a retry after a timeout or modal dialog (where part of the batch usually committed) places only what is missing:
  ```csharp
  var have = new HashSet<string>(new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFraming)
      .WhereElementIsNotElementType().Select(e => e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() ?? ""));
  // per row: if (have.Contains(mark)) { sb.AppendLine(mark + "|skip, exists"); continue; }
  ```
  Requires a unique Mark on every row before placing (planning gate). Check with `scripts/revit/find_duplicates.cs` after any retry.

## 6. Untested capabilities to probe (backlog)
`Floor.Create` signature on the installed version; view creation (`ViewPlan.Create`, `View3D.CreateIsometric`); schedule creation (`ViewSchedule.CreateSchedule`); `document.GetWarnings()`; DWG/PDF underlay import via `ImportInstance`/`Document.Link` — see live-test plan.

## 7. Failure cases
See `troubleshooting.md` (rows tagged "API").

## 8. Related
`model-validation.md`, `revit-families.md`, `assets/examples/live-test-plan.md`.
