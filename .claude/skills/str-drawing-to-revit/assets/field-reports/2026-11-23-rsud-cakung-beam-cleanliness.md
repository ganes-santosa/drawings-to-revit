# Handover to the skill agent: beam connectivity, joints, continuity and alignment

From: the structure agent on the RSUD Cakung tender model (a 6-floor hospital plus roof; structural DED of 84 pages).
Session: 2026-11-20 to 2026-11-23. Floors covered: Lantai 1 to 4, about 2,330 beams before clean-up and 904 after.
Setup: **Revit 2026**, driven through **mcp-server-for-revit** `send_code_to_revit`. C# runs inside `Execute` with `document` and an open transaction. PDF work used pdfplumber and poppler in a Linux workspace.

How to read the status tags below:
- **[VERIFIED]**: run in Revit 2026 in this session, with the result checked by an audit script or by the user's screenshots.
- **[EXPERIMENTAL]**: run in Revit and the counts came out right, but nobody has looked at the final geometry in 3D after the fix yet.
- **[THEORY]**: a reasoned rule that hasn't been run.

I haven't read the current repo, so file names under "Skill impact" are suggestions based on the layout you described (references/, workflows/). They are not quotes. Where I say the old skill said something, I mean the earlier `structural-drawings-to-revit` skill (from the KPwBI project), which your skill imports from.

---

## 0. The big lesson in one paragraph

Placing beams exactly where the drawn lines start and stop gives a model that looks right in plan but is wrong as a structure. The user found every one of these problems by orbiting a 3D view, not by reading reports:
- beam ends hanging in the air;
- edge beams missing because they were drawn differently;
- cantilever tips with nothing tying them together;
- corners with a notch or stub;
- girders chopped into a dozen pieces;
- perimeter beams sticking out past the columns.

The cure is a fixed **clean-up pipeline** after placement (section 9), plus an **audit with numbers** (section 10) that must reach zero, or a short list the user has agreed to, before a floor is called done.

---

## 1. Nothing floats: every beam end needs a support

**Found.** After placing about 2,300 beams from dashed face-line pairs, the user's screenshots showed beams that met neither each other nor a column. The first audit found free ends on every floor: Lt1 54, Lt2 8, Lt3 68, Lt4 113. Causes:
- the drawn line stops at a column face, at a text label, or at a dash gap;
- end positions were rounded differently on different sheets;
- calibration differs slightly between sheets.

**Rule.** A beam end is connected when either of these holds:
- (a) it lies inside a column footprint (bounding box ± 20 mm) at the beam's height; or
- (b) it lies on another beam: within that beam's half-width + 30 mm of its centreline, and between its two ends.

The only ends allowed to be free are cantilever tips (here, beams tagged OV / Sov "overstek"). Everything else is either fixed or listed for the user.

**Fix method** (pure maths on arrays, then one write per changed beam):
1. For each free end, look forward along the beam's own direction.
2. Take the nearest of:
   - a column centre whose footprint the line passes through; or
   - a crossing beam that is roughly perpendicular (|cos| ≤ 0.5), where the crossing point falls within that beam's length.
3. Cap the search at 4 m.
4. Move the end there.
5. If it moved more than 1.5 m, append to Comments: `LOW CONFIDENCE: end extended N mm to nearest support (connectivity rule)`.

**Evidence.** Run in Revit 2026 through send_code_to_revit on all four floors. Example output: `beams 424 extended 76 unresolved 48`, then after more passes `extended 0 unresolved 14`. The user confirmed the gaps visually and then pointed at the remaining ones.

**Failure cases (all seen):**
- **Overshoot bug (my error).** The first version let an end land up to about 450 mm *past the end* of the target beam. That made the corner stubs and notches the user screenshotted ("ends don't connect cleanly"). Lesson: the crossing point must lie within the target beam's length. Any overshoot is a corner case for the joint step (section 4), not a valid support.
- **Longest-jump danger.** A 4 m cap can still find the wrong support across a void or a stair opening. Long extensions must be flagged and reviewed.
- **Side effects of other edits.** Moving a girder (for example, the flush snap in section 5) leaves the beams framing into it short. On Lt2/Lt3, 11 beams ended 274 mm short. So run the free-end scan again after every geometry change, with a wider search (±400 mm forward *or backward*).
- **Missing supports, not bad ends.** A stubborn free end usually means a support beam that was never modelled (section 2), not a bad end.

