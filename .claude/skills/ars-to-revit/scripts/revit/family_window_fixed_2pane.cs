// Parametric window family: fixed 2-pane (frame + centre mullion + glass), built from Metric Window.rft.
// [VERIFIED 2026-11-25, Revit 2026 scratch model] 16/16 face locks, flex test 5/5, placed + cut, 0 warnings.
// Send each STEP as its own send_code_to_revit call (bridge limit ~4k chars). Edit TPL / PATH first.
// Ids printed by STEP 2 are needed in STEP 3 and 4. Reference: references/openings-families.md A5.

// ===== STEP 1: parameters + reference planes, SaveAs =====
var app = document.Application; double mm = 1/304.8;
string TPL = @"D:\ProgramData\Autodesk\RVT 2026\Family Templates\English\Metric Window.rft";
string PATH = @"D:\Outpost\Coding\str-to-revit\families\Windows\KPW_Window-Fixed-2Pane.rfa";
System.IO.Directory.CreateDirectory(System.IO.Path.GetDirectoryName(PATH));
Document fd = app.NewFamilyDocument(TPL);           // own document + own Transaction (works from the tool)
try {
  var fm = fd.FamilyManager;
  View ext = new FilteredElementCollector(fd).OfClass(typeof(View)).Cast<View>().First(v => v.ViewType == ViewType.Elevation && v.Name == "Exterior");
  using (var t = new Transaction(fd, "params")) { t.Start();
    if (fm.CurrentType == null) fm.NewType("Default");
    var pFW = fm.AddParameter("Frame Width", GroupTypeId.Construction, SpecTypeId.Length, false);
    var pFD = fm.AddParameter("Frame Depth", GroupTypeId.Construction, SpecTypeId.Length, false);
    var pHF = fm.AddParameter("Half Frame", GroupTypeId.Construction, SpecTypeId.Length, false);
    fm.Set(pFW, 50*mm); fm.Set(pFD, 100*mm); fm.SetFormula(pHF, "Frame Width / 2");
    Func<string, ReferencePlane> RP = n => new FilteredElementCollector(fd).OfClass(typeof(ReferencePlane)).Cast<ReferencePlane>().First(r => r.Name == n);
    var L = RP("Left"); var R = RP("Right"); var S = RP("Sill"); var H = RP("Head"); var C = RP("Center (Left/Right)");
    double f = 50*mm;
    Func<string,double,ReferencePlane> VP = (n,x) => { var p = fd.FamilyCreate.NewReferencePlane(new XYZ(x,0,0), new XYZ(x,0,10), XYZ.BasisY, ext); p.Name = n; return p; };
    Func<string,double,ReferencePlane> HP = (n,z) => { var p = fd.FamilyCreate.NewReferencePlane(new XYZ(-6,0,z), new XYZ(6,0,z), XYZ.BasisY, ext); p.Name = n; return p; };
    var fL = VP("Frame Left", L.BubbleEnd.X+f); var fR = VP("Frame Right", R.BubbleEnd.X-f);
    var fB = HP("Frame Bottom", S.BubbleEnd.Z+f); var fT = HP("Frame Top", H.BubbleEnd.Z-f);
    var mL = VP("Mullion Left", -f/2); var mR = VP("Mullion Right", f/2);
    fd.Regenerate();
    Action<ReferencePlane,ReferencePlane,bool,double,FamilyParameter> Dim = (a,b,vert,pos,par) => {
      var ra = new ReferenceArray(); ra.Append(a.GetReference()); ra.Append(b.GetReference());
      Line ln = vert ? Line.CreateBound(new XYZ(-6,0,pos), new XYZ(6,0,pos)) : Line.CreateBound(new XYZ(pos,0,-1), new XYZ(pos,0,12));
      fd.FamilyCreate.NewDimension(ext, ln, ra).FamilyLabel = par; };   // template plane first: the new plane moves
    Dim(L,fL,true,9.0,pFW); Dim(R,fR,true,9.0,pFW); Dim(S,fB,false,-2.5,pFW); Dim(H,fT,false,-2.5,pFW);
    Dim(C,mL,true,9.5,pHF); Dim(C,mR,true,9.5,pHF);
    t.Commit(); }
  var so = new SaveAsOptions(); so.OverwriteExistingFile = true; fd.SaveAs(PATH, so);
} finally { fd.Close(false); }
return "step1 ok";

// ===== STEP 2: extrusions (frame with inner loop, mullion, glass), subcategories, depth parameter =====
// Open PATH with app.OpenDocumentFile, own Transaction. Sketch planes normal Y: frame at y=-50 (end = Frame Depth), glass at y=-4 (end 8).
// Frame profile = outer rect (Left,Sill)-(Right,Head) + inner rect (Frame Left,Frame Bottom)-(Frame Right,Frame Top).
// Mullion rect (Mullion Left..Mullion Right) x (Frame Bottom..Frame Top); glass rect = inner frame rect.
// fm.AssociateElementParameterToFamilyParameter(ext.get_Parameter(BuiltInParameter.EXTRUSION_END_PARAM), fm.get_Parameter("Frame Depth"));
// Subcategories in the template: "Frame/Mullion", "Glass". fd.Save(); print the three extrusion ids.

// ===== STEP 3: lock every X/Z face to the reference plane it lies on =====
// var opt = new Options(); opt.ComputeReferences = true;
// for each extrusion -> Solid -> PlanarFace with normal ±X or ±Z: find the reference plane with the same normal whose
// BubbleEnd.X (or .Z) is within 0.5 mm of face.Origin; fd.FamilyCreate.NewAlignment(exteriorElevation, rp.GetReference(), pf.Reference).IsLocked = true;
// Expect 16 locks (frame 8, mullion 4, glass 4), 0 failures. fd.Save().

// ===== STEP 4: flex test (Transaction rolled back, nothing saved) =====
// For each catalog size {W,H,sill,frame}: fm.Set Width/Height/Default Sill Height/Frame Width, fd.Regenerate(),
// check bounding boxes: frame X = ±W/2, Z = sill..sill+H; glass X = ±(W/2-f), Z = sill+f..sill+H-f; mullion X = ±f/2. Tolerance 0.6 mm.
// Do not load the family unless every case passes.

// ===== STEP 5 (project): LoadFamily(PATH, out fam); one call. Then Duplicate the symbol per code,
// set Width / Height / Default Sill Height, WINDOW_TYPE_ID = code (Type Mark), Type Comments = sheet + provenance, Activate.
// Placement: NewFamilyInstance(pt at level z, symbol, wall, level, NonStructural) puts the SILL AT 0:
// set INSTANCE_SILL_HEIGHT_PARAM from the type's Default Sill Height right after placing (openings-placement.md B4).
