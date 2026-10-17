# Build log: Düwag GT6 894

Decisions, measurements and gotchas, newest last. Dimension sheet: `references/notes/heritage-dossier.md`.

## 2026-10-17: Research and choice
- Two research passes: fleet/type identification (`references/notes/research-raw.md`) and photo collection (106 images, with manifests).
- **Identification:**
  - Reference photo 1 (894) and photo 4 (856) are both ex-Copenhagen **Düwag GT6** cars. 856 is seen from its rear; its "١٠٧" is ٨٥٦ in Naskh.
  - Reference photo 2 is the Raml heritage car **601**.
  - Reference photo 3 is a city two-car set (Kinki 1982 or Ganz 1985/86).
- **Choice:** GT6 **894**. It runs alone, wore yellow (city) and light blue (Raml 2019) liveries, two of the four reference photos are this type, and the data are good. Car 601 and the city set became separate models (see "Related models" in the dossier). The reasoning is in `references/notes/heritage-dossier.md`.
- **Photogrammetry** (`references/notes/photogrammetry/rect1d.py`): 1-D projective rectification along the car side, scaled by the sourced 19.095 m length.
  - KS 818 (1969) is a long-lens, near-orthogonal broadside, much better than any Alexandria photo. It gives the windows, sections, bogie pivots (3.73 / 9.89 / 15.95 m, matching the GT6-D analog's 6.0 m spacing) and heights (roof 3.15 m).
  - The obliquer 877 photo is self-consistent with those heights at about a 31° view (50 mm lens).
- **Gotcha:** the front photos cannot use the 2.2 m width as an anchor. Düwag ends taper in plan, so the dash is narrower than the body.
- **Gotcha:** door-side layout. A first 3-point fit on 821 put door 1 at 2.4 m. The door close-ups (807/845) and the KS 890 front show door 1 directly behind the cab corner, with no right cab window. The fit was re-anchored on the front corner.

## 2026-10-17: Fusion build v1
- Created **Alexandria Heritage Tram 894** (Hybrid) with 80 user parameters, each with its source and confidence.
- **Body:** one section sketch (vertical lower side, 45 mm tumblehome window band, eave fillet, 3-point roof arc). It is extruded twice (sections A and B, gap at the articulation). The plan taper and bowed end faces are cut from the XZ plane, the roof-end domes are quarter-ellipse cuts in elevation, the dome edges are blended, and the body is shelled to 3 mm.
- **Fusion gotcha:** `TemporaryBRepManager` union of many same-named parts inside `TB.commit` made the door script time out (the transaction rolled back). Committing parts as separate bodies takes 0.2 s. Merging is off by default; `base()` name matching handles Fusion's "(1)" suffixes.
- **Fusion gotcha:** `OrientedBoundingBox3D.create` needs width ⟂ length. The helper now orthogonalises the width axis (tilted glass and tapered door panels).
- **Fusion gotcha:** deleting the only occurrence of a new component deletes the component. Keep it and reuse it as instance 1.
- Running gear, ends, roof, articulation, interior (36 seats as two instanced components), cab, livery and lettering scripts: see `fusion/README.md`.

## 2026-10-17: Door-side correction, underlays, slow appearance pass
- Right side re-laid from the 807/845 door close-ups:
  - door 1 at 0.62–1.92 m, directly behind the cab corner;
  - then a narrow window and 3 windows (1.49 m) up to door 2 at 7.58 m;
  - then a narrow window ‖ narrow window, door 3 at 11.10 m, and 3 windows (1.55 m);
  - rear-corner door 4 at 17.65 m.
  - The right-side windows come out wider than the left (1.30–1.33 m). LOW confidence, flagged in the dossier.
- New `underlay_818.py`: resamples the KS 818 broadside through the 1-D projective model into a metric left elevation at 100 px/m (`references/images/derived/derived_KS818_left_elevation_rectified.jpg`, gitignored). It checks out at roof 3.16 m and the window grid matches. `canvases.py` puts it on a plane at z = +2.6 m at 45 % opacity, so it overlays the model in the left view.
- **Performance gotcha:** the first `build_appearance.py` run took about 30 min.
  - Cause: splitting faces mid-timeline, then painting about 1,000 faces one by one.
  - Now the split features are kept unless `_context = 'resplit'`. Bodies are set to the interior colour in one call and only outer-skin faces are overridden. Progress goes to a log file in the system temp directory, because a remote script call times out long before the pass ends.
- Fixed: the route-number blind sat inside the solid route box. The blind and glass now sit in front of the box face, with a glazing frame.
- **Gotcha:** a modal dialog in Fusion (here an "Upload Error") blocks every API call; all script calls time out until it is dismissed.

## 2026-10-17: Ends, livery, lettering, overlay check, renders
- **Timeline check** after the openings/glazing/doors correction and the interior rebuild: 129 features, all healthy. All components are present (2 shell bodies, 166 glazing, 92 door, 320 interior bodies, 36 seats as 23 instanced seat components).
- `build_ends` re-run (26 front, 14 rear bodies). `build_appearance` now takes about 40–85 s, down from 30 min, because the splits are kept.
- **Fusion gotcha: setting a face appearance can reorder `body.faces`.** The one-pass loop skipped about 1 face in 6, so the bands were inconsistent: left lower panel painted "skirt", right window band painted "waist stripe". The loop now indexes faces and repeats until a pass changes nothing (it converges in 2 passes).
- **Fusion gotcha: editing the colour of an in-use appearance spawns same-named duplicates** (30 → 48 entries). `custom()` now writes a colour only when it differs, and unused `GT6*` duplicates are purged.
- **Interior fix:** mahogany wall-lining patches showed on the outside near both ends. Each lining was one straight box at `side_z(midpoint)`, but the plan taper plus its **R 15 m `taper_blend` arc** pulls the skin in from x ≈ 1.52 to 2.88 m (ray-measured: inner skin 108.2 cm at x = 2.2 m, against 109.7 cm amidships). `side_z()` now models the arc. Linings and heaters in the taper zones are cut into 30 cm chords that follow it. A ray check (344 rays, both sides) finds no interior body outside the skin.
- **Lettering:** the dash numbers came out rotated 90°, because the angled dash planes have sketch x = model up. `Sketch.move` ignores imported SVG curves, so the extruded decal bodies are now turned with a free-move feature about the plane normal, and the mirrored/plain SVG choice uses the rotated axis. The front "V" wasn't getting its blue: the name match failed on "(1)" suffixes and now uses `base()`. `common.wipe` also deletes move features.
- **Overlay check against KS 818** (left view, underlay at 45 %): window grid, section ends, articulation, bogie wheel positions, roof line, resistor cover and trolley-base position all match to within a few cm at render resolution. Nothing needed moving. The underlay is now hidden (`canvases.py hide`) for renders.
- **Renders** (`docs/renders/2026-10-17_*.png`): iso (front 3/4, door side), isoL, left, right, front, rear, interior.
  - `view.py` has a new `interior` preset (standing at the rear of section B, looking to the cab).
  - Presets reset `perspectiveAngle`, because the interior one leaked a 1.2 rad lens into the next iso.
  - `render.py` captures twice, because the first capture after a camera change can come out blank.
- Open items:
  - The interior render shows a dark floor-base and pivot area at the rear end of section B. Check whether the slats should cover it.
  - The right-side window widths are still LOW confidence.

## 2026-10-17: 894 lettering, ink-box fix
- **Bug:** the decal ink box was measured from `sketch.sketchPoints`, which includes the sketch origin, so the box grew by the font ascent and decals came out at 50–93 % of the requested height (worst on the Naskh numerals). Found on car 601.
- `fusion/scripts/build_lettering.py` now takes the decal ink box from the curves' bounding boxes. Re-ran it on 894 (72 bodies, 21 s).
- Measured heights now equal the requested ones:
  - dash numbers 894 and ٨٩٤: 15.0 cm each (before: Western ≈ 14 cm, Naskh visibly smaller);
  - destination 12.0 cm, inside the 20 cm blind;
  - route ٤: 17.0 cm;
  - side legend: 9.0 cm;
  - rear plate: 8.0 cm.
- Front and side screenshots are clean. Saved 894 and re-rendered `docs/renders/2026-10-17_{iso,isoL,left,right,front,rear}.png`.

## 2026-10-17: Parameter evaluation check (found on the city set)
- On the Ganz city car, `unitsManager.evaluateExpression('half_w')` returned a stale value after `body_w` was edited
  mid-session, so bodies were silently built at the old width. 894 also had parameters edited mid-session; its
  overlay against KS 818 still matched, but if a dimension looks off after a parameter change, close and reopen the
  document before rebuilding, or read plain names from `userParameters` as the city scripts do.

## 2026-10-17: Split into its own repository
- The model was developed inside a combined Alexandria-trams workspace, together with the other reference trams
  (see "Related models" in `references/notes/heritage-dossier.md`). This repository carries only this model's
  scripts, notes, renders, manifests and exports, plus a copy of the shared helper `common.py`.
- **Paths:** scripts no longer use absolute paths. The exec loader passes `__file__`; each script resolves
  `ROOT = os.path.dirname(os.path.abspath(__file__))` and finds its helpers, the lettering SVGs
  (`tools/lettering/svg/`), the render folder (`docs/renders/`) and the derived underlay
  (`references/images/derived/`, gitignored) relative to it. Progress logs go to the system temp directory.
- **Fusion organisation:** the designs now live in project **Eshera-Personal**, folder **Alexandria Tram Model 3 - Duewag GT6 894**. `create_doc.py`
  saves into that folder (created if missing), and the save guards check `PROJECT = 'Eshera-Personal'`.
- **Exports** in `models/` were made from the final Fusion designs: `Alexandria Heritage Tram 894.f3d` and `.step`.
- Reference photos are not redistributed; `references/SOURCES.md` lists each with author, licence and URL.
