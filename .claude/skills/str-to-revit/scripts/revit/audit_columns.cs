// audit_columns.cs : read-only column audit (columns.md B6). [THEORY]: not yet run.
// Per column: the column directly above it in the same stack (plan distance <= 300 mm, nearest base above).
// Reports stack gaps or overlaps > 5 mm, stack shifts in plan > 20 mm (review: drawn offset or error?),
// columns with no column above and no beam or slab reaching their top (column top floats), LOW CONFIDENCE count.
// Duplicates and marks: find_duplicates.cs. Column base support and short columns: check_connectivity.cs.
var sb = new System.Text.StringBuilder(); double ft = 304.8, t5 = 5 / ft, t20 = 20 / ft, near = 300 / ft;
var cs = new FilteredElementCollector(document).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().ToElements()
    .Where(e => e.get_BoundingBox(null) != null).ToList();
var tops = new FilteredElementCollector(document).WherePasses(new LogicalOrFilter(new ElementCategoryFilter(BuiltInCategory.OST_StructuralFraming),
    new ElementCategoryFilter(BuiltInCategory.OST_Floors))).WhereElementIsNotElementType().ToElements().Where(e => e.get_BoundingBox(null) != null).ToList();
int n = cs.Count, gaps = 0, shifts = 0, floatTop = 0, low = 0;
var P = new XYZ[n]; var lo = new double[n]; var hi = new double[n]; var id = new string[n];
for (int i = 0; i < n; i++) {
    var bb = cs[i].get_BoundingBox(null); var lp = cs[i].Location as LocationPoint;
    P[i] = lp != null ? lp.Point : (bb.Min + bb.Max) / 2; lo[i] = bb.Min.Z; hi[i] = bb.Max.Z;
    var m = cs[i].get_Parameter(BuiltInParameter.ALL_MODEL_MARK); var c = cs[i].get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS);
    id[i] = cs[i].Id + "|" + (m != null ? m.AsString() : "");
    if (c != null && (c.AsString() ?? "").ToUpper().Contains("LOW CONFIDENCE")) low++;
}
sb.AppendLine("ISSUES (id|mark|issue|value mm)");
for (int i = 0; i < n; i++) {
    int up = -1; double best = 1e9;
    for (int j = 0; j < n; j++) {
        if (j == i || lo[j] <= lo[i] + t20) continue;
        double d = Math.Sqrt(Math.Pow(P[j].X - P[i].X, 2) + Math.Pow(P[j].Y - P[i].Y, 2));
        if (d <= near && lo[j] < best) { best = lo[j]; up = j; }
    }
    if (up >= 0) {
        double gap = lo[up] - hi[i], sh = Math.Sqrt(Math.Pow(P[up].X - P[i].X, 2) + Math.Pow(P[up].Y - P[i].Y, 2));
        if (Math.Abs(gap) > t5) { gaps++; sb.AppendLine(id[i] + "|" + (gap > 0 ? "GAP to column above" : "OVERLAP with column above") + "|" + Math.Round(gap * ft)); }
        if (sh > t20) { shifts++; sb.AppendLine(id[i] + "|STACK SHIFT (check drawing)|" + Math.Round(sh * ft)); }
        continue;
    }
    var bc = cs[i].get_BoundingBox(null); bool held = false;   // top: a beam or slab must reach it
    foreach (var t in tops) {
        var b = t.get_BoundingBox(null);
        if (b.Min.X <= bc.Max.X + t20 && b.Max.X >= bc.Min.X - t20 && b.Min.Y <= bc.Max.Y + t20 && b.Max.Y >= bc.Min.Y - t20
            && b.Max.Z >= hi[i] - t20 && b.Min.Z <= hi[i] + t20) { held = true; break; }
    }
    if (!held) { floatTop++; sb.AppendLine(id[i] + "|TOP FREE (no beam, slab or column above)|" + Math.Round(hi[i] * ft)); }
}
sb.Insert(0, "Columns " + n + ": stack gaps/overlaps " + gaps + ", stack shifts " + shifts + ", free tops " + floatTop + ", LOW CONFIDENCE " + low + "\n");
return sb.ToString();
