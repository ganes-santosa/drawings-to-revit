// check_connectivity.cs : read-only report of free beam ends and unsupported columns.
// Rule [VERIFIED RSUD] (assets/field-reports/2026-11-23-rsud-cakung-beam-cleanliness.md):
//  end connected if (a) inside a column bbox +-20 mm at its height, or (b) within the other beam's
//  half-width + 30 mm of its centreline AND between that beam's two ends. CANTILEVER in Comments = allowed free.
// This script version: [THEORY] - not yet run. Record the first run in references/building-logic.md section 6.
// Paste into send_code_to_revit. Maths on arrays first (fast), Revit calls only to read.
var sb = new System.Text.StringBuilder();
double ft = 304.8, tc = 20 / ft, tb = 30 / ft;
var cols = new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().ToElements();
var fdn = new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFoundation).WhereElementIsNotElementType().ToElements();
var walls = new FilteredElementCollector(document).OfClass(typeof(Wall)).ToElements();
var all = new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements();
var bm = new List<Element>(); var A = new List<XYZ>(); var B = new List<XYZ>(); var hw = new List<double>();
foreach (var e in all) {
    var lc = e.Location as LocationCurve; if (lc == null || !(lc.Curve is Line)) continue;
    var s = document.GetElement(e.GetTypeId()) as FamilySymbol; Parameter w = null;
    if (s != null) w = s.LookupParameter("b") ?? s.LookupParameter("Width") ?? s.LookupParameter("bf");
    bm.Add(e); A.Add(lc.Curve.GetEndPoint(0)); B.Add(lc.Curve.GetEndPoint(1));
    hw.Add(w != null && w.AsDouble() > 0 ? w.AsDouble() / 2 : 150 / ft);
}
Func<Element, XYZ, double, bool> inBox = (e, p, t) => {
    var b = e.get_BoundingBox(null); if (b == null) return false;
    return p.X >= b.Min.X - t && p.X <= b.Max.X + t && p.Y >= b.Min.Y - t && p.Y <= b.Max.Y + t && p.Z >= b.Min.Z - t && p.Z <= b.Max.Z + t;
};
Func<Element, string> info = e => {
    var m = e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK); var c = e.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS);
    return e.Id + "|" + (m != null ? m.AsString() : "") + "|" + (c != null ? c.AsString() : "");
};
int n = bm.Count, free = 0, cant = 0;
sb.AppendLine("FREE BEAM ENDS (id|mark|comments|end|x,y,z mm)");
for (int i = 0; i < n; i++) {
    string inf = info(bm[i]); bool isCant = inf.ToUpper().Contains("CANTILEVER");
    for (int k = 0; k < 2; k++) {
        XYZ p = k == 0 ? A[i] : B[i]; bool ok = false;
        foreach (var c in cols) if (inBox(c, p, tc)) { ok = true; break; }
        if (!ok) foreach (var w in walls) if (inBox(w, p, tc)) { ok = true; break; }
        for (int j = 0; j < n && !ok; j++) {
            if (j == i) continue;
            var v = new XYZ(B[j].X - A[j].X, B[j].Y - A[j].Y, 0); double L = v.GetLength(); if (L < 1e-6) continue; v = v / L;
            var r = new XYZ(p.X - A[j].X, p.Y - A[j].Y, 0); double s = r.DotProduct(v);
            if (s < -tb || s > L + tb) continue;
            if (Math.Abs(r.X * v.Y - r.Y * v.X) <= hw[j] + tb) ok = true;
        }
        if (ok) continue;
        if (isCant) { cant++; continue; }
        free++; sb.AppendLine(inf + "|" + k + "|" + Math.Round(p.X * ft) + "," + Math.Round(p.Y * ft) + "," + Math.Round(p.Z * ft));
    }
}
int noBase = 0;
sb.AppendLine("COLUMNS WITHOUT SUPPORT BELOW (id|mark|comments|base z mm)");
foreach (var c in cols) {
    var bb = c.get_BoundingBox(null); if (bb == null) continue;
    var q = new XYZ((bb.Min.X + bb.Max.X) / 2, (bb.Min.Y + bb.Max.Y) / 2, bb.Min.Z - tc); bool ok = false;
    foreach (var f in fdn) if (inBox(f, q, tc)) { ok = true; break; }
    if (!ok) foreach (var o in cols) if (o.Id != c.Id && inBox(o, q, tc)) { ok = true; break; }
    if (!ok) foreach (var o in bm) if (inBox(o, q, tc)) { ok = true; break; }
    if (!ok) foreach (var w in walls) if (inBox(w, q, tc)) { ok = true; break; }
    if (!ok) { noBase++; sb.AppendLine(info(c) + "|" + Math.Round(bb.Min.Z * ft)); }
}
sb.Insert(0, "Beams " + n + ", free ends " + free + " (cantilever tips " + cant + "); columns " + cols.Count + ", without support below " + noBase + "\n");
return sb.ToString();
