#!/usr/bin/env python3
"""Piecewise grid calibration for vector PDF drawings (pdfplumber).

Maps PDF points -> real-world mm, grid-to-grid, independently per axis.  Never uses one
global scale.  Reports residuals so a wrong grid pick is visible.

Usage:
  pdf_calibrate.py lines FILE.pdf PAGE [--min-len 200]
      List long near-vertical / near-horizontal lines (grid candidates) with pt coordinates.
  pdf_calibrate.py map  --xknots "308.9:0,602.1:6000,..." --yknots "..." --pt X Y
      Convert a PDF point to mm and print per-segment scale deviations (flags >0.5%).
Knots are pt:mm pairs, increasing in pt.  Piecewise-linear; extrapolates from the end
segments.  `--selftest` builds a synthetic PDF with a known non-uniform scale and checks it.
"""
import argparse, sys, tempfile, os


def parse_knots(s):
    k = sorted((float(a), float(b)) for a, b in (p.split(":") for p in s.split(",")))
    if len(k) < 2:
        raise SystemExit("need >=2 knots")
    return k


def interp(knots, v):
    """Piecewise-linear pt -> mm with end-segment extrapolation."""
    if v <= knots[0][0]:
        i = 0
    elif v >= knots[-1][0]:
        i = len(knots) - 2
    else:
        i = max(j for j in range(len(knots) - 1) if knots[j][0] <= v)
    (p0, m0), (p1, m1) = knots[i], knots[i + 1]
    return m0 + (v - p0) * (m1 - m0) / (p1 - p0)


def residual_report(knots):
    """Per-segment scale (mm/pt); flags segments deviating >0.5% from the median scale."""
    sc = [(knots[i + 1][1] - knots[i][1]) / (knots[i + 1][0] - knots[i][0]) for i in range(len(knots) - 1)]
    med = sorted(sc)[len(sc) // 2]
    out = []
    for i, s in enumerate(sc):
        dev = (s / med - 1) * 100
        out.append(f"  seg {i}: {knots[i][0]:.2f}->{knots[i+1][0]:.2f} pt  {s:.4f} mm/pt  dev {dev:+.2f}%" + ("  <-- CHECK" if abs(dev) > 0.5 else ""))
    return "\n".join(out)


def list_lines(path, page, min_len):
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        pg = pdf.pages[page - 1]
        print(f"page {page}: {pg.width:.1f} x {pg.height:.1f} pt")
        vs, hs = [], []
        for ln in pg.lines + [r for r in pg.rects if min(r['width'], r['height']) < 1]:
            x0, x1, t, b = ln['x0'], ln['x1'], ln['top'], ln['bottom']
            if abs(x1 - x0) < 0.5 and (b - t) >= min_len:
                vs.append((round((x0 + x1) / 2, 2), round(t, 1), round(b, 1), ln.get('linewidth')))
            elif abs(b - t) < 0.5 and (x1 - x0) >= min_len:
                hs.append((round((t + b) / 2, 2), round(x0, 1), round(x1, 1), ln.get('linewidth')))
        print("VERTICAL lines (x_pt, top, bottom, width):"); [print("  ", v) for v in sorted(set(vs))]
        print("HORIZONTAL lines (y_pt(top-origin), x0, x1, width):"); [print("  ", h) for h in sorted(set(hs))]


def selftest():
    # Synthetic sheet: vertical grid lines at known x_pt with deliberately NON-uniform pt/mm.
    from reportlab.pdfgen import canvas  # type: ignore
    xs_pt = [50.0, 150.4, 249.9, 400.2]
    xs_mm = [0.0, 6000.0, 12000.0, 21000.0]
    path = os.path.join(tempfile.mkdtemp(), "t.pdf")
    c = canvas.Canvas(path, pagesize=(500, 500))
    for x in xs_pt:
        c.line(x, 20, x, 480)
    c.save()
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        found = sorted({round((l['x0'] + l['x1']) / 2, 1) for l in pdf.pages[0].lines if l['bottom'] - l['top'] > 200})
    assert found == xs_pt, (found, xs_pt)
    k = list(zip(found, xs_mm))
    for (p, m) in k:
        assert abs(interp(k, p) - m) < 1e-6
    mid = interp(k, 200.15)  # midway in segment 2 -> expect 9000
    assert abs(mid - 9000) < 1.0, mid
    g = (xs_mm[-1] - xs_mm[0]) / (xs_pt[-1] - xs_pt[0]) * (200.15 - xs_pt[0])  # global-scale error demo
    print(f"selftest OK: piecewise mid={mid:.1f} mm (truth 9000); global-scale would give {g:.1f} mm (err {g-9000:+.1f})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("lines"); a.add_argument("pdf"); a.add_argument("page", type=int); a.add_argument("--min-len", type=float, default=200)
    m = sub.add_parser("map"); m.add_argument("--xknots"); m.add_argument("--yknots"); m.add_argument("--pt", nargs=2, type=float, required=True)
    ap.add_argument("--selftest", action="store_true")
    n = ap.parse_args()
    if n.selftest:
        selftest()
    elif n.cmd == "lines":
        list_lines(n.pdf, n.page, n.min_len)
    elif n.cmd == "map":
        out = []
        if n.xknots:
            k = parse_knots(n.xknots); print("X scale check:\n" + residual_report(k)); out.append(f"x={interp(k, n.pt[0]):.1f} mm")
        if n.yknots:
            k = parse_knots(n.yknots); print("Y scale check:\n" + residual_report(k)); out.append(f"y={interp(k, n.pt[1]):.1f} mm")
        print(" ".join(out))
    else:
        ap.print_help()
