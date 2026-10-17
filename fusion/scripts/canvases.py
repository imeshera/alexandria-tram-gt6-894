# Calibrated photo underlays (component Underlays). Images come from references/notes/photogrammetry/underlay_*.py.
# Side canvases sit on the XY plane at z = offset (positive: between the viewer of the LEFT side and the car,
# so at 50 % opacity they overlay the model in the 'left' view). Image-right = model +X, image-up = +Y.
import adsk.core, adsk.fusion
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
DER = os.path.join(ROOT, '..', '..', 'references', 'images', 'derived', '')   # gitignored; see references/notes/photogrammetry
# name, file, z offset cm, mm/px, u0 px, v0 px (from top) of the model origin (front end, top of rail), w, h
CANVASES = [('KS 818 left (rectified)', 'derived_KS818_left_elevation_rectified.jpg', 260.0, 10.0, 100, 450, 2150, 500)]

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}; exec(open(g['__file__']).read(), g)
    des = g['design']()
    C = g['comp'](des, 'Underlays')
    for i in range(C.canvases.count - 1, -1, -1): C.canvases.item(i).deleteMe()
    for i in range(C.constructionPlanes.count - 1, -1, -1): C.constructionPlanes.item(i).deleteMe()
    vis = (_context or '').strip() != 'hide'
    for name, fn, off, s, u0, v0, iw, ih in CANVASES:
        pi = C.constructionPlanes.createInput(); pi.setByOffset(C.xYConstructionPlane, adsk.core.ValueInput.createByReal(off))
        pl = C.constructionPlanes.add(pi); pl.name = 'Underlay plane ' + name; pl.isLightBulbOn = False
        ci = C.canvases.createInput(DER + fn, pl)
        W, H = iw * s / 10.0, ih * s / 10.0
        uo, vo = u0 / iw, 1.0 - v0 / ih
        m = adsk.core.Matrix2D.create()
        m.setCell(0, 0, W); m.setCell(0, 2, -W * uo); m.setCell(1, 1, H); m.setCell(1, 2, -H * vo)
        ci.transform = m; ci.opacity = 45; ci.isDisplayedThrough = False
        cv = C.canvases.add(ci); cv.name = name; cv.isLightBulbOn = vis
    print('canvases', C.canvases.count, 'visible' if vis else 'hidden')
