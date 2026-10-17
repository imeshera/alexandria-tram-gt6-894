# Articulation (component Articulation): body-section-shaped portal ring between the two sections with
# black rubber bellows either side (pleated), gangway lining, and the turntable floor plate.
# Section profile is the body section inset by d (same construction as build_body.section()).
import math
import adsk.core, adsk.fusion
import os
ROOT = os.path.dirname(os.path.abspath(__file__))

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}; exec(open(g['__file__']).read(), g)
    des = g['design'](); ev = g['ev_fn'](des)
    C = g['comp'](des, 'Articulation'); g['wipe'](C)
    P = adsk.core.Point3D.create; VI = adsk.core.ValueInput.createByString
    hw, t = ev('half_w'), ev('tumble')
    sb, belt, eave, crown = ev('skirt_bot'), ev('belt_h'), ev('eave_h'), ev('crown_h')
    la, gap, ax = ev('sec_a_len'), ev('artic_gap'), ev('artic_x')
    fl = ev('floor_h')
    ext = C.features.extrudeFeatures
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation

    def plane(x):
        pi = C.constructionPlanes.createInput(); pi.setByOffset(C.yZConstructionPlane, adsk.core.ValueInput.createByReal(x))
        p = C.constructionPlanes.add(pi); p.isLightBulbOn = False; return p

    def ring(x0, length, d, name, bottom=None):
        sk = C.sketches.add(plane(x0)); sk.name = name
        m = lambda y, z: sk.modelToSketchSpace(P(x0, y, z))
        h = hw - d; yb = bottom if bottom is not None else sb + d
        Ln, Ar = sk.sketchCurves.sketchLines, sk.sketchCurves.sketchArcs
        A, B = m(yb, -h), m(yb, h)
        l1 = Ln.addByTwoPoints(A, B); l2 = Ln.addByTwoPoints(l1.endSketchPoint, m(belt, h))
        l3 = Ln.addByTwoPoints(l2.endSketchPoint, m(eave - d, h - t))
        Fp = m(eave - d, -(h - t))
        roof = Ar.addByThreePoints(l3.endSketchPoint, m(crown - d, 0), Fp)
        e = roof.endSketchPoint if roof.endSketchPoint.geometry.distanceTo(Fp) < 1e-3 else roof.startSketchPoint
        l5 = Ln.addByTwoPoints(e, m(belt, -h)); Ln.addByTwoPoints(l5.endSketchPoint, l1.startSketchPoint)
        # gangway opening (arched like KS 890's portal)
        gw, gt = 62.0, fl + 200.0
        o1 = Ln.addByTwoPoints(m(fl, -gw), m(fl, gw)); o2 = Ln.addByTwoPoints(m(fl, gw), m(gt - 25, gw))
        oa = Ar.addByThreePoints(m(gt - 25, gw), m(gt, 0), m(gt - 25, -gw)); Ln.addByTwoPoints(m(gt - 25, -gw), m(fl, -gw))
        prof = None
        for i in range(sk.profiles.count):
            pr = sk.profiles.item(i)
            if pr.profileLoops.count == 2:
                prof = pr
        ei = ext.createInput(prof, NEW); ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal(length))
        f = ext.add(ei); f.name = name
        for b in f.bodies: b.name = name
        sk.isVisible = False
        return f

    # bellows: pleats alternating inset 4.5 / 7 cm, from the A end to the B start
    n = 14; pl = gap / n
    for k in range(n):
        ring(la + k * pl, pl, 4.5 if k % 2 == 0 else 7.0, 'Bellows', bottom=sb + 25)
    # portal ring (body colour) in the middle
    ring(ax - 14.0, 28.0, 2.0, 'Portal ring', bottom=sb + 20)
    # turntable floor plate + gangway side linings
    tb = g['TB'](C)
    tb.cyl('Turntable plate', (ax, fl - 2.0, 0), (ax, fl + 0.6, 0), 80.0)
    for s in (1, -1):
        tb.box('Gangway lining', ax, fl + 100, s * 63.0, gap + 30, 200, 1.5)
    tb.commit('Articulation floor')
    print('articulation bodies', C.bRepBodies.count)
