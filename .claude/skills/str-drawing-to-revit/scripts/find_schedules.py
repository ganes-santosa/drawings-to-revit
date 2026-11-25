#!/usr/bin/env python3
"""Find pages in structural drawing PDFs that look like type schedules/tables.

Usage:
  python find_schedules.py <pdf or folder> [--element columns|beams|slabs|foundations|roof|all] [--top 10]

Scores each page by schedule keywords (English + Indonesian) and element keywords, and
prints the best candidates with page number and matching lines. It only reads text that the
PDF actually contains: outlined/vector text and scanned sheets return nothing (then look
visually or ask the user to point to the sheet). Uses PyMuPDF (fitz) if installed, else
the pdftotext command.
"""
import argparse, re, shutil, subprocess, sys
from pathlib import Path

SCHEDULE = ["schedule", "tabel", "table", "daftar", "tabulasi", "type", "tipe", "penulangan", "pembesian",
            "dimensi", "ukuran", "size", "mark", "kode"]
ELEMENT = {
    "columns": ["kolom", "column", "col.", "k1", "k2", "kc"],
    "beams": ["balok", "beam", "b1", "b2", "g1", "girder", "sloof", "tie beam"],
    "slabs": ["pelat", "plat", "slab", "s1", "s2", "deck", "tebal", "thickness"],
    "foundations": ["pondasi", "fondasi", "foundation", "footing", "pile", "tiang",
                    "pile cap", "poer", "bor pile", "strauss"],
    "roof": ["atap", "roof", "rangka", "truss", "kuda-kuda", "gording", "gordeng", "purlin",
             "rafter", "wf", "cnp", "profil", "trekstang", "trekstank", "trecstang", "sagrod",
             "ikatan angin", "kanopi", "canopy", "baja ringan", "hb", "2l", "lc"],
}


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


# Table/detail title phrases: the strongest signal. A plan page that merely mentions
# "KOLOM K2 800x800" in labels must not outrank the real table (lesson from the DRC set).
_E = {"columns": r"kolom|column", "beams": r"balok|beam|sloof", "slabs": r"pelat|plat|slab",
      "foundations": r"pondasi|fondasi|foundation|footing|pile ?cap|poer|tiang|bore ?pile",
      "roof": r"atap|roof|kuda[- ]kuda|truss|gording|purlin|kanopi|canopy|crown"}
PHRASES = {k: [r"(tabel|daftar|tabulasi)\s+((penulangan|pembesian|tulangan)\s+)?(" + v + r")",
               r"(tipe|type)\s+((perkuatan|jacketing|strengthening)\s+)?(" + v + r")",
               r"detail\s+((penulangan|pembesian)\s+)?(" + v + r")",
               r"(" + v + r")\s+(schedule|table|type)"] for k, v in _E.items()}
PHRASES["roof"] += [r"(tabel|daftar)\s+profil", r"profil\s+baja", r"denah\s+(pelat\s+)?rangka\s+(atap|crown|kanopi)",
                     r"rencana\s+atap", r"potongan\s+(truss|rangka\s+atap|kuda)", r"detail\s+(tipikal\s+)?gording"]
# steel profiles as written on roof sheets: WF 350x175x7x11, WF.350.175.7.11, C 125.50.20.2,3, 2L 70x70x6
PROFILE = re.compile(r"(?<![a-z])(wf|hb|h|cnp|lc|c|2l|l)\s*[. ]?\s*\d{2,3}(\s*[.x×]\s*\d+(,\d+)?){1,4}")
TITLE = re.compile(r"^(detail|tabel|daftar|denah|potongan|rencana|schedule)\b.*$", re.M)


def score(text, element):
    low = text.lower()
    kinds = list(_E) if element == "all" else [element]
    p_hits = sorted({m.group(0) for k in kinds for pat in PHRASES[k] for m in re.finditer(pat, low)})
    s_hits = [k for k in SCHEDULE if re.search(r"(?<![a-z])" + k + r"(?![a-z])", low)]
    keys = sum((ELEMENT[k] for k in kinds), [])
    e_hits = [k for k in keys if re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", low)]
    sizes = len(set(re.findall(r"\d{2,4}\s*[x×]\s*\d{2,4}", low)))  # distinct sizes only
    if element in ("roof", "all"):
        sizes = max(sizes, len({m.group(0) for m in PROFILE.finditer(low)}))
    titles = [m.group(0).strip() for m in TITLE.finditer(low)]
    title_hit = any(re.search(_E[k], t) for k in kinds for t in titles)
    plan_only = any(t.startswith("denah") for t in titles) and not p_hits
    # stair sheets mention kolom/balok bordes: push them down unless they are the target
    stair = any(re.search(r"tangga|bordes|stair", t) for t in titles)
    # "contoh" = example: standard-detail sheets show example tables, not the project's own
    example = bool(re.search(r"contoh\s+(tabel|tabulasi)|example\s+(table|schedule)", low))
    sc = 8 * len(p_hits) + 6 * title_hit + 2 * len(s_hits) + 2 * len(e_hits) + min(sizes, 6) - 6 * plan_only - 12 * stair - 15 * example
    return sc, p_hits, e_hits, sizes, titles


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--element", default="all", choices=list(ELEMENT) + ["all"])
    ap.add_argument("--top", type=int, default=10)
    a = ap.parse_args()
    p = Path(a.path)
    pdfs = sorted(p.rglob("*.pdf")) if p.is_dir() else [p]
    if not pdfs:
        sys.exit(f"No PDFs found in {p}")
    rows, empty, index = [], [], []
    for pdf in pdfs:
        for n, text in page_texts(pdf):
            if len(text.strip()) < 20:
                empty.append(f"{pdf.name} p{n}")
                continue
            if re.search(r"daftar\s+gambar|drawing\s+(index|list)|list\s+of\s+drawings", text.lower()):
                index.append(f"{pdf.name} p{n}")
            sc, ph, eh, sz, titles = score(text, a.element)
            if sc > 0 and (eh or ph):
                rows.append((sc, pdf, n, ph, sz, titles))
    rows.sort(key=lambda r: -r[0])
    print(f"Scanned {len(pdfs)} PDF(s). Candidates for '{a.element}' (best first):")
    for sc, pdf, n, ph, sz, titles in rows[:a.top]:
        print(f"\n[{sc}] {pdf.name}  page {n}  distinct sizes:{sz}")
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
        print("  none found by text. The table may be outlined text or a scan: look visually or ask the user.")
    if empty:
        print(f"\n{len(empty)} page(s) had no extractable text (outlined text or scans): "
              + ", ".join(empty[:15]) + (" ..." if len(empty) > 15 else ""))


if __name__ == "__main__":
    main()