**Status.** Scan and extension: [VERIFIED]. The 4 m / 1.5 m thresholds: [EXPERIMENTAL].

**Skill impact.** This confirms your "nothing floats" principle and makes it testable. Add the connected-end definition and the extension algorithm to the beam placement/verify workflow (for example `workflows/beams.md`). Add the overshoot bug to troubleshooting.

---

## 2. "If the alternative is not modelling, model it, then tag it"

**Found.** Several perimeter beams weren't detected, because they are drawn differently from normal beams:
- **One-sided edge beams.** These are a single dashed face line running 1–4 pt beside the solid slab outline, with no second dashed line. The width is the gap between the dashed line and the outline (about 150 mm or 300 mm here). Example: the Lt1 south edge, tagged S1, at y≈8743. The S1 secondary beams all "floated" because this beam was missing.
- **Single-line edge beams tagged L1 / L2.** These are drawn only as the outline, with no face pair. The tag counts were 41 L1 on Lt1, 6 on Lt2, 22 L1 + 5 L2 on Lt3, and 28 L1 on Lt4.
- **Tie beams across cantilever tips** (Lt3 south, Lt4 south and east). Without them, rows of cantilevers end in mid-air.

**User rule (stated forcefully).** *If the only alternative is to leave it out, model it. Assume visually if you must, then tag it LOW CONFIDENCE.* This was already in the old skill as "drawn but not dimensioned → estimate". The new part is that it also covers elements drawn in an unusual *graphic* convention, not just elements missing a dimension. I had listed the L1 beams as "not modelled yet, needs a decision", and the user was annoyed that I didn't just model them.

**Detection method** (pdfplumber, on the calibrated sheet):
1. Collect long solid lines longer than about 100 pt.
2. Collect short dashed segments (linewidth 0.71 pt here, 3–9 pt long) that have *no partner dash* within 8 pt.
3. Keep any group of at least 4 dashes that runs parallel to a solid line, 0.5–4 pt from it, within the solid line's extent.
4. The face line is the dashes and the other face is the outline. Width = the gap.

Output on p31: `H solid y 8592 dash y 8895 x 24289..58603 n 23` and 8 more runs.

**Evidence.** Detection was run on the PDF. Placement was run in Revit 2026:
- Lt1: 4 S1 beams (300x600);
- Lt3: 22 L1 beams;
- Lt4: 9 L1 beams.

All are tagged LOW CONFIDENCE.

**Failure cases:**
- Line widths are specific to each drawing set. Read the widths from the sheet's own vector data first; don't hard-code 0.71.
- A one-sided line can also be a slab step or a drop edge. Check the tag next to it and the section if there is one.
- The L1 position is a guess (outline = outer face). Flag it.

**Status.** Detection: [VERIFIED] on this set. That it generalises to other sets: [EXPERIMENTAL].

**Skill impact.** Add to the drawing-interpretation reference: "edge beams can be drawn one-sided or as a single outline". Add the "model it, then tag it" rule next to the never-invent-dimensions rule, and note that they don't conflict: you invent no *dimension*; you estimate a drawn element's geometry and flag it.

---

## 3. One continuous instance per run (don't split beams)

**Found.** My placement cut beams at every column and every crossing beam, and so did the old skill's habit of keeping secondary beams split where they frame into girders. The user selected three split pieces of one B3 line and said: *"drawing it split like this provides no benefit."*

**Rule.** Merge collinear beams into one instance when all of these hold:
- same type (same family symbol);
- same level and top height (within 10 mm);
- both ends within 10 mm of the same line;
- touching or overlapping (gap ≤ 50 mm).

When merging:
- keep the instance with the lowest Mark and delete the others;
- add `merged continuous from 001,002,...` to its Comments;
- if any piece was LOW CONFIDENCE, the merged beam inherits the flag.

Different types on one line stay separate (for example an OV2 cantilever continuing a B3).

**Evidence.** Run in Revit 2026 in one script over all four floors: 441 merged runs, and instance count went from about 2,330 to 904. The call *looked* like a timeout because Revit opened the warning **"Can't keep elements joined"**. The user clicked **Unjoin** and the change committed. A follow-up count confirmed it: `ST-BM-L01 307; L02 166; L03 287; L04 144 merged:441`.

**Failure cases:**
- Beams of the same type that continue across a dilatation (expansion) joint must NOT be merged. Check for a joint before merging (I had none on these floors).
- Very long merged members (one is 51 m) are fine for modelling and quantities. If anyone later needs per-span data, it lives in the drawings, not in the instance split.

