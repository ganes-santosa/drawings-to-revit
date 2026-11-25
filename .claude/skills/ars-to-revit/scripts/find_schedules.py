#!/usr/bin/env python3
# SHARED COPY - do not edit here. Edit shared/scripts/find_schedules.py in the repo, then run tools/sync_shared.py
"""Shortlist pages in construction drawing PDFs that hold type schedules/tables, for the
structural (str) or architectural (ars) skill; with --sheets, print a sheet-type map.

Usage:
  python find_schedules.py <pdf or folder> [--element <element>|all] [--top 10] [--discipline str|ars]
  python find_schedules.py <pdf or folder> --sheets          # one line per page: type, sheet no, title
  Elements  str: columns beams slabs foundations roof
            ars: openings walls finishes ceilings floors roofs
  --discipline defaults to the skill this copy sits in (folder name starts with str / ars).

Scores each page by schedule phrases (English + Indonesian) and element keywords and prints
the best candidates with page numbers. It only reads text the PDF really contains: outlined
text and scans return nothing (then read the drawing index, look visually, or ask the user).
Uses PyMuPDF if installed, else the pdftotext command. A shortlist, never the answer.
Shared by both skills: edit only shared/scripts/find_schedules.py, then run tools/sync_shared.py.
"""
import argparse, re, shutil, subprocess, sys
from pathlib import Path

# ----------------------------------------------------------------------------- vocabulary: STR
STR_SCHEDULE = ["schedule", "tabel", "table", "daftar", "tabulasi", "type", "tipe", "penulangan", "pembesian",
                "dimensi", "ukuran", "size", "mark", "kode"]
STR_ELEMENT = {
    "columns": ["kolom", "column", "col.", "k1", "k2", "kc"],
    "beams": ["balok", "beam", "b1", "b2", "g1", "girder", "sloof", "tie beam"],
    "slabs": ["pelat", "plat", "slab", "s1", "s2", "deck", "tebal", "thickness"],
    "foundations": ["pondasi", "fondasi", "foundation", "footing", "pile", "tiang",
                    "pile cap", "poer", "bor pile", "strauss"],
    "roof": ["atap", "roof", "rangka", "truss", "kuda-kuda", "gording", "gordeng", "purlin",
             "rafter", "wf", "cnp", "profil", "trekstang", "trekstank", "trecstang", "sagrod",
             "ikatan angin", "kanopi", "canopy", "baja ringan", "hb", "2l", "lc"],
}
# Table/detail title phrases: the strongest signal. A plan page that merely mentions
# "KOLOM K2 800x800" in labels must not outrank the real table (lesson from the DRC set).
_S = {"columns": r"kolom|column", "beams": r"balok|beam|sloof", "slabs": r"pelat|plat|slab",
      "foundations": r"pondasi|fondasi|foundation|footing|pile ?cap|poer|tiang|bore ?pile",
      "roof": r"atap|roof|kuda[- ]kuda|truss|gording|purlin|kanopi|canopy|crown"}
STR_PHRASES = {k: [r"(tabel|daftar|tabulasi)\s+((penulangan|pembesian|tulangan)\s+)?(" + v + r")",
                   r"(tipe|type)\s+((perkuatan|jacketing|strengthening)\s+)?(" + v + r")",
                   r"detail\s+((penulangan|pembesian)\s+)?(" + v + r")",
                   r"(" + v + r")\s+(schedule|table|type)"] for k, v in _S.items()}
STR_PHRASES["roof"] += [r"(tabel|daftar)\s+profil", r"profil\s+baja", r"denah\s+(pelat\s+)?rangka\s+(atap|crown|kanopi)",
                        r"rencana\s+atap", r"potongan\s+(truss|rangka\s+atap|kuda)", r"detail\s+(tipikal\s+)?gording"]
# steel profiles as written on roof sheets: WF 350x175x7x11, WF.350.175.7.11, C 125.50.20.2,3, 2L 70x70x6
PROFILE = re.compile(r"(?<![a-z])(wf|hb|h|cnp|lc|c|2l|l)\s*[. ]?\s*\d{2,3}(\s*[.x×]\s*\d+(,\d+)?){1,4}")
TITLE = re.compile(r"^(detail|tabel|daftar|denah|potongan|rencana|schedule)\b.*$", re.M)

