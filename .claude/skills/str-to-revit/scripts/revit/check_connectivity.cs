// check_connectivity.cs : read-only report of free beam ends and unsupported columns.
// Rule [VERIFIED RSUD] (field report 2026-11-23): an end is connected if (a) inside a column/wall footprint
// +-20 mm at the right height, or (b) within the other beam's half-width + 30 mm of its centreline, between
// its ends, AND on the same floor (the two beams overlap in height). CANTILEVER in Comments = allowed free.
// 2026-11-25: height tests added (before, beams stacked in plan on different floors counted as connected);
// "column top below beam soffit" reported. Script version [THEORY]: not yet run (building-logic.md section 6).
// Limit: heights come from bounding boxes, so sloped members get a loose height test.
var sb = new System.Text.StringBuilder();
double ft = 304.8, tc = 20 / ft, tb = 30 / ft;
Func<BuiltInCategory, IList<Element>> get = c => new FilteredElementCollector(document).OfCategory(c).WhereElementIsNotElementType().ToElements();
var cols = get(BuiltInCategory.OST_StructuralColumns); var fdn = get(BuiltInCategory.OST_StructuralFoundation);
var walls = new FilteredElementCollector(document).OfClass(typeof(Wall)).ToElements();
var bm = new List<Element>(); var A = new List<XYZ>(); var B = new List<XYZ>();
var hw = new List<double>(); var lo = new List<double>(); var hi = new List<double>();
foreach (var e in get(BuiltInCategory.OST_StructuralFraming)) {
    var lc = e.Location as LocationCurve; var bb = e.get_BoundingBox(null);
    if (lc == null || !(lc.Curve is Line) || bb == null) continue;
    var s = document.GetElement(e.GetTypeId()) as FamilySymbol; Parameter w = null;
    if (s != null) w = s.LookupParameter("b") ?? s.LookupParameter("Width") ?? s.LookupParameter("bf");
    bm.Add(e); A.Add(lc.Curve.GetEndPoint(0)); B.Add(lc.Curve.GetEndPoint(1)); lo.Add(bb.Min.Z); hi.Add(bb.Max.Z);
    hw.Add(w != null && w.AsDouble() > 0 ? w.AsDouble() / 2 : 150 / ft);
}
// e holds p: p inside e's plan footprint +-t, and height range [zl,zh] overlaps e's height +-t
Func<Element, XYZ, double, double, double, bool> holds = (e, p, zl, zh, t) => {
    var b = e.get_BoundingBox(null); if (b == null) return false;
    return p.X >= b.Min.X - t && p.X <= b.Max.X + t && p.Y >= b.Min.Y - t && p.Y <= b.Max.Y + t && zh >= b.Min.Z - t && zl <= b.Max.Z + t;
};
Func<Element, string> info = e => {
    var m = e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK); var c = e.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS);
    return e.Id + "|" + (m != null ? m.AsString() : "") + "|" + (c != null ? c.AsString() : "");
};
int n = bm.Count, free = 0, cant = 0;
sb.AppendLine("FREE BEAM ENDS (id|mark|comments|end|x,y,z mm|why)");
for (int i = 0; i < n; i++) {
    string inf = info(bm[i]); bool isCant = inf.ToUpper().Contains("CANTILEVER");
    for (int k = 0; k < 2; k++) {
        XYZ p = k == 0 ? A[i] : B[i]; bool ok = false; string why = "no support";
        foreach (var c in cols) {   // column must reach the beam soffit; a column starting on top of the beam does not count
            if (holds(c, p, lo[i], lo[i], tc)) { ok = true; break; }
            if (holds(c, p, -1e9, lo[i], tc)) why = "column top below beam soffit";
        }
        if (!ok) foreach (var w in walls) if (holds(w, p, lo[i], hi[i], tc)) { ok = true; break; }
        for (int j = 0; j < n && !ok; j++) {
            if (j == i || hi[i] < lo[j] - tb || lo[i] > hi[j] + tb) continue;   // other floor
            var v = new XYZ(B[j].X - A[j].X, B[j].Y - A[j].Y, 0); double L = v.GetLength(); if (L < 1e-6) continue; v = v / L;
            var r = new XYZ(p.X - A[j].X, p.Y - A[j].Y, 0); double s = r.DotProduct(v);
            if (s < -tb || s > L + tb) continue;
            if (Math.Abs(r.X * v.Y - r.Y * v.X) <= hw[j] + tb) ok = true;
        }
        if (ok) continue;
        if (isCant) { cant++; continue; }
        free++; sb.AppendLine(inf + "|" + k + "|" + Math.Round(p.X * ft) + "," + Math.Round(p.Y * ft) + "," + Math.Round(p.Z * ft) + "|" + why);
    }
}
int noBase = 0;
sb.AppendLine("COLUMNS WITHOUT SUPPORT BELOW (id|mark|comments|base z mm)");
foreach (var c in cols) {
    var bb = c.get_BoundingBox(null); if (bb == null) continue;
    var q = new XYZ((bb.Min.X + bb.Max.X) / 2, (bb.Min.Y + bb.Max.Y) / 2, bb.Min.Z - tc); bool ok = false;
    foreach (var f in fdn) if (holds(f, q, q.Z, q.Z, tc)) { ok = true; break; }
    if (!ok) foreach (var o in cols) if (o.Id != c.Id && holds(o, q, q.Z, q.Z, tc)) { ok = true; break; }
    if (!ok) foreach (var o in bm) if (holds(o, q, q.Z, q.Z, tc)) { ok = true; break; }
    if (!ok) foreach (var w in walls) if (holds(w, q, q.Z, q.Z, tc)) { ok = true; break; }
    if (!ok) { noBase++; sb.AppendLine(info(c) + "|" + Math.Round(bb.Min.Z * ft)); }
}
sb.Insert(0, "Beams " + n + ", free ends " + free + " (cantilever tips " + cant + "); columns " + cols.Count + ", without support below " + noBase + "\n");
return sb.ToString();
