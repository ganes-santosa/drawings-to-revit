// check_connectivity.cs : report floating beam ends and unsupported columns.
// Status: [THEORY] - written 2026-11-20, NOT yet run in Revit. After the first run, record the result
// in references/building-logic.md section 6 and promote or fix.
// Use: paste the body into send_code_to_revit. Read-only (creates/changes nothing).
// Written for the KPwBI host quirks: no LINQ, no local functions, Func<> lambdas, double literals.
var sb = new System.Text.StringBuilder();
double ft = 304.8;
double tolSup = 50 / ft;    // beam end to column/wall bounding box
double tolBeam = 200 / ft;  // beam end to another beam's centreline
var cols = new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().ToElements();
var beams = new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements();
var walls = new FilteredElementCollector(document).OfClass(typeof(Wall)).ToElements();
var fdn = new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFoundation).WhereElementIsNotElementType().ToElements();

Func<Element, XYZ, double, bool> inBox = (e, p, t) => {
    var b = e.get_BoundingBox(null);
    if (b == null) return false;
    return p.X >= b.Min.X - t && p.X <= b.Max.X + t && p.Y >= b.Min.Y - t && p.Y <= b.Max.Y + t && p.Z >= b.Min.Z - t && p.Z <= b.Max.Z + t;
};
Func<Element, string> info = (e) => {
    var m = e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK);
    var c = e.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS);
    return e.Id + "|" + (m != null ? m.AsString() : "") + "|" + (c != null ? c.AsString() : "");
};

int floating = 0, checkedEnds = 0;
sb.AppendLine("FLOATING BEAM ENDS (id|mark|comments|end|x,y,z mm)");
foreach (var bm in beams) {
    var lc = bm.Location as LocationCurve;
    if (lc == null) continue;
    string inf = info(bm);
    if (inf.ToUpper().Contains("CANTILEVER")) continue;
    for (int i = 0; i < 2; i++) {
        XYZ p = lc.Curve.GetEndPoint(i);
        checkedEnds++;
        bool ok = false;
        foreach (var c in cols) { if (inBox(c, p, tolSup)) { ok = true; break; } }
        if (!ok) foreach (var w in walls) { if (inBox(w, p, tolSup)) { ok = true; break; } }
        if (!ok) foreach (var o in beams) {
            if (o.Id == bm.Id) continue;
            var ol = o.Location as LocationCurve;
            if (ol != null && ol.Curve.Distance(p) <= tolBeam) { ok = true; break; }
        }
        if (!ok) {
            floating++;
            sb.AppendLine(inf + "|" + i + "|" + Math.Round(p.X * ft) + "," + Math.Round(p.Y * ft) + "," + Math.Round(p.Z * ft));
        }
    }
}

int noBase = 0;
sb.AppendLine("COLUMNS WITHOUT SUPPORT BELOW (id|mark|comments|base z mm)");
foreach (var c in cols) {
    var bb = c.get_BoundingBox(null);
    if (bb == null) continue;
    XYZ basePt = new XYZ((bb.Min.X + bb.Max.X) / 2, (bb.Min.Y + bb.Max.Y) / 2, bb.Min.Z - tolSup);
    bool ok = false;
    foreach (var f in fdn) { if (inBox(f, basePt, tolSup)) { ok = true; break; } }
    if (!ok) foreach (var o in cols) { if (o.Id != c.Id && inBox(o, basePt, tolSup)) { ok = true; break; } }
    if (!ok) foreach (var o in beams) { if (inBox(o, basePt, tolSup)) { ok = true; break; } }
    if (!ok) foreach (var w in walls) { if (inBox(w, basePt, tolSup)) { ok = true; break; } }
    if (!ok) { noBase++; sb.AppendLine(info(c) + "|" + Math.Round(bb.Min.Z * ft)); }
}

sb.Insert(0, "Beam ends checked: " + checkedEnds + ", floating: " + floating + "; columns: " + cols.Count + ", without support below: " + noBase + "\n");
return sb.ToString();