# ----------------------------------------------------------------------------- vocabulary: ARS
# "kode", "jumlah", "keterangan" left out: they sit in every Indonesian title block (KPwBI).
ARS_SCHEDULE = ["schedule", "jadwal", "skedul", "tabel", "table", "daftar", "tipe", "type",
                "legenda", "legend", "spesifikasi"]
# Column headers of door/window schedule sheets (KPwBI: LOCATION FRAME LEAF / PANEL HARDWARE
# REMARKS FIGURE TYPE). Header words survive even when sizes and codes are outlined text.
HEADERS = ["location", "lokasi", "frame", "kusen", "leaf", "daun", "panel", "hardware", "aksesoris",
           "remarks", "figure", "gambar kerja", "ukuran", "dimensi", "ambang", "sill", "jumlah unit"]
# Door/window codes vary per office (P1, PJ1, J1, BV1, D1, W1, AW-01): a weak signal only.
ARS_ELEMENT = {
    "openings": ["pintu", "jendela", "kusen", "door", "window", "boven", "bouvenlicht", "louvre", "jalusi",
                 "daun pintu", "engsel", "kaca", "glass", "aluminium", "handle", "kunci"],
    "walls": ["dinding", "wall", "partisi", "partition", "bata", "hebel", "bata ringan", "plester", "acian",
              "gypsum", "gipsum", "batako"],
    "finishes": ["finishing", "finish", "material", "granit", "keramik", "homogeneous", "cat", "paint",
                 "vinyl", "parket", "hpl", "plint"],
    "ceilings": ["plafond", "plafon", "ceiling", "rangka hollow", "gypsum board", "acp", "kalsiboard",
                 "list plafond", "drop ceiling"],
    "floors": ["lantai", "floor", "pola lantai", "screed", "granit", "keramik", "peil", "ffl", "+-0.00"],
    "roofs": ["atap", "roof", "genteng", "metal roof", "spandek", "talang", "lisplang", "nok", "dak"],
}
_A = {"openings": r"pintu|jendela|kusen|door|window|bovenlicht|boven|louvre",
      "walls": r"dinding|wall|partisi|partition",
      "finishes": r"finishing|finish|material",
      "ceilings": r"plafond|plafon|ceiling",
      "floors": r"lantai|floor",
      "roofs": r"atap|roof"}
ARS_PHRASES = {k: [r"(schedule|jadwal|skedul|tabel|daftar|rekapitulasi)\s+(tipe\s+|type\s+)?(" + v + r")",
                   r"(tipe|type|detail)\s+(" + v + r")",
                   r"(" + v + r")\s+(schedule|table|type|legend|legenda)",
                   r"(rencana|denah)\s+(" + v + r")"] for k, v in _A.items()}
ARS_PHRASES["openings"] += [r"(kusen|frame)\s+(pintu|jendela|door|window)", r"(pintu|door)\s*(dan|&|and)\s*(jendela|window)"]
ARS_PHRASES["ceilings"] += [r"finishing\s+(plafond|plafon|ceiling)"]  # KPwBI A-43xx
ARS_PHRASES["finishes"] += [r"(tabel|daftar|skedul|jadwal)\s+(material|finishing)", r"(finishing|material)\s+(lantai|dinding|plafond|plafon)"]

ELEMENTS = {"str": STR_ELEMENT, "ars": ARS_ELEMENT}
INDEX = r"daftar\s+gambar|drawing\s+(index|list)|list\s+of\s+drawings"
SHEET_TYPES = [("index", INDEX),
               ("schedule", r"(jadwal|skedul|tabel|daftar|schedule)\s+(tipe\s+|penulangan\s+)?(pintu|jendela|kusen|door|window|finishing|material|dinding|plafond|plafon|kolom|balok|pelat|plat|pondasi|profil)"),
               ("demolition", r"bongk\w*ran|bongkar|demolition|eksisting|existing"),
               ("plan", r"\bdenah\b|\bplan\b|rencana\s+(lantai|atap|plafond|plafon|pola)"),
               ("elevation", r"\btampak\b|elevation"),
               ("section", r"\bpotongan\b|\bsection\b"),
               ("detail", r"\bdetail\b|\bdetil\b"),
               ("3d", r"perspektif|perspective|gambar\s+3d|\b3d\b|render")]


