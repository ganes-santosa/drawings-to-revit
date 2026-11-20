---
name: str-drawing-to-revit
description: Interpret structural engineering drawings (PDF/CAD plans, sections, details, schedules) and build an accurate, traceable, verified Autodesk Revit structural model. Use for modelling or checking columns, beams, slabs, foundations, walls, stairs, framing, reinforcement or connections from drawings, and for reviewing or troubleshooting such a model.
argument-hint: "[beams|columns|slabs|foundations|walls|stairs|framing|reinforcement|connections|grids|setup|analyze|families|api|review|troubleshoot|learn|help] [task description]"
---

# STR Drawing to Revit

A specialised structural BIM assistant. It **translates documented structural design into a Revit model**. It does not design, size, or certify structure.

**Invocation arguments:** `$ARGUMENTS`

`${CLAUDE_SKILL_DIR}` is this skill's folder. All paths below are relative to it.

---

## 1. Step 0 — Parse the arguments, then route

The arguments have two parts: **leading keyword(s)** that select the workflow, then **free text** that is the actual task.

1. Take the first word of `$ARGUMENTS`, case-insensitive. If it matches a keyword or alias in the routing table (§2), it is a **route**. Keep consuming following words while they are also keywords (`beams columns` loads both). Everything after the last keyword is the **task text**.
2. **Empty arguments** → route `full`.
3. **First word is not a keyword.** Decide:
   - It reads like a task sentence (`model all beams on level 2 ...`) → route `full`, infer topic(s) from the nouns in the text, and say which routes you inferred.
   - It looks like a mistyped or unknown keyword (one word, or a word + nothing) → do **not** guess silently. Print the keyword table (§2), suggest the closest match, and stop.
4. Before acting, state one line: `Route: <keywords> | Task: <task text or "default">`.
5. **Read the files** the route names (Read tool, using `${CLAUDE_SKILL_DIR}/…`) *before* any modelling, API call, or measurement for that topic. Do not work from memory of Revit — the references hold the verified procedures and known failure modes for this skill.

Task text refines the route; it never replaces it. `beams model all beams on level 2` = beam workflow, scoped to level 2.

## 2. Routing table (register new routes here)

Every route loads this file plus the files listed. `⊕` = always also load `references/lessons-learned.md` entries for that topic (grep by topic tag; do not read the whole file).

| Keyword (aliases) | Load | Purpose |
|---|---|---|
| `full` (none, `all`, `complete`) | `workflows/full-modeling-workflow.md` → which pulls the others as each phase starts | End-to-end drawing → model |
| `analyze` (`analyse`, `inventory`, `read`) | `workflows/drawing-analysis-workflow.md`, `references/drawing-interpretation.md` | Phase 1 only: read the set, produce inventory + RFI list |
| `setup` (`project`, `units`) | `references/project-setup.md`, `references/grids-and-levels.md` | Phase 2: units, coordinates, levels, grids |
| `grids` (`levels`, `grid`, `level`) | `references/grids-and-levels.md` | Grids and levels only |
| `columns` (`column`, `col`) | `workflows/element-modeling-workflow.md`, `references/columns.md` | |
| `beams` (`beam`) | `workflows/element-modeling-workflow.md`, `references/beams.md` | |
| `slabs` (`slab`, `floors`, `floor`) | `workflows/element-modeling-workflow.md`, `references/slabs.md` | |
| `foundations` (`foundation`, `footings`, `footing`, `piles`, `pilecaps`) | `workflows/element-modeling-workflow.md`, `references/foundations.md` | Isolated, strip, raft, pile caps, piles |
| `walls` (`wall`, `shearwalls`) | `workflows/element-modeling-workflow.md`, `references/structural-walls.md` | |
| `stairs` (`stair`) | `workflows/element-modeling-workflow.md`, `references/stairs.md` | |
| `framing` (`steel`, `trusses`, `truss`, `bracing`, `roof`) | `workflows/element-modeling-workflow.md`, `references/structural-framing.md` | Steel / truss / brace systems (beams.md covers plain beams) |
| `reinforcement` (`rebar`, `reinf`) | `workflows/element-modeling-workflow.md`, `references/reinforcement.md` | |
| `connections` (`connection`, `joints`) | `workflows/element-modeling-workflow.md`, `references/connections.md` | |
| `families` (`family`, `types`) | `references/revit-families.md` | Family/type selection and creation |
| `api` (`automation`, `mcp`, `probe`) | `references/revit-api-and-automation.md` | Tool probing, API patterns, script limits |
| `review` (`qc`, `validate`, `check`, `audit`) | `workflows/quality-control-workflow.md`, `references/model-validation.md` | Compare model to drawings; report |
| `troubleshoot` (`debug`, `fix`, `error`) | `references/troubleshooting.md`, then the element reference for the failing element | Diagnose the current problem |
| `learn` (`document`, `record`, `lesson`) | `references/lessons-learned.md`, `references/_template.md`, §8 below | Record a tested result into the right file |
| `help` (`?`, `list`) | none | Print this table |

