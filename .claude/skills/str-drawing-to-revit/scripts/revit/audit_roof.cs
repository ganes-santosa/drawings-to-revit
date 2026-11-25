// audit_roof.cs : read-only 3D audit of roof framing (roof-framing.md B5b). [THEORY]: not yet run.
// Scope: framing members whose Mark starts with PREFIX (edit below), or all framing above ZMIN_MM.
// An end is connected if, in 3D, it lies within (both members' half-depths + 30 mm) of the other member's
// location line (arcs are split into short segments), or inside a column / wall bounding box +-20 mm.
// CANTILEVER in Comments = allowed free end. Also lists members shorter than 100 mm.
string PREFIX = "RF-"; double ZMIN_MM = 1e9;   // e.g. PREFIX = ""; ZMIN_MM = 14000 to audit everything above +14.000
var sb = new System.Text.StringBuilder(); double ft = 304.8, tb = 30 / ft, tc = 20 / ft;
var fr = new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements();
var sup = new FilteredElementCollector(document).WherePasses(new LogicalOrFilter(new ElementCategoryFilter(BuiltInCategory.OST_StructuralColumns),
    new ElementCategoryFilter(BuiltInCategory.OST_Walls))).WhereElementIsNotElementType().ToElements().Select(e => e.get_BoundingBox(null)).Where(b => b != null).ToList();
var mem = new List<Element>(); var segA = new List<XYZ>(); var segB = new List<XYZ>(); var segM = new List<int>(); var hd = new List<double>();
foreach (var e in fr) {
    var lc = e.Location as LocationCurve; if (lc == null) continue;
    var mk = e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK); string m = mk != null ? (mk.AsString() ?? "") : "";
    bool inScope = (PREFIX != "" && m.StartsWith(PREFIX)) || Math.Min(lc.Curve.GetEndPoint(0).Z, lc.Curve.GetEndPoint(1).Z) * ft >= ZMIN_MM;
    if (!inScope) continue;
    var s = document.GetElement(e.GetTypeId()) as FamilySymbol; Parameter d = null;
    if (s != null) d = s.LookupParameter("d") ?? s.LookupParameter("h") ?? s.LookupParameter("Height");
    int k = mem.Count; mem.Add(e); hd.Add(d != null && d.AsDouble() > 0 ? d.AsDouble() / 2 : 150 / ft);
    var pts = lc.Curve is Line ? new List<XYZ> { lc.Curve.GetEndPoint(0), lc.Curve.GetEndPoint(1) } : lc.Curve.Tessellate().ToList();
    for (int i = 0; i + 1 < pts.Count; i++) { segA.Add(pts[i]); segB.Add(pts[i + 1]); segM.Add(k); }
}
Func<XYZ, XYZ, XYZ, double> dist = (p, a, b) => {
    var ab = b - a; double L2 = ab.DotProduct(ab); if (L2 < 1e-12) return p.DistanceTo(a);
    double t = Math.Max(0, Math.Min(1, (p - a).DotProduct(ab) / L2)); return p.DistanceTo(a + ab * t);
};
int free = 0, cant = 0, shortm = 0;
sb.AppendLine("FREE ENDS (id|mark|end|x,y,z mm)  /  SHORT (id|mark|length mm)");
for (int k = 0; k < mem.Count; k++) {
    var e = mem[k]; var c = ((LocationCurve)e.Location).Curve;
    var mk = e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK); var cm = e.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS);
    string id = e.Id + "|" + (mk != null ? mk.AsString() : ""); bool isCant = cm != null && (cm.AsString() ?? "").ToUpper().Contains("CANTILEVER");
    if (c.Length * ft < 100) { shortm++; sb.AppendLine("SHORT|" + id + "|" + Math.Round(c.Length * ft)); }
    for (int end = 0; end < 2; end++) {
        var p = c.GetEndPoint(end); bool ok = false;
        foreach (var b in sup) if (p.X >= b.Min.X - tc && p.X <= b.Max.X + tc && p.Y >= b.Min.Y - tc && p.Y <= b.Max.Y + tc && p.Z >= b.Min.Z - tc && p.Z <= b.Max.Z + tc) { ok = true; break; }
        for (int i = 0; i < segA.Count && !ok; i++) {
            if (segM[i] == k) continue;
            if (dist(p, segA[i], segB[i]) <= hd[segM[i]] + hd[k] + tb) ok = true;   // both half-depths: a purlin sits on top of its rafter
        }
        if (ok) continue;
        if (isCant) { cant++; continue; }
        free++; sb.AppendLine("FREE|" + id + "|" + end + "|" + Math.Round(p.X * ft) + "," + Math.Round(p.Y * ft) + "," + Math.Round(p.Z * ft));
    }
}
sb.Insert(0, "Roof members " + mem.Count + ": free ends " + free + " (cantilever " + cant + "), short members " + shortm + "\n");
return sb.ToString();