# ----------------------------------------------------------------------------- text
def page_texts(pdf):
    try:
        import pymupdf as fitz  # PyMuPDF >= 1.24
    except ImportError:
        try:
            import fitz
        except ImportError:
            fitz = None
    if fitz is not None:
        with fitz.open(pdf) as doc:
            for i, page in enumerate(doc, 1):
                yield i, page.get_text()
        return
    if not shutil.which("pdftotext"):
        sys.exit("Need PyMuPDF (pip install pymupdf) or pdftotext on PATH")
    out = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True,
                         text=True, encoding="utf-8", errors="replace").stdout
    for i, t in enumerate(out.split("\f"), 1):
        if t.strip():
            yield i, t


def word(k, low, digits=False):
    edge = r"(?<![a-z0-9])" if digits else r"(?<![a-z])"
    return re.search(edge + re.escape(k) + (r"(?![a-z0-9])" if digits else r"(?![a-z])"), low)


# ----------------------------------------------------------------------------- scoring
def score_str(text, element):
    """Structural ranking, tuned on DRC, RSUD, KPwBI, Hunver (columns 4/4, roof 5/5)."""
    low = text.lower()
    kinds = list(_S) if element == "all" else [element]
    p_hits = sorted({m.group(0) for k in kinds for pat in STR_PHRASES[k] for m in re.finditer(pat, low)})  # raw: keeps the tuned scores
    s_hits = [k for k in STR_SCHEDULE if word(k, low)]
    e_hits = [k for k in sum((STR_ELEMENT[k] for k in kinds), []) if word(k, low, digits=True)]
    sizes = len(set(re.findall(r"\d{2,4}\s*[x×]\s*\d{2,4}", low)))  # distinct sizes only
    if element in ("roof", "all"):
        sizes = max(sizes, len({m.group(0) for m in PROFILE.finditer(low)}))
    titles = [m.group(0).strip() for m in TITLE.finditer(low)]
    title_hit = any(re.search(_S[k], t) for k in kinds for t in titles)
    plan_only = any(t.startswith("denah") for t in titles) and not p_hits
    # stair sheets mention kolom/balok bordes: push them down unless they are the target
    stair = any(re.search(r"tangga|bordes|stair", t) for t in titles)
    # "contoh" = example: standard-detail sheets show example tables, not the project's own
    example = bool(re.search(r"contoh\s+(tabel|tabulasi)|example\s+(table|schedule)", low))
    sc = 8 * len(p_hits) + 6 * title_hit + 2 * len(s_hits) + 2 * len(e_hits) + min(sizes, 6) - 6 * plan_only - 12 * stair - 15 * example
    keep = bool(e_hits or p_hits)
    return sc, keep, p_hits, sizes, None, titles


def codes(low):
    """Distinct opening-like codes (P1, PJ-2, J3, BV1, D12, W4, AW-04, PJ1a)."""
    return set(re.findall(r"(?<![a-z0-9])(?:p|pj|pd|j|jd|bv|d|w|aw|dw|l|lv)[-.]?\d{1,3}[a-z]?(?![a-z0-9])", low))


def score_ars(text, element):
    """Architectural ranking, tuned on KPwBI (all 26 door/window schedule pages first)."""
    low = text.lower()
    kinds = list(_A) if element == "all" else [element]
    p_hits = sorted({" ".join(m.group(0).split()) for k in kinds for pat in ARS_PHRASES[k] for m in re.finditer(pat, low)})
    s_hits = [k for k in ARS_SCHEDULE if word(k, low)]
    e_hits = [k for k in sum((ARS_ELEMENT[k] for k in kinds), []) if word(k, low, digits=True)]
    sizes = len(set(re.findall(r"\d{3,4}\s*[x×]\s*\d{3,4}", low)))
    n_codes = len(codes(low)) if "openings" in kinds else 0
    n_head = sum(1 for h in HEADERS if word(h, low)) if "openings" in kinds else 0
    plan_only = bool(re.search(r"\bdenah\b", low)) and not any(re.match(r"(schedule|jadwal|skedul|tabel|daftar)", h) for h in p_hits)
    example = bool(re.search(r"contoh\s+(tabel|jadwal)|example\s+(table|schedule)", low))
    sc = (8 * len(p_hits) + 2 * len(s_hits) + 2 * len(e_hits) + min(sizes, 8) + min(n_codes, 8) // 2 + 2 * min(n_head, 6)
          - 6 * plan_only - 15 * example)
    return sc, bool(p_hits), p_hits, sizes, n_codes, []