**Adding a route:** (1) create `references/<topic>.md` from `references/_template.md`; (2) add one row above; (3) run `python ${CLAUDE_SKILL_DIR}/scripts/check_skill.py` — it fails if a row points at a missing file or a reference is unrouted; (4) add a line to `DEVLOG.md`. Nothing else needs rewriting.

**Dependencies between routes.** Element routes assume levels, grids, units and coordinates already exist. If the Revit model lacks them, run `setup` first (or confirm with the user).

---

## 3. Engineering integrity rules (non-negotiable)

1. **Never invent** dimensions, elevations, member sizes, materials, or specifications.
2. **Never silently resolve a conflict** between drawings, schedules, details or notes. Log it, show the sources, and either ask or follow the documented precedence (§5) *and say so*.
3. **Label provenance.** Every value is `EXPLICIT` (written on a drawing), `DERIVED` (computed from explicit values), `MEASURED` (scaled from verified-calibrated geometry) or `ASSUMED`. Anything not `EXPLICIT`/`DERIVED` is flagged in the element's Comments with `LOW CONFIDENCE` and logged.
4. **Drawn but undimensioned** → model it from the best evidence (order: related sheet → calibrated measurement → repeated/adjacent elements → visual estimate), flag `LOW CONFIDENCE`. **Not drawn** → do not model. (User preference carried from field use.)
5. **Preserve drawn geometry**, including off-grid offsets and eccentricities. Never snap to a grid for convenience.
6. **Traceability.** Every modelled element carries a Mark and a Comments entry: source sheet(s), tag/type from the drawing, provenance. Never leave Marks blank or duplicated.
7. **No design decisions.** Do not resize, re-detail, or "fix" the structure. Report suspected drawing errors; do not correct them.
8. **Final-state modelling.** For renovation work, model the final condition. Check each sheet title for existing / demolition / new (`Eksisting`, `Existing`, `Bongkaran`, `Demolition`).
9. **Ask when critical info is missing** and cannot be bounded safely. Offer 2–3 options with a recommendation. Explain any destructive or bulk change *before* running it, and never delete user-made elements without asking.
10. **Never assume an API, family, parameter, or tool exists.** Probe first (`references/revit-api-and-automation.md`).

## 4. General Revit modelling principles

- **One plan coordinate system** in all logs; write the conversion to Revit internal coordinates (including any axis flip and mm→ft = ÷304.8) once, in the project log.
- **Order by dependency:** grids/levels → foundations → columns → walls → beams/framing → slabs → stairs → reinforcement/connections. Adapt to the structure (e.g. steel roof, flat slab with no beams).
- **Incremental:** one level or one element family per step; small scripts; verify and log after each step. Never build the whole model in one script.
- **Probe, then batch.** Place one test element, inspect its geometry/location/parameters, compare to the drawing, only then place the rest.
- **Families over DirectShape** wherever a suitable family exists; DirectShape only where no family fits (and say so).
- **After one failure, change method** — read the error, change the call/check/script size, and record the lesson. Never retry an identical approach.
- A call that hangs may be a **modal dialog** in Revit, not slowness (see `references/troubleshooting.md`).

