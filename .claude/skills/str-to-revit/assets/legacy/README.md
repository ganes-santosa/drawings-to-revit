# Legacy source (do not edit)

`structural-drawings-to-revit-v1-KPwBI.md` is a verbatim copy of the original single-file skill (installed plugin `structural-drawings-to-revit`). It records the KPwBI DIY Gedung Utama renovation project: a 120-page structural DED, Revit 2026, ~840 framing members, 66 floors, 52 pile caps, a steel roof truss and a portico canopy.

All of its knowledge has been distributed into `references/` and `workflows/`, tagged `[IMPORTED KPwBI]`. Mapping (legacy part → current home):

| Legacy | Now in |
|---|---|
| Part 1.1 principles, 5.1 preferences | SKILL.md §3, §4 "User working preferences" |
| Part 1.2 workflow | workflows/full-modeling-workflow.md, SKILL.md §4 order |
| Part 1.3 user points at something | SKILL.md §4 preferences, drawing-interpretation.md §5 |
| Part 2 drawing interpretation | references/drawing-interpretation.md, grids-and-levels.md §5 |
| Part 3.1 coordinates/levels | project-setup.md, grids-and-levels.md |
| Part 3.2–3.6 elements | columns.md, beams.md, slabs.md, structural-framing.md, foundations.md, revit-families.md |
| Part 3.7 MCP/API mechanics | revit-api-and-automation.md §4 |
| Part 4 documentation and views | removed from focus (view naming rules and the template-filter gotcha are in troubleshooting.md) |
| Part 5 troubleshooting table | troubleshooting.md (index) + element files |
| Part 6 QC checklist | model-validation.md §2, workflows/quality-control-workflow.md |

Keep this file as the evidence trail. If a current reference contradicts it, check this file first, then re-test.
