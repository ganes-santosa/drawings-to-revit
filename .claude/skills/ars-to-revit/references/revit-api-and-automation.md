# Revit API and automation — probing, the MCP bridge, limits

> Legend: `[VERIFIED src]` `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]` `[EXPERIMENTAL]` `[THEORY]` `[LIMIT]` `[OPEN]` (SKILL.md §8).
> Last reviewed: 2026-11-25

## 1. Environment record (local Windows 11 machine)
- Revit 2026 (build 26.5.10.38) with `mcp-server-for-revit`; tools named `mcp__mcp-server-for-revit__<tool>` (load schemas with ToolSearch `select:<name>`) `[VERIFIED 2026-11-24]`.
- The MCP works only while Revit is open with the add-in running; otherwise calls fail with `connect to revit client failed` `[IMPORTED STR]`.
- **`say_hello` opens a modal greeting dialog and the call timed out while it waited** (`Say hello operation timed out`) `[VERIFIED 2026-11-24]`, matching the KPwBI warning that it blocks the API `[IMPORTED KPwBI-ARS]`. **Do not use it as a connection test.** Use the read-only probe below (`get_current_view_info` also answered at once `[VERIFIED 2026-11-24]`).
- **Only probe a model the user has said is free for this work.** On 2026-11-24 the open model belonged to other agents; the user said not to work in it.
- Python + PyMuPDF installed; pdfplumber not installed `[VERIFIED 2026-11-24]`; pdftoppm not on PATH `[IMPORTED STR]` (render with PyMuPDF `page.get_pixmap(dpi=…)`).

## 2. Mechanisms
| Mechanism | Notes |
|---|---|
| `send_code_to_revit` | C# body of `Execute`, `document` in scope, **a transaction already open**, return a string `[IMPORTED KPwBI-ARS]` |
| `get_available_family_types`, `ai_element_filter`, `get_selected_elements`, `get_current_view_info` | Read-only queries; `get_selected_elements` when the user points at something |
| `create_line_based_element` (walls), `create_point_based_element` (doors/windows, `hostWallId`, `facingFlipped`), `create_surface_based_element` (floors/ceilings/roofs), `create_room`, `create_level`, `create_grid` | Exist `[VERIFIED 2026-11-24 schemas]`; behaviour untested `[THEORY]`. Prefer scripts until each is piloted |
| `operate_element` (Delete, Isolate, SetColor …) | Delete is permanent: ask first |

## 3. Read-only probe (first call in a session, on an agreed model)
```csharp
var sb = new System.Text.StringBuilder();
sb.AppendLine("Title: " + document.Title + " | " + document.PathName);
sb.AppendLine("Revit: " + document.Application.VersionNumber);
foreach (Document d in document.Application.Documents) sb.AppendLine("Open: " + d.Title + (d.IsLinked ? " (linked)" : ""));
foreach (Level l in new FilteredElementCollector(document).OfClass(typeof(Level))) sb.AppendLine(l.Name + " " + Math.Round(l.Elevation * 304.8));
return sb.ToString();
```
`[VERIFIED 2026-11-24]` (an equivalent script ran read-only and returned title, levels and category counts).

## 4. Bridge behaviour
- **Keep scripts ≲ 4k characters.** A 9k script timed out three times; split into three it ran in < 1 s `[IMPORTED KPwBI-ARS]`. Typed C# only (`dynamic` timed out) `[IMPORTED KPwBI-ARS]`.
- Errors arrive in Chinese: `执行失败: Exception has been thrown by the target of an invocation` = runtime exception (try/catch, return `(ex.InnerException??ex).Message`); `代码编译错误` = compile error with line; `代码执行超时` = timeout `[IMPORTED KPwBI-ARS]`.
- **Transactions:** a throwing call rolls back everything; a call that catches and returns commits what came before; a timed-out call may still have completed: query state before retrying `[IMPORTED KPwBI-ARS]`.
- **Revit may delete elements at commit** (dialog "Can't make type") although the script returned OK: verify in a later call `[IMPORTED KPwBI-ARS]`.
- **Modal dialogs freeze the API and look like timeouts:** floors/walls overlapping, "Can't keep elements joined", "identical instances in the same place", "Can't make cut-out", say_hello. Ask the user to dismiss (Unjoin/OK, never Delete), then count what committed `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]`.
- Replies can come back out of step (a reply carrying the previous call's result): re-query when a result looks wrong `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]`.
- Compiler quirks: avoid `?.` chains and null `.AsString()`; `int[]` literals may fail (use `double[]`/`long[]`); prefer `Func<>` over local functions; `ElementId.Value` and `new ElementId(long)` in 2026; some BuiltInParameters absent in 2026 (guard); no `WallType.CrossSection`; `out` is a keyword `[IMPORTED KPwBI-ARS]` `[IMPORTED STR]`.
- **Silent failure handling** `[VERIFIED 2026-11-25]`: subscribe `app.FailuresProcessing += h` (lambda: delete warnings; on errors `e.SetProcessingResult(FailureProcessingResult.ProceedWithRollBack)`), unsubscribe in `finally`. The commit then returns `RolledBack` instead of a modal dialog. It does **not** catch failures raised immediately inside `FamilyManager.Set` in a family document.
- **Timeouts are not always hangs:** a long call (dozens of commits) exceeds the bridge timeout while Revit keeps working; the next call times out too. Keep calls short; log progress to a text file inside long loops `[VERIFIED 2026-11-25]`.
- Persist between calls: `AppDomain.CurrentDomain.SetData/GetData` (while Revit stays open) `[IMPORTED KPwBI-ARS]`.
- One concern per script: create types → set parameters → place, in separate calls `[IMPORTED KPwBI-ARS]`.
- **One level per call** for heavy work (several levels raised "insufficient memory" and rolled back) `[IMPORTED STR]`. Keep reporting in a separate read-only call (an exception in reporting rolled back the modelling) `[IMPORTED STR]`.
- Speed: copy element data into arrays, compute, write only changed elements `[IMPORTED STR]`. File hand-off: Python writes geometry to a text file, C# reads it with `File.ReadAllLines` `[IMPORTED STR]`.
- Do not touch elements after deleting them in the same script (`InvalidObject`) `[IMPORTED STR]`.
- **Family documents:** `EditFamily` fails inside the tool transaction; use `Application.OpenDocumentFile` / `NewFamilyDocument` + own Transaction, SaveAs, Close; delete `.0001.rfa` backups `[IMPORTED KPwBI-ARS]`; **confirmed here: new family from template, reopen, edit, save, load, all from `send_code_to_revit` `[VERIFIED 2026-11-25]`** (the STR skill's "impossible" note was about `EditFamily` inside the tool transaction). `LoadFamily(path, out fam)` returns the family and its symbol ids in the same call `[VERIFIED 2026-11-25]`.

## 5. Visual check `[IMPORTED KPwBI-ARS]`
Duplicate a 3D view (`CHK <AREA> 3D`, no AI names), crop box not section box, hide levels/grids; `ViewOrientation3D(eye, up, forward)` with up ⟂ forward; `ImageExportOptions` (PixelSize 4000, FitToPage) to a folder; compare with the elevation/render.

## 6. KPwBI PC bridge (not used here) `[IMPORTED KPwBI-ARS]`
The KPwBI sessions ran in a container and staged PC files with `device_stage_files`. This repo runs locally: files are read directly. Kept for the record in `assets/legacy/`.

## Related
`troubleshooting.md`, `model-validation.md`, `openings-families.md` (family documents).
