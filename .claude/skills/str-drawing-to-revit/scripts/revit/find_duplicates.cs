// find_duplicates.cs : read-only. Finds elements placed twice (e.g. after a batch was re-run or retried
// after a timeout) and duplicate/blank Marks, for columns, framing, floors and foundations.
// Duplicate = same category + same type + same bounding box within 10 mm. [THEORY]: not yet run.
// Use after every retried batch and in every review (model-validation.md #2, #3). Delete nothing without the user's OK.
var sb = new System.Text.StringBuilder(); double r = 304.8 / 10;   // feet -> 10 mm units
var cats = new[] { BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_StructuralFraming, BuiltInCategory.OST_Floors, BuiltInCategory.OST_StructuralFoundation };
int dupGeo = 0, dupMark = 0, blank = 0;
foreach (var cat in cats) {
    var els = new FilteredElementCollector(document).OfCategory(cat).WhereElementIsNotElementType().ToElements();
    var geo = new Dictionary<string, List<Element>>(); var marks = new Dictionary<string, List<Element>>();
    foreach (var e in els) {
        var bb = e.get_BoundingBox(null); if (bb == null) continue;
        string k = e.GetTypeId() + "|" + Math.Round(bb.Min.X * r) + "," + Math.Round(bb.Min.Y * r) + "," + Math.Round(bb.Min.Z * r)
                 + "|" + Math.Round(bb.Max.X * r) + "," + Math.Round(bb.Max.Y * r) + "," + Math.Round(bb.Max.Z * r);
        if (!geo.ContainsKey(k)) geo[k] = new List<Element>(); geo[k].Add(e);
        var mp = e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK); string m = mp != null ? mp.AsString() : null;
        if (string.IsNullOrWhiteSpace(m)) { blank++; continue; }
        if (!marks.ContainsKey(m)) marks[m] = new List<Element>(); marks[m].Add(e);
    }
    foreach (var g in geo.Values.Where(x => x.Count > 1)) {
        dupGeo += g.Count - 1;
        sb.AppendLine(cat + " SAME PLACE: " + string.Join(",", g.Select(x => x.Id.ToString())));
    }
    foreach (var kv in marks.Where(x => x.Value.Count > 1)) {
        dupMark += kv.Value.Count - 1;
        sb.AppendLine(cat + " MARK " + kv.Key + ": " + string.Join(",", kv.Value.Select(x => x.Id.ToString())));
    }
}
sb.Insert(0, "Placed twice " + dupGeo + ", duplicate marks " + dupMark + ", blank marks " + blank + "\n");
return sb.ToString();
