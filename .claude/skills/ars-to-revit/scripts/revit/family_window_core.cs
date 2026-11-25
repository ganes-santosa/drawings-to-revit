// CORE WINDOW FAMILY "KPW_Window" from Metric Window.rft (openings-families.md A5d).
// [VERIFIED 2026-11-25, Revit 2026 scratch model] 40/40 face locks, flex test 8/8 (KPwBI AW01/04/10/11/18/21, GP04, DRC W3);
// project check: AW04/AW18/AW21 placed, size/sill/cut/bbox exact, 0 warnings (after parking hidden mullions).
// Parameters (type): Width, Height, Default Sill Height (template) + Frame Width 50, Frame Depth 100, Columns 1-6,
//   Has Top Light / Top Light Height, Has Bottom Light / Bottom Light Height, Operation (template text: record only).
// Send each STEP as its own send_code_to_revit call. Build at the defaults (Width 3000, Height 2400, Columns 6,
// both lights 400) so that no two planes coincide while locking.

// ===== STEP 1: parameters and formulas (NewFamilyDocument(TPL), own Transaction, SaveAs PATH) =====
//   Pane  = if(Width - (Columns + 1) * Frame Width > Columns * 10 mm, (Width - (Columns + 1) * Frame Width) / Columns, 10 mm)  -> equal panes, never <= 0
//   MkL   = if(Columns > k, Frame Width + k * Pane + (k-1) * Frame Width, Frame Width)   (k = 1..5, from Left)
//   MkR   = if(Columns > k, Frame Width + k * Pane + k * Frame Width, 2 * Frame Width)
//   (hidden mullions are PARKED inside the frame: hidden geometry still counts in the bounding box)
//   Show Mk = Columns > k                                               (Yes/No, drives mullion visibility)
//   TLB = Frame Width + Top Light Height       (from Head: top bar upper face)
//   TLT = 2 * Frame Width + Top Light Height   (from Head: top bar lower face)
//   BLT = Frame Width + Bottom Light Height    (from Sill: bottom bar lower face)
//   BLB = 2 * Frame Width + Bottom Light Height(from Sill: bottom bar upper face)
// Code used:
//   Func<string,ForgeTypeId,FamilyParameter> P = (n,s) => fm.AddParameter(n, GroupTypeId.Construction, s, false);
//   SpecTypeId.Length / SpecTypeId.Int.Integer / SpecTypeId.Boolean.YesNo ; fm.SetFormula(p, "...")

// ===== STEP 2: reference planes + labelled dimensions (OpenDocumentFile, own Transaction, Save) =====
//   Frame Left/Right (from Left/Right, label Frame Width), Frame Bottom/Top (from Sill/Head, Frame Width),
//   Mullion k L / Mullion k R (from Left, labels MkL / MkR), Top Bar Upper/Lower (from Head, TLB/TLT),
//   Bottom Bar Lower/Upper (from Sill, BLT/BLB).
//   Vertical plane:   fd.FamilyCreate.NewReferencePlane(new XYZ(x,0,0), new XYZ(x,0,10), XYZ.BasisY, exteriorElevation)
//   Horizontal plane: fd.FamilyCreate.NewReferencePlane(new XYZ(-8,0,z), new XYZ(8,0,z), XYZ.BasisY, exteriorElevation)
//   Dimension: ReferenceArray { templatePlane.GetReference(), newPlane.GetReference() } -> NewDimension(view, line, ra).FamilyLabel = param
//   Create each plane at its computed position (read the formula value with fm.CurrentType.AsDouble) before labelling.

// ===== STEP 3: extrusions (sketch planes normal Y; frame parts y=-50 end=Frame Depth, glass y=-4 end 8 mm) =====
//   frame = outer rect (Left,Sill)-(Right,Head) + inner rect (Frame Left,Frame Bottom)-(Frame Right,Frame Top)
//   glass = inner rect;  mullion k = (Mullion k L, Frame Bottom)-(Mullion k R, Frame Top), visible = Show Mk
//   top bar = (Frame Left, Top Bar Lower)-(Frame Right, Top Bar Upper), visible = Has Top Light; bottom bar likewise
//   fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(BuiltInParameter.EXTRUSION_END_PARAM), Frame Depth)
//   fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(BuiltInParameter.IS_VISIBLE_PARAM), <Yes/No param>)
//   Subcategories: Frame/Mullion, Glass.

// ===== STEP 4: lock every X/Z planar face to the one reference plane at its position (±0.5 mm) =====
//   Options { ComputeReferences = true }; NewAlignment(exteriorElevation, plane.GetReference(), face.Reference).IsLocked = true
//   Abort if a face matches 0 or >1 planes. Expect 40 locks.

// ===== STEP 5: flex test (Transaction, RollBack) =====
//   Per catalog case set Width/Height/Sill/Columns/lights, Regenerate, compare bounding boxes:
//   frame ±W/2, sill..sill+H; mullion k x = -W/2 + f + k*pane + (k-1)*f .. +f ; visible iff Columns > k;
//   top bar z = sill+H-2f-TL .. sill+H-f-TL; bottom bar z = sill+f+BL .. sill+2f+BL. Tolerance 0.6 mm. All must pass.
