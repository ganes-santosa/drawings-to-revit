// CORE DOOR FAMILY "KPW_Door" from Metric Door.rft (openings-families.md A5d).
// [VERIFIED 2026-11-25, Revit 2026 scratch model] 47/47 face locks, flex test 8/8 (KPwBI D46/47/48/52/53/55/65, DRC SD2),
// committed combination sweep 101/120 without failure (rest not run: bridge timeouts), project check D46/D47/D52/D55 exact.
// Without the caps below, D55 (single leaf, vision 800) failed: "Parameter VDaL has an invalid value" -> modal dialog, API frozen.
// Width x Height = wall opening = frame outside (KPwBI "Ukuran Opening"). Template's Opening Cut is kept.
// Parameters (type): Width, Height, Frame Width 50, Thickness 50 (leaf), Frame Depth 100, Leaves 1|2,
//   Has Transom + Transom Door Height, Has Vision Panel + Vision Width/Height/Bottom (centred in each leaf),
//   Has Louvre + Louvre Height/Bottom/Margin (bottom panel in each leaf). Glass door = vision panel nearly the leaf size.

// ===== STEP 1: delete the template frame extrusions (ids 443, 528 in the 2026 English template; find them by
//   class Extrusion), then parameters + formulas:
//   Door Height = if(Has Transom, if(Transom Door Height < Height - 2 * Frame Width - 50 mm, Transom Door Height, Height - 2 * Frame Width - 50 mm), Height - 3 * Frame Width - 100 mm)
//   Leaf Top    = if(Has Transom, Door Height, Height - Frame Width)
//   Bar Top     = Door Height + Frame Width
//   Leaf W2     = (Width - 2 * Frame Width) / 2
//   Vision Width S = if(Vision Width < Width - 2 * Frame Width - 100 mm, Vision Width, Width - 2 * Frame Width - 100 mm)
//   Vision Width D = if(Vision Width < Leaf W2 - 100 mm, Vision Width, Leaf W2 - 100 mm)   (caps: hidden copies must stay valid)
//   VS1L/VS1R   = Width / 2 -/+ Vision Width S / 2                                (single leaf)
//   VDaL/VDaR   = Frame Width + Leaf W2 / 2 -/+ Vision Width D / 2                (double, leaf A)
//   VDbL/VDbR   = Frame Width + 1.5 * Leaf W2 -/+ Vision Width D / 2              (double, leaf B)
//   Vision Top  = Vision Bottom + Vision Height ; Louvre Top = Louvre Bottom + Louvre Height
//   LS1L = Frame Width + Louvre Margin ; LS1R = Width - Frame Width - Louvre Margin ; LDaR = if(Width / 2 - Louvre Margin > Frame Width + Louvre Margin + 20 mm, Width / 2 - Louvre Margin, Frame Width + Louvre Margin + 20 mm) ; LDbL mirrored
//   Show Single = Leaves = 1 ; Show Double = Leaves = 2 ; Show Vision 1/2 = and(Has Vision Panel, Leaves = 1/2) ; Show Louvre 1/2 likewise
//   Build defaults: Width 1800, Height 3000, Leaves 2, transom 2400, vision 300x600 @1300, louvre 300 @200, margin 100.

// ===== STEP 2: planes. Name the template's horizontal plane "Head". From Left: Frame Left (Frame Width), VS*, VD*, LS*, LD*;
//   from Right: Frame Right; from Head: Frame Top; from the level (lvl.GetPlaneReference()): Leaf Top, Bar Bottom (Door Height),
//   Bar Top, Vision Bottom/Top, Louvre Bottom/Top. Leaf Top and Bar Bottom coincide with a transom: lock by NAME (step 3), not by position.

// ===== STEP 3: extrusions + explicit lock map (same Transaction, Regenerate before locking). Sketch planes normal Y:
//   frame U-polygon (Left,0)(Left,Head)(Right,Head)(Right,0)(Frame Right,0)(Frame Right,Frame Top)(Frame Left,Frame Top)(Frame Left,0)
//     y=-50 end=Frame Depth, locks X: Left, Right, Frame Left, Frame Right; Z: Head, Frame Top
//   leaf single (Frame Left..Frame Right, 0..Leaf Top) y=-25 end=Thickness, Panel, Show Single
//   leaf A (Frame Left..Center (Left/Right)), leaf B (Center..Frame Right), Show Double
//   transom bar (Bar Bottom..Bar Top) + transom glass (Bar Top..Frame Top), Has Transom
//   vision 1 / a / b: glass 54 mm deep at y=-27 (sticks out 2 mm each side so it shows on the leaf faces)
//   louvre 1 / a / b: new subcategory "Louvre", 54 mm deep at y=-27
//   Template plan-swing symbolic lines: IS_VISIBLE_PARAM -> Show Single (double-leaf swing not drawn yet).
//   Expect 47 locks.

// ===== STEP 4: flex test (RollBack): frame ±W/2 and 0..H; leaf extents; leaf top = transom ? Transom Door Height : H - f;
//   transom bar z; vision bbox centred per leaf; louvre bbox; visibility of every optional part. All must pass.
