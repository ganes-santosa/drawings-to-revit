# Roof framing — steel trusses, portals and arches, roof steel frames, canopies, purlins, bracing (OST_Truss, OST_StructuralFraming, OST_StructuralColumns)

> Legend: SKILL.md §8 · Last reviewed: 2026-11-25 · Revit tested: RSUD Cakung roof field report (Revit 2026, `mcp-server-for-revit`; Roof Utama arch 299 members, Roof Aula mono-pitch 92 members; `assets/field-reports/2026-11-25-rsud-cakung-roof-supports-voids.md`) where tagged `[VERIFIED RSUD]`; KPwBI items imported; everything else `[THEORY]` until run. Drawing conventions below come from reading the six sample sets (2026-11-25).
> Order of work: `workflows/element-modeling-workflow.md` (Stage A types → gate → Stage B placement → gate). This file supplies the roof-specific details for each step.
> Support and connectivity rules (nothing floats): `building-logic.md`. Plain floor beams: `beams.md`. Concrete roof slabs: `slabs.md`.

## 1. Scope
Steel roof structures on top of the concrete frame: trusses (kuda-kuda) and their stub columns, portal and arch frames, steel frames on the roof (crown, penthouse), canopies (kanopi), purlins (gording), sag rods (trekstang/sagrod), wind bracing (ikatan angin), ring and edge beams. Not covered: connections, plates and bolts (parked); roof sheeting and gutters (architectural); light-gauge truss design (supplier's job, §2).

### 1.1 Roof systems in the sample sets (read the system first, then model)
| System | Sample (file, page) | What the drawings give | Typical members |
|---|---|---|---|
| **Steel trusses on stub columns over a roof slab** | KPwBI GKU p36 (trusses 1, 1A, 2–7); KPwBI GPNJ p50 plan, p51–52 truss sections | Roof frame plan (*denah rangka atap baja*) with truss lines named `TRUSS 1…6` and member tags; one elevation per truss with a profile written on **every** member, panel dimensions and level marks (`SFL +14.400`, `LANTAI DAK +17.250`, `T.O.B +19.650`) | chords WF250x125x6x9, webs 2L70x70x6 / 2L90x90x7, bottom chord 2L100x100x10, stub columns HB300 / WF300x150 on concrete beams 500x1000, purlins CNP150x65x20x3.2 @ 1200 along the slope, trekstang Ø10, concrete upstand *tanggulan* 150x300 |
| **Curved arch frame** | RSUD Cakung p62 plan (S-48), p63–65 sections per axis (S-49…) | Plan over the atrium with profile labels on each member; sections with span 16 800, column height 3 750, crown 7 500 above the slab | WF350.175.7.11 columns and arch rafters, WF250.125.6.9 edge/ring beams, purlins C125.50.20.2,3 @ 1215 along the arc, trekstang Ø12, ikatan angin Ø16 |
| **Steel frame on the roof (crown)** | Hunver OIKN p30 (*denah rangka crown*, SFL +58.850) | Plan with `CS1`, `BS1–BS3` tags, a **PROFIL BAJA** table on the same sheet, symbols for moment vs shear connections | CS1 HB250x250x9x14, BS1 WF400x200x8x13, BS2 WF300x150x6x9, BS3 WF200x100x5.5x8 |
| **Flat canopy** | DRC Kalimantan p65 (*denah rangka atap SL+4.000*), p66/p70 blow-ups | Plan with purlin spacings (≈2024), slope 1°, cantilever beams from the columns | purlins C100.50.20.2,8, trekstang Ø12, spandek sheeting |
| **Light-gauge roof (baja ringan)** | DRC Kalimantan p72 (*detail rangka atap*) | Schematic plan and two sections only: `BAJA RINGAN C1`, slope 10°, spans 7 421 / 9 680 | supplier-designed; members not engineered one by one |

**Text is often outlined on roof sheets.** RSUD p62–65 and KPwBI GPNJ p50 carry almost no searchable text (only titles), and the Bandara and Tower 4 sets returned no roof text at all. `find_schedules.py --element roof` finds the sheets where text exists; otherwise read the drawing index and look visually, or ask the user to point to the sheets.

---

## 2. Decide what to model (ask once, at setup)
Part of the project modelling decisions (`project-setup.md` §3 step 5b). Ask with AskUserQuestion; record in the project log.

| Member group | Default | Why |
|---|---|---|
| Columns, rafters, truss chords and webs, ring/edge beams, canopy beams | always model | drawn with profiles; primary structure |
| Purlins (gording) | **model** when the profile and spacing are drawn | count and weight matter for quantities and 4D |
| Sag rods (trekstang/sagrod), wind rods (ikatan angin), turnbuckles | **ask**; default: list as not modelled | many small items; RSUD modelled them all (204 sag rods, 32 wind rods) as straight `Beam` members `[VERIFIED RSUD]` (B4–B5) |
| Light-gauge (baja ringan) roof | **ask**: skip, or model only the ring beam it sits on, or a placeholder | the supplier designs it; the drawing is schematic |
| Plates, bolts, base plates | not modelled (parked) | out of focus |

Purlin segmentation (continuous over several trusses or one piece per bay) follows the beam segmentation decision unless the user says otherwise.

### 2a. Roof structure method (ask once, at setup; user rule 2026-11-25)
Ask with AskUserQuestion (`project-setup.md` §3 step 5b) and record the answer in the project log:

| Method | What it means | Status |
|---|---|---|
| **Revit Structural Trusses** *(recommended, default)* | each kuda-kuda / roof frame is one truss instance (`OST_Truss`); the truss creates its chords and webs as framing members; one truss type per layout and profile set (A4b) | `[THEORY]` until piloted |
| **Structural Framing members** | every chord, web, rafter and post is a separate beam placed in 3D (B4b) | `[VERIFIED RSUD]` (299 + 92 members) |

- Purlins, sag rods, wind bracing, ring and edge beams and canopy beams are **framing members in both methods** (B4b): they are not part of a truss.
- A frame drawn **without webs** (a single rafter on posts, a portal frame, a solid-web WF arch like RSUD Roof Utama, a canopy cantilever) is not a truss: rafters and arches are **Structural Framing** members (B4b; arches with the curved beam method), posts are **Structural Columns** (slanted if drawn sloped), haunches are Revit steel connections or stay on the LOD 500 not-modelled list (§2). Say so when the method question is asked. Why (web research 2026-11-25, to re-check on a real project): Revit's beam tool is its own way to draw sloped and curved rafters; the truss tool needs a chord-and-web layout; Revit's knee and apex haunch connections attach only to separate framing members and columns and transfer to Advance Steel; a whole-frame family (swept profiles, used for pre-engineered buildings) loses per-member schedules, analysis and connections `[THEORY]`.
- If the truss pilot (B4a) cannot match the drawing, show the difference and ask before switching that frame to framing members.

**Always list as not modelled (LOD 500 gap), per roof, with detail sheet and page** `[VERIFIED RSUD]`: haunches (cut WF), end plates, splice plates, base plates and anchors, bolts, gutter brackets. A later LOD 500 pass can pick them up from that list.

---

## A. Types

### A1. Where the roof types are on the drawings
1. A **PROFIL BAJA table on the roof plan sheet** itself, small, usually top right near the notes (KPwBI GPNJ p50, Hunver p30): `TIPE | PROFIL`, grouped KOLOM / BEAM / BRACING.
2. **No table: the profile is written on each member** in the truss elevations (KPwBI GKU p36) or on the plan (RSUD p62). Then the catalog is the set of distinct labels.
3. **Typical details sheet** for purlins and rods (KPwBI GPNJ p18 *detail tipikal gording baja*, *sagrod Ø12*, *wind rod #16* with turnbuckle; a table of lipped channels `LC 150x65x20x2.3` … with bolts).
4. **General notes** for steel grade: ASTM A36 / BJ37 / SS400; anchor bolts F1554 Gr.55.
5. Profiles missing from the structural sheets (front-roof blocks, canopies): look at the architectural sections, mark `LOW CONFIDENCE`, note the discipline `[IMPORTED KPwBI]`.

### A2. What to extract per type
| Field | Notes |
|---|---|
| Tag | `CS1`, `BS1`, `BR1`, a letter A–E (KPwBI roof), or none (label only) |
| Role | column / rafter / top chord / bottom chord / web / post / ring beam / canopy beam / purlin / rod / brace |
| Profile as drawn | exactly as written, for traceability |
| Normalised profile | see the notation table |
| Dimensions (mm) | WF/H: h, b, tw, tf (r if given); channel: h, b, lip, t; angle: leg, leg, t; rod: diameter |
| Double angle gap | gusset thickness from the connection detail (KPwBI used 12 mm) |
| Grade | from the general notes |
| Source | sheet/page, provenance |

**Profile notation seen in the samples** (normalise: `.`, `x`, `×` and spaces are separators; a comma is a decimal point):
| Written | Means | Note |
|---|---|---|
| `WF 350x175x7x11`, `WF.350.175.7.11` | wide flange h×b×tw×tf | RSUD writes dots |
| `HB 300x300x10x15`, `H 250x250x9x14` | H-beam / column section | |
| `CNP 150x65x20x3.2`, `C 125.50.20.2,3`, `LC 150x65x20x2.3` | lipped channel h×b×lip×t | `2,3` = 2.3 mm, never 23 |
| `2L 70x70x6` | two angles back to back | gap = gusset thickness |
| `Ø12`, `#16`, `D16` | round rod | trekstang, ikatan angin |
| `CB 375x125x6x9` | castellated beam from WF 250x125 | KPwBI standard detail table |

### A3. Catalog notes
- One catalog row per distinct profile, not per tag: `BS2` on two sheets with two profiles is a conflict, log it.
- A profile on the plan that differs from the truss section: the section is more specific, but log and ask when it changes the weight class.
- Type names follow the project's style (`revit-families.md` §3): KPwBI used `WF250x125x6x9`, `KOLOM BAJA HB300x300x10x15` `[IMPORTED KPwBI]`.

### A4–A5. Make the types in Revit
Preference order (workflow Stage A): exists → duplicate → load → new family → DirectShape (ask).
1. **Wide flange and H:** duplicate a type of a W/H-shape framing (or column) family, then set the dimensions in a separate call `[IMPORTED KPwBI]`. Parameter names differ between families: list them first:
   ```csharp
   // [THEORY] list the length parameters of one steel type, in mm
   var s = (FamilySymbol)document.GetElement(new ElementId(TYPE_ID));
   return string.Join("; ", s.Parameters.Cast<Parameter>().Where(p => p.StorageType == StorageType.Double)
       .Select(p => p.Definition.Name + "=" + Math.Round(p.AsDouble() * 304.8, 1)));
   ```
   Typical names: `d`/`h`, `bf`/`b`, `tw`, `tf`, `k`/`r`. Set them with `LookupParameter(name).Set(mm / 304.8)`.
2. **Channels (CNP/LC), angles, double angles:** look for a loadable family in the user's library first (ask for the folder once; record it). If none: a new family from `Metric Structural Framing - Beams and Braces.rft` with a parametric profile (`[OPEN]`: family editing through `send_code_to_revit` is untested), or ask the user to build it from the template with exact parameters.
3. **DirectShape fallback** (ask first): KPwBI had no angle or CNP family and modelled double angles and purlins as DirectShape in Structural Framing, using `GeometryCreationUtilities.CreateExtrusionGeometry` with an I, 2L (12 mm gusset gap) or 12-point CNP profile `[IMPORTED KPwBI]`. A DirectShape is not a real framing member: no type, no analytical model, no joins. Mark and Comments are still required.
4. **Rods:** a round bar family if one exists; otherwise list as not modelled (decision §2).
4b. **No steel content in the project or on the PC** (RSUD) `[VERIFIED RSUD]`: real families were built from the installed Metric templates (Structural Framing / Structural Column), **one fixed size per family**, ends locked to Member Left/Right (framing) or Lower/Upper Ref Level (columns). One project steel material from the spec (RSUD BJ-37 / ST-37, fy 240 MPa) with the source in its identity data. Whether the families were built by script or by hand is not recorded `[OPEN]`: ask before relying on a script.
5. Nearest-size substitution: only with the user's OK, `LOW CONFIDENCE`.

### A4b. Truss types (method: Structural Trusses, §2a) `[THEORY]`
A Revit truss type is a **truss family** (the layout: chord shape, panel points, web pattern) plus the **framing types** its chords and webs use. So the profile types (A4–A5) are made first, then the truss types.
1. **Catalog the trusses** from the truss sections: one row per distinct layout (chord shape flat / pitched / mono / arched, panel count and spacing, web pattern and diagonal directions) and profile set. Copies of one section = one type. Record: truss names as drawn (`TRUSS 1`, `1A`), span, heel and ridge heights, panel points, profile per role (top chord, bottom chord, verticals, diagonals), source sheet/page. A member whose profile differs from its role (e.g. end diagonals 2L90 while the rest are 2L70) is listed as a **per-member override**.
2. **Inventory:** `get_available_family_types` with `OST_Truss`, or `new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_Truss).WhereElementIsElementType()`. List each type's parameters (the snippet in A4–A5 step 1, all storage types) to read its chord and web framing types.
3. **No matching truss types in the project: ask** (AskUserQuestion): **Make the truss types first** *(recommended)*: build them from the drawings (steps 4–5), then place; or **I will load my own truss families**: wait, then inventory again and map the catalog. Never place a truss until every truss in the catalog has a verified type.
4. **Truss family, one per layout:** template `Metric Structural Trusses.rft` (this machine: `D:\ProgramData\Autodesk\RVT 2026\Family Templates\English\` `[VERIFIED exists 2026-11-25]`). Top chord, bottom chord and web lines on reference planes at the **drawn** panel points, locked; fixed panel dimensions, or equal spacing only where the drawing divides equally. Save to the family folder (`families\Structural Trusses\`), load into the project. Family documents can be created, edited, saved and loaded from `send_code_to_revit` (`NewFamilyDocument` / `OpenDocumentFile` + own Transaction, one build step per call) `[IMPORTED ARS]` (door and window families, 2026-11-25). Creating the truss chord and web lines by API is `[OPEN]`: pilot it on one truss; if it fails, ask the user to draw the layout in the family editor from the geometry record (exact panel points).
5. **Truss types, one per profile set:** duplicate, then set the top chord, bottom chord, vertical web and diagonal web framing types and the bearing chord (top or bottom, as the support detail shows), each in its own call. Names follow the drawing or the project style (`TRUSS 1 (T1/T1A)`).
6. **Gate (adds to A6):** every catalogued truss has a type; each type's chord and web framing types read back match the catalog; the pilot instance (B4a) matches the drawn panel points.

### A6. Gate
Read back every type's dimensions in mm against the catalog; every profile label found on the roof sheets resolves to a type (or to a DirectShape profile the user approved); grades set where the family has a material parameter.

---

## B. Placement

### B1. Where the positions and heights are
- **Plan** (*denah rangka atap*): member lines, truss/frame names, spacings, grid offsets, overhangs.
- **Sections** (*potongan truss N*, *potongan rangka atap As.E-G/5&6*): heights, slopes, panel points, member profiles. A truss name in the plan points to its section; one section often serves several identical trusses.
- **Level marks** on the sections: roof slab SFL, *lantai dak*, top of building (T.O.B). Use written heights; scale only when nothing is written (`LOW CONFIDENCE`).
- **Architectural roof plan and sections** for heights missing from the structural set `[IMPORTED KPwBI]`.

### B2. Geometry record and instance table
Roof members are placed in **3D coordinates** (sloped and curved), not level + offset. First write one **geometry record per truss or frame** in the project log (`[IMPORTED KPwBI]` format, extended):
- frame id, plan line (start/end x,y), the gridlines it sits on, and every gridline where an identical copy sits;
- supports: what and where (stub column, column, concrete beam, tanggulan), support top z;
- heel z, ridge z, eave tip, overhang length, slope (degrees or rise/run);
- chord centreline z at the supports; panel points along the chord (from the dimension strings);
- web pattern and diagonal directions as drawn;
- profile per member segment;
- for arches: span s, rise f, radius R = (s²/4 + f²) / 2f, centre point, and which line the heights refer to (top of steel or centreline).

Then the instance table, one row per member:
`mark | type | role | frame id | start (x,y,z) | end (x,y,z) | arc mid-point (if curved) | start support | end support | cross-section rotation | CANTILEVER? | source | provenance`

**Arched roofs: one circle from the section, every member on its own radius** `[VERIFIED RSUD]` (Roof Utama):
1. From the **section vectors**, read the circle centre (RSUD: on the ridge grid, below the slab) and the top-of-steel radius R_top. Check it against the dimensioned apex and eave heights.
2. Concentric radii from that one circle: rafter centreline = R_top − d/2; rafter soffit = R_top − d; purlin mid-depth = R_top + purlin depth/2; bracing nodes on the rafter centreline (or as detailed).
3. Purlins on the rafter top, web normal to the roof surface, spaced by **arc length**, equal division from ridge to eave.
4. The plan can draw purlins at developed (true arc-length) spacing and beyond the eave: take geometry from the section, log the plan difference as a question.
5. Ridge and eave members: top flush with the rafter top or just under the rafter soffit, as the detail shows; `LOW CONFIDENCE` if the detail is schematic.

**Mono-pitch frames** `[VERIFIED RSUD]` (Roof Aula): slope from the section vectors, not the label (measured 10.0°); rafter positions from the plan's rafter rectangles; each post height from the section dimension beam top → rafter top; high posts, low stubs and middle posts each sit on a named concrete beam, recorded in Comments.

**Cross-check from dimensions only (before vectors are read), `DERIVED`:** span 16 800, columns 3 750, crown 7 500 above the slab, so rise f = 3 750 and R = (8 400² + 3 750²) / (2 × 3 750) ≈ 11 283 mm, half-angle ≈ 48°, arc length ≈ 18 950 mm. The purlin spacing 1215 is measured along the outer (purlin) line: count the spaces on the section; 16 spaces would need ≈ 19 440 mm, roughly 2.5 % longer than the centreline arc. That fits a purlin line about 300 mm outside the centreline, but if the numbers do not close, the 7 500 may be to the top of steel: flag `LOW CONFIDENCE` and ask.

### B3. Interpretation rules
1. **Classify the system first** (table §1.1); the rules differ for trusses, arches, frames and canopies.
2. **Plan and section together:** the plan gives positions and repetitions, the section gives heights. Never take a height from the plan or a position from a section without checking the other.
3. **Height chain, top-down where written, bottom-up otherwise:** support top → heel → slope → ridge. Check that tan(slope) matches rise/run within 0.5°; a mismatch is a conflict, not a rounding.
4. **Member lines:** truss chords and webs on their centrelines, meeting at panel points (the analysis lines of the section) `[IMPORTED KPwBI]`. Rafters and canopy beams that carry purlins: top of steel on the roof line. Record the convention once per project.
5. **Panel points from the dimension strings,** never by eye. Diagonal directions exactly as drawn.
6. **Read the profile on every member,** including extensions, hips and valleys: KPwBI hip and valley extensions were labelled A but first modelled as D overhangs `[IMPORTED KPwBI]`.
7. **Purlins:** spacing is measured along the slope (or the arc), not in plan: plan spacing = slope spacing × cos(slope). Count them from the section; edge and ridge purlins have their own spacing (KPwBI GPNJ: 830 and 150 at the eave). Purlin z = top of the member it sits on. Orientation from the typical purlin detail (GPNJ p18: purlin on a cleat, web square to the rafter); record it.
8. **Eave-tip and outline members** drawn as thin outer lines are members too `[IMPORTED KPwBI]`.
9. **Supports (nothing floats):** every truss bears on a stub column, column, concrete beam or tanggulan that exists in the model. Stub columns (KPwBI WF300x150 on concrete beams 500x1000) are columns: their base sits on the concrete beam, top at the truss heel.
10. **Canopies:** cantilever beams from the columns get `CANTILEVER` in Comments; even a 1° slope is modelled as drawn.
11. **Moment / shear connection symbols** (Hunver): note them in Comments; connections are not modelled.
12. **Light-gauge roofs:** per the decision in §2; never invent member layouts for a schematic.
13. **Roof sections govern the column plan under a steel roof** `[VERIFIED RSUD]`: where the sections show steel posts or stubs standing on a concrete beam, the concrete column stops at that beam and the steel post carries on, even if the column plan draws a concrete column there (RSUD Lantai 5–6: 600×600 columns drawn at the aula roof grid would have pierced the roof by up to 3.3 m). Never let a column rise through a roof. Log the conflict; ask if unclear (`columns.md` B3.6).
14. **Every roof edge and rafter end lands on something** `[VERIFIED RSUD]`: a post, column or beam under it. If one is missing, look for the pattern on parallel grid lines and check every column plan for a label, even one missing from the column schedule (RSUD aula south edge: KT1 drawn on both storey plans, missing from the schedule; added as concrete KT1 to Lantai 5 plus a steel WF400 post to the rafter, like the matching grid line).
15. **Do not invent beams under a roof:** a beam that no column plan or section places there does not exist. RSUD: a B7 had been placed along two purlin lines; it belonged on the grid-10 column line where the sections centre it and the posts stand on it `[VERIFIED RSUD]`.
16. **Sag rods run purlin to purlin**, straight, at purlin mid-depth, one segment per purlin gap (RSUD: 17 per line, 204 in total), never as one arc `[VERIFIED RSUD]`.

### B3b. Clean the table before placing `[THEORY]`
1. **Nodes:** collect every member end and panel point; merge ends within 20 mm (3D) into one node. Every web end must sit on a chord node; every chord runs support to support (or to a drawn splice).
2. **De-duplicate** members shared by two trusses (hips, valleys, a ridge member where trusses meet).
3. **Purlins on their supports:** each purlin end and crossing lies on a rafter or top chord line, within that member's length; overhangs past the last rafter only where drawn.
4. **Copies of a truss:** translate the geometry record to every gridline the plan names; check each copy's supports exist.
5. **Gate:** 0 member ends off a node or support (except drawn overhangs), 0 zero-length members, every profile in the catalog, member count per truss = the section.

### B4a. Trusses (method: Structural Trusses, §2a) `[THEORY]`
```csharp
// [THEORY] one truss from the geometry record; plan points and bearing z in mm
var tt = document.GetElement(new ElementId(TRUSS_TYPE_ID));
double z = Z_BEARING / 304.8;                                          // bearing chord level from the record
var sp = SketchPlane.Create(document, Plane.CreateByNormalAndOrigin(XYZ.BasisZ, new XYZ(0, 0, z)));
var line = Line.CreateBound(new XYZ(X0 / 304.8, Y0 / 304.8, z), new XYZ(X1 / 304.8, Y1 / 304.8, z));
var t = Autodesk.Revit.DB.Structure.Truss.Create(document, tt.Id, sp.Id, line);
var h = t.LookupParameter("Truss Height"); if (h != null) h.Set(H_MM / 304.8);   // check the name in the parameter list
t.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("RF-T1@3");
t.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set("TRUSS 1 | GKU p36 | EXPLICIT");
document.Regenerate();
Func<XYZ, string> f = p => Math.Round(p.X * 304.8) + "," + Math.Round(p.Y * 304.8) + "," + Math.Round(p.Z * 304.8);
return t.Id + " | members " + t.Members.Count + "\n" + string.Join("\n", t.Members.Select(id => {
    var c = ((LocationCurve)document.GetElement(id).Location).Curve; return id + " " + f(c.GetEndPoint(0)) + " / " + f(c.GetEndPoint(1)); }));
```
- **Pilot one truss first:** read back every member's end points and compare with the geometry record's panel points (±10 mm), heel and ridge z, and member count. Adjust in this order: truss height, bearing chord, the family layout, or the drawn chord shape with `t.SetProfile(topChords, bottomChords)` (also for arched chords) `[THEORY]`.
- **Plan line = the truss line between its bearing points** on the supports (stub columns, columns, concrete beams); overhangs as the family or profile draws them.
- **Per-member overrides:** after the truss is made, change that member's type (`member.ChangeTypeId(typeId)`) and read it back `[THEORY]`.
- **Marks:** the truss gets `RF-<frame>@<grid>`; each member gets `…-TC01`, `-BC01`, `-W01` by role (`t.GetTrussMemberInfo(id)` gives the role `[THEORY]`), with Comments (profile, sheet/page, provenance).
- **Copies:** one `Truss.Create` per gridline in the record; supports checked per copy (B3b step 4).
- **If a truss cannot be made to match:** show the difference and ask (§2a). `Truss.DropTruss(t)` keeps the members as separate beams `[THEORY]`; or rebuild that frame with B4b.
- Then purlins, rods, bracing and ring beams with B4b, sitting on the truss top chords.

### B4b. Framing members (method: Structural Framing; and purlins, rods, bracing, ring beams in both methods)
```csharp
// [THEORY] one sloped member; points in mm, absolute z (from the geometry record)
var sym = (FamilySymbol)document.GetElement(new ElementId(TYPE_ID));
if (!sym.IsActive) sym.Activate();
var lvl = (Level)document.GetElement(new ElementId(LEVEL_ID));       // roof level as reference
var a = new XYZ(X0 / 304.8, Y0 / 304.8, Z0 / 304.8);
var b = new XYZ(X1 / 304.8, Y1 / 304.8, Z1 / 304.8);
var m = document.Create.NewFamilyInstance(Line.CreateBound(a, b), sym, lvl, Autodesk.Revit.DB.Structure.StructuralType.Beam);
m.get_Parameter(BuiltInParameter.Y_JUSTIFICATION).Set(1);             // Center
m.get_Parameter(BuiltInParameter.Z_JUSTIFICATION).Set(1);             // Center for truss members; 0 = Top for purlin-carrying rafters
Autodesk.Revit.DB.Structure.StructuralFramingUtils.DisallowJoinAtEnd(m, 0);   // keep truss members from trimming each other
Autodesk.Revit.DB.Structure.StructuralFramingUtils.DisallowJoinAtEnd(m, 1);
m.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("RF-T1@3-TC01");
m.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set("TRUSS 1 top chord | WF250x125x6x9 | GKU p36 | EXPLICIT");
return m.Id + " | " + Math.Round(((LocationCurve)m.Location).Curve.GetEndPoint(0).Z * 304.8) + " | " + Math.Round(((LocationCurve)m.Location).Curve.GetEndPoint(1).Z * 304.8);
```
- **Every separately placed steel member is `StructuralType.Beam`,** including bracing, knee braces, rods and sloped rafters, even when it is a brace by function `[VERIFIED RSUD]` (confirms KPwBI). With `StructuralType.Brace`, Revit re-attached 32 wind-rod ends to nearby members and moved them by up to 15 m. Read every end point back (`LocationCurve.Curve.GetEndPoint`) and report the deviation; target 0.0 mm. "Slightly off axis" warnings on skewed rods are harmless: accept them.
- **Structural Usage** (`INSTANCE_STRUCT_USAGE_PARAM`) by role, so rafters, purlins and bracing schedule apart although all are "beams": rafters and ring beams Girder, purlins Purlin, wind bracing Horizontal Bracing, knee braces Kicker Bracing, sag rods Other. Set it after placing and read it back `[THEORY]`.
- **Pilot first:** read back both end z values; Revit may move the line to the reference level and store the height as end offsets. If the read-back z differs from the record, set `STRUCTURAL_BEAM_END0/1_ELEVATION` to (z − level elevation) and read back again `[THEORY]`.
- **Joins:** disallow at truss member ends (Revit otherwise trims and extends members it thinks meet); allow where a rafter frames into a column, as for beams (`beams.md` B4–B5) `[THEORY]`.
- **Curved members:** `NewFamilyInstance(arc, symbol, level, StructuralType.Beam)` with `Arc.Create(start, end, pointOnArc)` in the vertical plane of the frame. **The main arched rafter: one arc beam per frame worked** `[VERIFIED RSUD]`; read its z back after creation. **Anything else drawn as an arc (sag rods) was flattened by Revit** into horizontal lines at one z (12 of 12) `[VERIFIED RSUD]`: model it as straight segments between the members it connects. Purlins on an arc: straight members at angle steps of spacing / R along the purlin line.
- **Curve edits reset end offsets:** after setting `LocationCurve.Curve`, write `STRUCTURAL_BEAM_END0/1_ELEVATION` back and read them back (`beams.md` B4–B5) `[VERIFIED RSUD]`.
- **Purlin orientation:** cross-section rotation (`STRUCTURAL_BEND_DIR_ANGLE`) so the web is square to the roof surface; check one in a section view `[THEORY]`.
- **DirectShape** members (fallback, A4–A5 step 3): KPwBI CNP150x65x20x3.2 purlins sat web on the rafter top, flanges up, lips in, web centre 46 mm outboard at the eave tips `[IMPORTED KPwBI]`.
- **Marks:** `RF-<frame>@<grid>-<role><nn>` (trusses: B4a) (TC top chord, BC bottom chord, W web, P post, R rafter, PU purlin, RB ring beam, K stub column); follow the project's pattern if it has one. Comments: drawing tag and profile, sheet/page, provenance, `LOW CONFIDENCE`, `CANTILEVER`.
- **Order:** supports (stub columns, columns) → trusses (B4a) or rafters / chords and webs (B4b) → ring and edge beams → purlins → rods (if modelled).
- **One model group per roof** `[VERIFIED RSUD]`: e.g. `RANGKA ATAP UTAMA (E-G/4-7)` (299 members), `RANGKA ATAP AULA` (92); Marks `RA-U-*`, `RA-A-*`, with a type code for rods (`RA-U-TS-LL-SS` = sag rod, line LL, segment SS). To rebuild a group: delete the members, recreate them, then `NewGroup` again. Moving or changing a group raises a modal warning that blocks the API.
- **Re-runnable:** skip rows whose Mark already exists (`revit-api-and-automation.md` §5).
- One frame or one roof zone per call; scripts ≲ 4k characters.

### B5b. Audit and repair after placing `[THEORY]`
Run read-only after each roof zone: `scripts/revit/audit_roof.cs` (includes the members of trusses whose Mark has the prefix; member ends not on another member or a support, measured in 3D; very short members), `scripts/revit/find_duplicates.cs`, `scripts/revit/check_connectivity.cs` (stub column bases). The general connectivity check is loose for trusses (all members of one truss overlap in plan and height), so the 3D roof audit is the one that counts. Repair only what is listed; if a support moves, re-check what rests on it (`building-logic.md` §7).

### B6. Verification
**Before calling a roof done, in this order** `[VERIFIED RSUD]`:
1. Every post base sits on a modelled beam or column top. Record the base level and offset including plate and grout from the base detail (RSUD +26.00 = 25.95 top of concrete + 25 + 25).
2. Every post top reaches the rafter centreline.
3. No concrete column passes through any roof member (bounding box against the roof group, then confirm with geometry).
4. Every roof edge and rafter end has a vertical support or a beam under it.
5. Every column top carries something (`audit_columns.cs` free tops); otherwise the hidden group or ask (`columns.md` B3b.6).
6. Bracing and rod end points read back, deviation 0.
7. Group member counts recorded in the project log.

Also:
- Member count per truss / frame and per profile vs the sections and plan; trusses: every member's end points on the drawn panel points (±10 mm) and every per-member override applied.
- Heel, ridge and crown z vs the written levels (±10 mm); slope vs drawn (±0.5°).
- Purlin count and spacing along the slope; eave-tip purlins present.
- Every truss and frame on a modelled support; every stub column on a concrete element.
- Nothing at a height taken from a misread end-on member label (drawing-interpretation §5) `[IMPORTED KPwBI]`.
- A 3D view of each roof zone for the user (screenshot), plus the audit numbers.

## Field notes and failure cases
| Symptom | Cause | Fix | Status |
|---|---|---|---|
| Hip extensions with the wrong profile | Assumed D | Read the letter on every segment (A) | [IMPORTED KPwBI] |
| Eave-tip purlins missing | Thin outer lines overlooked | Model them; ask what a user circle means | [IMPORTED KPwBI] |
| Roof sheets not found by the schedule finder | Text outlined (RSUD, GPNJ plan, Bandara, Tower 4) | Drawing index + visual search, or ask | [VERIFIED 2026-11-25, samples] |
| Purlin count off by one or two per slope | Spacing applied in plan instead of along the slope | Spacing along the slope; plan = s × cos θ | [THEORY] |
| `C 100.50.20.2,8` read as 28 mm thick | Decimal comma | Comma = decimal point | [THEORY] |
| Double angles modelled as one angle | `2L` read as `L` | 2L = two angles + gusset gap | [THEORY] |
| Arch crown too high or low | Heights refer to top of steel, not the centreline | Check the arc length against the purlin count; ask | [THEORY] |
| Truss members trimmed or extended by Revit | Automatic joins | Disallow joins at member ends (framing method) | [THEORY] |
| Truss members off the drawn panel points | Family layout or truss height does not match the section | Fix the layout, the height or `SetProfile`; ask before switching to framing members | [THEORY] |
| Rod / brace ends moved up to 15 m | Placed as `StructuralType.Brace`; Revit re-attached the ends | Place as Beam; read ends back | [VERIFIED RSUD] |
| Arc sag rods became flat lines at one z | Revit flattens non-rafter arc beams | Straight segments purlin to purlin | [VERIFIED RSUD] |
| Concrete column pierces the roof (up to 3.3 m) | Column plan followed instead of roof sections | Column stops at the beam; steel post continues (B3.13) | [VERIFIED RSUD] |
| Roof edge with no vertical member | Column missing from the schedule, drawn on plans | Check every column plan and the parallel grid pattern (B3.14) | [VERIFIED RSUD] |
| Call "times out" after editing a roof | Group moved/changed: modal warning | User closes the dialog; re-query; rebuild groups by delete → recreate → NewGroup | [VERIFIED RSUD] |

## Related
`project-setup.md` §3 step 5b (roof method), `building-logic.md`, `beams.md` (end offsets, joins, curved beams), `columns.md` (stub columns), `revit-families.md`, `drawing-interpretation.md`, `model-validation.md` (#21), `project-setup.md` §3 step 5b, field report `../assets/field-reports/2026-11-25-rsud-cakung-roof-supports-voids.md`.