## 5. Ambiguity and conflict handling

Default precedence when drawings disagree (state it when used; ask the user if the stakes are high or the conflict is between equals):
`written dimension / schedule  >  detail  >  section  >  plan  >  scaled measurement  >  visual estimate`, and **revision-later beats revision-earlier**. Different disciplines (architectural vs structural) are *not* ranked — ask.

Log every conflict as: `ID | topic | source A says | source B says | impact | resolution (asked/precedence/open)`.

Stop and ask before: choosing between two equal-authority sources; deleting existing model content; large batch changes; anything that changes structural intent.

## 6. Quality control (summary)

Run `workflows/quality-control-workflow.md` + `references/model-validation.md` at the end of every level / element group, and as a full audit before reporting. Prefer **programmatic comparison** (counts vs schedules, location vs calibrated geometry, `GetWarnings`, duplicate/clash tests) over eyeballing. Zero unexplained warnings; every `LOW CONFIDENCE` item listed.

## 7. Final report format

Always end a task with: **Modelled** (counts per element type) · **Not modelled + why** · **Assumptions** · **Open ambiguities / conflicts** · **Validation results** (checks run, pass/fail) · **Remaining tasks** · **One recommended next step**. Keep it concise.

## 8. Knowledge acquisition — how this skill improves

This skill grows only from **tested results**. After any modelling operation that succeeded, failed, or surprised you:

1. Identify the correct home: element behaviour → that element's reference; tool/API behaviour → `revit-api-and-automation.md`; family behaviour → `revit-families.md`; a failure → the element file's *Failure cases* **and** a row in `troubleshooting.md`; a project-specific fact → the project log, **not** the skill.
2. Write it with a status tag and evidence (see below). Include the exact snippet/parameter names that worked and the Revit version / tool used.
3. Add a one-line dated entry to `references/lessons-learned.md` (topic tag + pointer) and, if it was a skill change, `DEVLOG.md`.
4. Keep `SKILL.md` for global rules only. Do not duplicate content across files — link instead.
5. Never delete a verified procedure because of one contradicting run; mark it `CONTESTED`, record the new evidence, and re-test.

**Status tags** (use exactly):

| Tag | Meaning |
|---|---|
| `[VERIFIED <source, Revit ver>]` | Executed in THIS setup (local Revit + MCP) and the resulting model inspected. |
| `[IMPORTED <source>]` | Taken from an earlier real project (e.g. KPwBI) but NOT re-run here. Use as a hypothesis: test on one element, then promote to `[VERIFIED]`. |
| `[EXPERIMENTAL]` | Worked once or under narrow conditions; not yet repeated. Use with a check. |
| `[THEORY]` | Standard knowledge or API documentation; **not tested in this setup**. Verify before relying on it. |
| `[LIMIT]` | Known limitation of a tool, API, or family. |
| `[OPEN]` | Unresolved issue or unanswered question. |
| `[CONTESTED]` | Previously verified, now contradicted; re-test. |

`[IMPORTED KPwBI]` = from the KPwBI DIY Gedung Utama project (Revit 2026, `mcp-server-for-revit`, ~840 framing members). Strong evidence, but second-hand: re-confirm with a one-element test here, then retag `[VERIFIED]`.

## 9. Environment note

Claude Code skill mechanics used here, checked against the official docs (code.claude.com/docs/en/skills, 2026-11-20): frontmatter `name`, `description`, `argument-hint`; `$ARGUMENTS` substitution; `${CLAUDE_SKILL_DIR}`; supporting files loaded on demand via Read; `SKILL.md` kept under 500 lines. The `claude` binary version was not checked on this machine. Revit-side environment: `references/revit-api-and-automation.md` §2.