# ----------------------------------------------------------------------------- sheet map
SHEET_NO = re.compile(r"(?<![A-Za-z0-9])([A-Z]{1,3}[-.]\d{3,4}[A-Z]?)(?![A-Za-z0-9])")


def sheet_title(text):
    """Sheet number = most frequent code like A-5008; title = words just before it (title block)."""
    one = " ".join(text.split())
    nos = SHEET_NO.findall(one)
    if not nos:
        return "", ""
    no = max(set(nos), key=nos.count)
    best = ""
    for m in re.finditer(re.escape(no), one):
        before = one[max(0, m.start() - 70):m.start()]
        before = re.split(r"SKALA|SCALE|S C A L E|Issue Date|@A\d|1 : \d+", before)[-1].strip()
        if len(before) > len(best):
            best = before
    return no, best


def sheet_type(low, title=""):
    for src in (title.lower(), low):
        hits = [name for name, pat in SHEET_TYPES if src and re.search(pat, src)]
        if hits:
            return hits[0]
    return "?"


def default_discipline():
    name = Path(__file__).resolve().parent.parent.name.lower()
    return "str" if name.startswith("str") else "ars" if name.startswith("ars") else None


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--discipline", choices=["str", "ars"], default=default_discipline())
    ap.add_argument("--element", default="all")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--sheets", action="store_true", help="print a sheet-type map of every page")
    a = ap.parse_args()
    if a.discipline is None and not a.sheets:
        sys.exit("Say --discipline str or ars (this copy is not inside a str/ars skill folder)")
    if not a.sheets and a.element != "all" and a.element not in ELEMENTS[a.discipline]:
        sys.exit(f"--element for {a.discipline}: {', '.join(ELEMENTS[a.discipline])} or all")
    p = Path(a.path)
    pdfs = sorted(p.rglob("*.pdf")) if p.is_dir() else [p]
    if not pdfs:
        sys.exit(f"No PDFs found in {p}")
    score = score_str if a.discipline == "str" else score_ars
    rows, empty, index = [], [], []
    for pdf in pdfs:
        for n, text in page_texts(pdf):
            low = text.lower()
            if len(low.strip()) < 20:
                empty.append(f"{pdf.name} p{n}")
                if a.sheets:
                    print(f"{pdf.name} p{n:<4} (no text)")
                continue
            if a.sheets:
                no, title = sheet_title(text)
                print(f"{pdf.name} p{n:<4} {sheet_type(low, title):<10} {no:<8} {title[:80]}")
                continue
            if re.search(INDEX, low):
                index.append(f"{pdf.name} p{n}")
            sc, keep, ph, sz, nc, titles = score(text, a.element)
            if sc > 0 and keep:
                rows.append((sc, pdf, n, ph, sz, nc, titles))
    if a.sheets:
        return
    rows.sort(key=lambda r: -r[0])
    print(f"Scanned {len(pdfs)} PDF(s). Candidates for '{a.element}' ({a.discipline}, best first):")
    for sc, pdf, n, ph, sz, nc, titles in rows[:a.top]:
        print(f"\n[{sc}] {pdf.name}  page {n}  distinct sizes:{sz}" + (f"  codes:{nc}" if nc is not None else ""))
        if ph:
            print("    table phrases: " + "; ".join(" ".join(x.split()) for x in ph[:6]))
        seen = []
        for t in titles:
            if t not in seen:
                seen.append(t)
        if seen:
            print("    sheet/view titles: " + " | ".join(s.upper()[:60] for s in seen[:6]))
    if index:
        print("\nDrawing index pages (read these first, they list every sheet title): " + ", ".join(index[:10]))
    if not rows:
        print("  none found by text. The table may be outlined text or a scan: read the drawing index, look visually, or ask the user.")
    if empty:
        print(f"\n{len(empty)} page(s) had no extractable text (outlined text or scans): "
              + ", ".join(empty[:15]) + (" ..." if len(empty) > 15 else ""))


if __name__ == "__main__":
    main()
