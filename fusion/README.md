# Fusion build scripts: Düwag GT6 894

These scripts build the Fusion design **Alexandria Heritage Tram 894** from scratch, from a parameter table.
Units are Fusion's internal cm. Frame: 1:1, Y up, X runs from the front (cab) end towards the rear, Z is lateral,
and the door side (right) is −Z.

## Running a script: the exec loader

Every script defines `run(_context: str)` and finds its helpers, lettering SVGs and render folder relative to its
own `__file__`, so the repo can live anywhere. Run a script through this small loader (paste it into a Fusion
script created under **Utilities → Scripts and Add-Ins → +**, or send it through any bridge that runs Python inside
Fusion), with the path pointing at your clone:

```python
def run(_context: str):
    path = '<repo>/fusion/scripts/<script>.py'          # e.g. ~/src/alexandria-tram-gt6-894/fusion/scripts/build_body.py
    ns = {'__name__': 'fusion_script', '__file__': path}
    exec(compile(open(path).read(), path, 'exec'), ns)
    ns['run'](_context)                                   # _context = the script's options string ('' for defaults)
```

`__file__` must be passed: the scripts compute `ROOT = os.path.dirname(os.path.abspath(__file__))` and exec their
helpers (`common.py`) from there.

All geometry reads the document's user parameters. After changing a parameter, re-run the scripts that depend on it.
Each build script wipes and rebuilds its own component, so re-running is safe.

**Fusion project.** `common.py` holds `PROJECT = 'Eshera-Personal'` and `FOLDER = 'Alexandria Tram Model 3 - Duewag GT6 894'`. `create_doc.py`
saves the new design into that folder (created if missing), and the save guards refuse to save a document that is not
in `PROJECT`. Change both constants to use your own project.

## Build order

| # | Script | Context | Builds |
|---|---|---|---|
| 1 | `create_doc.py` | | Creates and saves the design (Hybrid intent) in the model folder |
| 2 | `apply_params.py` | | Creates or updates the 77 user parameters from `params.py` (each with its source and confidence) |
| 3 | `build_body.py` | | Cross-section (tumblehome, arched roof) → sections A and B, plan taper and bowed end faces, roof-end domes, 3 mm shell |
| 4 | `build_openings.py` | | Left windows, right doors and windows, windscreen, destination glass, rear window, gangway openings (`layout()` is shared with 5, 6 and 11) |
| 5 | `build_glazing.py` | | Tilted side glass, rubbers, hopper vents, two-pane windscreen and rear window, destination blind |
| 6 | `build_doors.py` | | 4-panel folding doors (lower/upper leaves, glazing, KS front-door lower lights), handles, entrance steps |
| 7 | `build_bogies.py` | | Düwag tandem-drive motor bogie ×2 and the Jacobs bogie (wheels, axleboxes, chevron springs, track brakes, cardan motor) |
| 8 | `build_ends.py` | | Headlight, roof marker lamps, route box, bumper, indicators, mirror; tail lamps and rear route box |
| 9 | `build_roof.py` | | Trolley pole with base, harp and wheel, resistor cover, arrester, pole hook; or the diamond pantograph (`panto_on = 1`) |
| 10 | `build_articulation.py` | | Pleated bellows, portal ring, turntable plate, gangway linings |
| 11 | `build_interior.py` | | Wood-slat floor, linings, ribbed ceiling, light strips, poles and rails, heaters, cab partition, conductor's desk, 36 instanced wood-slat seats (2+1) |
| 12 | `build_cab.py` | | Dash, gauges, Düwag controller, brake valve, switches, pedals, driver's seat |
| 13 | `build_appearance.py` | `''` or `resplit` | Livery split and paint per `livery`, and all materials. Run it in its own call, then check the paint (see BUILD-LOG) |
| 14 | `build_lettering.py` | | CoreText SVG decals from `tools/lettering/svg/`: dash numbers 894 / ٨٩٤, route ٤ and destination blinds, operator name, rear plate, livery-1 front "V" |
| 15 | `canvases.py` | `''` or `hide` | Calibrated KS 818 broadside underlay (needs the derived image, see below); `hide` switches it off for renders |
| 16 | `save.py` | version message | Guarded save |
| — | `view.py` | `iso`, `isoL`, `isoR`, `left`, `right`, `front`, `rear`, `top`, `interior`, `fit` | Camera presets |
| — | `render.py` | preset list or `all` | Viewport captures to `docs/renders/<date>_<view>.png` |

`common.py` holds the shared helpers: `design()` (find the open document by name), `comp()`, `wipe()`, the
`TB` TemporaryBRep body collector, `base()` (strips Fusion's "(1)" suffixes), `ev_fn()`, `find_project()`,
`model_folder()`.

## Switches (user parameters)

| Parameter | Values |
|---|---|
| `livery` | 1 city ochre-yellow + blue stripe, c. 2000–2015 (default) · 2 APTA 1974 ochre/cream · 3 green/white 2016+ · 4 Raml light blue/white 2019 · 5 KS Copenhagen |
| `panto_on` | 1 = diamond pantograph instead of the trolley pole (re-run `build_roof.py`) |
| `door2_on` | 0 = second door plated over (re-run 4–6) |
| `car_no` | Fleet number (regenerate the SVGs with `tools/lettering/make_svgs.sh <text2svg> <no>`, then re-run `build_lettering.py`) |

After changing `livery`, re-run `build_appearance.py` and `build_lettering.py`.

## Photo underlay

`canvases.py` expects `references/images/derived/derived_KS818_left_elevation_rectified.jpg`, which is not in the
repo (it is derived from a third-party photo). Download the KS 818 broadside listed in `references/SOURCES.md`
(Commons 41468165) and run
`python3 references/notes/photogrammetry/underlay_818.py <photo> references/images/derived/derived_KS818_left_elevation_rectified.jpg`.