**Status.** [VERIFIED] mechanically. User acceptance of the visual result is pending.

**Skill impact.** This **corrects** the old guidance: "merge collinear beams that meet at a column" stays, but "keep secondary beams split where they frame into girders" goes. Default to one instance per continuous run.

---

## 4. Clean joints: how beam ends should meet

**Found.** After the end extensions, joints were geometrically "connected" but looked dirty: notches, stubs and doubled lengths (user image 1). The clean result needs explicit rules for each kind of joint.

| Joint type | How to recognise it | Where the end goes |
|---|---|---|
| **T** (a beam frames into the side of another) | the end is near the other beam's centreline, away from that beam's ends | exactly on the other beam's **centreline** (the end face is hidden inside it) |
| **L-corner** (two beams end at each other) | the crossing point is within about half a width (+100 mm) of the other beam's end | **both** beams extend past the crossing point by the **other** beam's half-width, so the corner square is filled |
| **Collinear, different types** (B4 continuing as B8) | same line, ends overlap or have a gap | both ends meet at one common point (the midpoint of the overlap) |
| **In a column** | end inside the column footprint | leave it; keep the Revit join allowed |

**Evidence.** Run in Revit 2026 on all four floors:
- T-ends snapped: Lt1 403, Lt2 163, Lt3 319, Lt4 169.
- L-corners filled: 90.
- Overlaps from wrongly classified corners: 8, all exactly 400 mm (= 2 × 200 mm half-width), which gave them away. These were really crossings, not corners. They were trimmed to the common point.
- Final audit: 0 overlaps, 0 duplicate marks.

**Failure cases:**
- **A crossing mistaken for a corner.** If a collinear beam continues past the joint, it's a crossing, not an L. Check for a collinear continuation before treating a joint as an L, or run the overlap scan afterwards and trim, as I did.
- **A shallower beam receiving a deeper one at a T.** The deeper beam's end face shows below the shallow one. That's real geometry and is acceptable.

**Status.** [EXPERIMENTAL]: run and counted, but the user hasn't yet looked at the result in 3D.

**Skill impact.** **Adds** a joint-classification step to beam verification. The old skill only said "disallow joins except at columns".

---

## 5. Intent to be flush vs. intentional misalignment

**Found.** On the perimeter rows, the plan draws the beam's outer face line on the same line as the columns' outer face. The beam is *eccentric on purpose* so the façade is flush. In the model, the beams were placed from the plan's beam lines but the columns from the column plan / schedule. These disagree by about 185 mm, so the beams stuck out past the columns. The user: *"[these] are meant to sit flush with the outward facing side of the columns in that grid, check the drawings again."*

**How to tell flush intent from intentional misalignment:**
- **Flush intent (snap it):** the beam is off the column centre by more than 40 mm, its face is within about 300 mm of the column's face on the same side, and the offset points **outward**. Outward means no other column exists beyond it within about 1.8–12 m in that direction (within ±4.5 m along the beam). These are the façade and edge beams.
- **Intentional misalignment (leave it):** interior beams that are eccentric for a reason. Examples: narrow beams (B5 200 wide) passing beside a column, stair and lift beams, beams set off a grid by a dimension, beams at voids. The old skill's examples hold too: KPwBI perimeter beams 120 mm inside, secondary beams at 1A − 1200. **If it's drawn off-grid by a dimension, keep it exactly.**

**Rule when snapping:**
- Snap the beam so its outer face equals the **modelled** column's outer face. The column schedule wins for column size and position.
- Group the collinear run, and use the outermost column face in the run, so the beam stays straight. Where column sizes change (an 800 column next to a 950 column), the beam aligns with the bigger one and the smaller column sits inside.
- Move only between 8 and 320 mm. Append `flush with outer column face (N mm)` to Comments.

**Evidence.** Run in Revit 2026:
- The first, "snap every eccentric beam" version flagged 55 beams + 9 conflicts on Lt1 alone, most of them interior beams that shouldn't move. **It was too broad and I didn't apply it.**
- The perimeter-only, run-grouped version flagged 15 on Lt1 and moved 78 over four floors. For example, the Lt1 B3 row moved from 79660 to 79475, flush with the 950 column face at 79675.

