# Drawing analysis workflow (route: `analyze`)

1. **Inventory:** list the PDFs; `find_schedules.py <folder> --sheets` for a sheet map (type, number, title). Pages with no text → note them; read titles visually (rendered page or the drawing index `DAFTAR GAMBAR`).
2. **Classify** each sheet: plan / wall-type / finish (floor, wall, ceiling) / elevation / section / detail / keyplan / schedule / demolition / existing / 3D (`references/drawing-interpretation.md` §2). Confirm the architectural set (some folders are full multi-discipline sets).
3. **Schedules per element:** `--element openings|walls|finishes|ceilings|floors|roofs`; confirm the top pages visually.
4. **Levels and heights:** where FFL/SFL, floor-to-floor, sills, ceiling heights, eaves and ridges are given; note conflicts.
5. **Scale and grids:** scale per sheet; grid names; check one dimension chain per plan.
6. **Renovation status:** existing / demolition sheets and what they remove.
7. **Output:** sheet map + schedule pages + level sources in the project log; RFI/conflict list (`assets/examples/rfi-log-template.md`). Ask the user about the critical items.
