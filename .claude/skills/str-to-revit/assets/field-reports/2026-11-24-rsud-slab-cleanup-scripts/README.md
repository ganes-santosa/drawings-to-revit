# Slab clean-up and audit scripts (RSUD Cakung, 2026-11-24) — [EXPERIMENTAL] outside RSUD

Field tools from the structure agent. See ../2026-11-24-rsud-cakung-slab-cleanliness.md for the rules they implement.

Run order per level (after generating slab_<LEVEL>.txt and exporting beams to CSV):
1. `python corner2.py LEVEL...` then `python cap.py LEVEL... -w`   (corner steps, U-caps, slivers, paired steps)
2. `python snapedge.py LEVEL... -w`                               (edges onto edge-beam outer faces)
3. repeat 1
4. audits: `audit.py`, `prot.py`, `side.py`, `freeend.py "LEVEL NAME"`, `encl.py`
5. rebuild the level's floors in Revit (one level per call), read back warnings.

Dependencies: numpy, opencv-python (cv2), matplotlib (Path). No Revit access needed.

Project-specific (replace before reuse): file paths (/mnt/user-data/...), level names, joint x-range in snapedge.py (67350–67950),
the RSUD arc terrace in protlib.py / snapedge.py, and the DEL/UPD/ADD beam patches in snapedge.py.

## Notes from the skill agent (2026-11-24, on archiving)
- Archived verbatim from the structure agent. Not parameterised, not run in this repo: `[EXPERIMENTAL RSUD]`, and RSUD-only until generalised.
- `audit.py` flags sketch edges < 400 mm; the report's audit #6 says < 200 mm. Use the report's value; the script's is looser.
- `corner2.py` has two `__main__` blocks (the second runs `pairs`). Harmless; clean up when generalising.
- Generalising these into `scripts/` (paths, level names, joint range, hand-built pieces as inputs) is an open task in HANDOFF.md.