**Failure cases:**
- Moving a girder strands the beams that frame into it (section 1). Re-scan afterwards.
- A U-shaped or stepped building fools the "nothing beyond it" test at re-entrant corners. Review that list.
- If the column itself is in the wrong place, snapping the beam moves the error. Decide first which drawing is right: the schedule or column plan versus the floor plan outline. Here the user's instruction and the column schedule agreed.
- **Misreading the user.** The user wrote "columns like these are meant to sit flush…" but meant *beams*. Confirm from the selection (`get_selected_elements`) and the drawing geometry, not from the wording.

**Status.** Concept: [VERIFIED] by the user's instruction plus the drawing. The perimeter test: [EXPERIMENTAL].

**Skill impact.** **Adds** a "flush intent" section to the drawing-interpretation reference. **Refines** the old principle "model drawn offsets as drawn": an eccentric beam drawn flush with a column face keeps the *relationship* (flush), even when the column position comes from a different sheet than the beam's.

---

## 6. Order of operations matters

Every step can break the previous one, so the order is fixed (all steps run, the order verified in this session):

1. Place from the drawings (already de-duplicated).
2. Check for duplicates and collinear overlaps before anything else.
3. Add missing edge and tie beams (section 2).
4. Extend free ends to supports (section 1).
5. Snap perimeter beams flush (section 5).
6. Merge continuous runs (section 3).
7. Clean the joints (section 4).
8. Re-scan free ends with a ±400 mm search (catches what step 5 broke).
9. Overlap scan, then trim to a common point.
10. Final audit (section 10).

Running the merge before the flush snap would split the snap decision across merged runs. Running the joint clean-up before the merge wastes work on joints that disappear.

---

## 7. Revit mechanics that matter for clean beams

| Finding | Evidence | Status |
|---|---|---|
| Beam created with `NewFamilyInstance(Line, symbol, level, StructuralType.Beam)`; set `Y_JUSTIFICATION=1` (Center) and `Z_JUSTIFICATION=0` (Top); top height via `STRUCTURAL_BEAM_END0/1_ELEVATION` | Run, about 2,300 beams | [VERIFIED] (confirms the old skill) |
| Move or trim by setting `((LocationCurve)el.Location).Curve = Line.CreateBound(a,b)` | Run thousands of times | [VERIFIED] |
| `StructuralFramingUtils.DisallowJoinAtEnd(beam, k)` at ends **not** in a column; `AllowJoinAtEnd` at ends in a column. I had wrongly disallowed joins at *every* end at first and had to re-allow 1,573 column ends | Run | [VERIFIED] (confirms the old skill; add the mistake to troubleshooting) |
| Disallow the join **before** changing the curve, or Revit may raise "Can't keep elements joined" | The dialog appeared during the merge | [EXPERIMENTAL] |
| **Modal dialogs block the API and look exactly like a timeout:** "There are identical instances in the same place" (from duplicate placement) and "Can't keep elements joined". The next call also times out. Ask the user to dismiss it (Unjoin / OK, never Delete), then **count what committed before retrying**, because the change usually did commit | Happened 3 times | [VERIFIED] |
| A timed-out script's result can come back as the reply to the *next* call. Don't trust a reply that doesn't match the script just sent | Seen once | [VERIFIED] |
| Speed: loops of Revit API calls (e.g. `Line.Project` in nested loops) time out. Copying endpoints into plain arrays first, doing the maths, then writing only the changed beams runs in under a second for 700 beams × 700 and over four floors in one call | Run | [VERIFIED] |
| Don't iterate elements after deleting them in the same script (InvalidObject). Collect, delete, then edit | Error seen and fixed | [VERIFIED] |
| `out` is a C# keyword and can't be a variable name | Compile error | [VERIFIED] |

---

## 8. Other drawing-reading findings from this session

- **Sheets shift relative to each other.** One plan page (p43) sat 45.3 pt lower than its sister sheets. My automatic grid alignment locked onto the wrong grid spacing (an error of a whole multiple of about 28 pt) and placed the whole floor wrong. Fix: align each sheet to its own grid with a *constrained* shift search, and check one known column per sheet. Evidence: PDF analysis, then placement checked against the columns. [VERIFIED]. This adds to the existing calibration section.
- **The plan's column outline can disagree with the column schedule and plan** (here by about 185 mm in y, and the outline was not even square). The schedule wins for the column. Beams drawn relative to that outline keep their *relationship* (section 5), not their absolute coordinates. [VERIFIED] on this set.
- **Duplicate detection rows** (the same beam found twice) cause the "identical instances" dialog. De-duplicate the instance table before placement, by type + collinear + overlapping. [VERIFIED]
- **Over-splitting at crossings** also came from the detector cutting runs at every crossing beam. That's now superseded by the merge (section 3).

---

## 9. Suggested workflow text (plain language, for workflows/beams.md)

> After all beams on a floor are placed, run the clean-up in this order and do not skip steps:
> 1. Remove duplicates and overlaps.
> 2. Look for edge beams drawn one-sided or as an outline only, and tie beams across cantilever tips. Model them and tag LOW CONFIDENCE.
> 3. Find every beam end that sits on nothing. Extend it to the nearest column or crossing beam ahead of it (max 4 m). Flag long extensions.
> 4. Make façade beams flush with the outer face of the columns where the drawing shows them flush.
> 5. Join pieces of the same beam on the same line into one beam.
> 6. Tidy every joint: T-ends to the centreline of the supporting beam, corners filled, different beams meeting end to end at one point.
> 7. Check again for loose ends, because steps 4–6 can create new ones.
> 8. Run the audit and show the user the numbers and the list of remaining free ends.

## 10. The audit (what "done" means for a floor)

Report these numbers for each floor:
- **Free ends**, split into cantilever tips (allowed) and others (must be listed with mark and coordinates);
- **Collinear overlaps over 50 mm** (target 0);
- **Duplicate marks** (target 0);
- **Beams passing through a column's interior** without ending in it (review; found 8 on Lt4, still open);
- **Long unsupported spans** (review);
- **Count of LOW CONFIDENCE beams.**

Final numbers in this session:
- duplicate marks 0, overlaps 0;
- non-cantilever free ends: Lt1 7, Lt2 1, Lt3 about 8, Lt4 5. All are listed in the project doc, and some need a user decision (e.g. 800 mm gaps in a Lt4 edge line with no column under them).

Status: audit script [VERIFIED]. The thresholds: [EXPERIMENTAL].

---

## 11. Gaps in the skill that this session exposed

1. There is no definition of a "connected" beam end, and no automated free-end check. Add sections 1 and 10.
2. No joint-cleanliness rules. Add section 4.
3. It says to split secondary beams; the user wants continuous instances. Correct this (section 3).
4. No guidance on flush intent versus deliberate eccentricity. Add section 5.
5. No guidance on edge beams drawn one-sided or as an outline only. Add section 2.
6. No fixed order for the clean-up. Add section 6.
7. Modal dialogs are mentioned only for slab overlaps. Generalise to "any warning dialog freezes the API; count, then retry" (section 7).
8. User-intent handling: the user's words can name the wrong category ("columns" for beams). Always resolve from the selection and the drawing (the old skill's "When the user points at something", strengthened).
9. Perimeter tie beams at cantilever tips: if a row of cantilevers has no edge beam on the drawing but the slab edge runs across their tips, model the tie and flag it, or ask. [THEORY] as a general rule: here it was done under the user's "no floating" instruction.

---

## Core code (C#, Revit 2026, send_code_to_revit)

The connected-end test and the T / L joint classification, stripped down. The full scripts are about 4k characters each.

```csharp
// E[i,0], E[i,1] = beam end points (XYZ, feet); hw[i] = half width; cl = column bounding boxes at this floor
Func<XYZ,bool> inCol = p => cl.Any(bb => p.X>=bb.Min.X-0.07 && p.X<=bb.Max.X+0.07
                                       && p.Y>=bb.Min.Y-0.07 && p.Y<=bb.Max.Y+0.07);
Func<XYZ,int,bool> onBeam = (e,i) => {           // within half width + ~30 mm of another beam's axis, inside its length
  for (int j=0;j<n;j++){ if(j==i) continue;
    var v=E[j,1]-E[j,0]; v=new XYZ(v.X,v.Y,0); double L=v.GetLength(); v=v/L;
    var r=new XYZ(e.X-E[j,0].X,e.Y-E[j,0].Y,0); double s=r.DotProduct(v);
    if(s<-0.1||s>L+0.1) continue;
    if(Math.Abs(r.X*v.Y-r.Y*v.X)<=hw[j]+0.1) return true; }
  return false; };
// Joint: C = intersection of beam i's axis with beam j's axis; sC = position of C along j (0..Lj)
// if C is within (hw[i]+~100 mm) of an end of j  -> L corner: end_i = C + u_i*hw[j];  end_j = C + u_j*hw[i]
// else                                           -> T joint:  end_i = C (on j's centreline)
// Before setting the curve: StructuralFramingUtils.DisallowJoinAtEnd(beam,k) for ends not in a column.
```
