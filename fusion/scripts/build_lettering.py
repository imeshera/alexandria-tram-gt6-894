# Lettering decals (component Lettering) from CoreText SVG outlines (tools/lettering).
# Generic planar placement: for each decal we give a construction plane, the model point of the ink-box centre,
# the ink height, the reading direction (as seen from outside) and the outward direction. The script picks the
# mirrored (_L) or plain (_R) SVG from the sketch x-axis, drops counters (holes), and extrudes 0.3 mm outward.
#  - front dash: Western "894" on the viewer's left, Eastern-Arabic "٨٩٤" on the right of the headlight
#    (829/830/875 photos). The dash is bowed in plan, so each number sits on its own angled plane.
#  - route blind "٤" and destination blind "أبو الدرداء" (894 on route 4 to Abou El Dardaa, 2024: E for the era)
#  - operator name small under the windows on both sides; rear number plate.
#  - livery 1 only: dark-blue waist-stripe "V" on the front dash (2000s Alexandria scheme, e.g. 815/856/895).
import math
import adsk.core, adsk.fusion
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(ROOT, '..', '..', 'tools', 'lettering', 'svg', '')
PX = 3.7795275591

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}; exec(open(g['__file__']).read(), g)
    des = g['design'](); ev = g['ev_fn'](des)
    L = g['comp'](des, 'Lettering'); g['wipe'](L)
    P, V3 = adsk.core.Point3D.create, adsk.core.Vector3D.create
    hw, Lc = ev('half_w'), ev('car_len')
    bow, et = ev('nose_bow'), ev('end_taper'); zf = hw - et
    face_x = lambda z: bow * min(1.0, (z / zf) ** 2)
    no = str(int(round(ev('car_no', ''))))
    black = des.appearances.itemByName('Plastic - Matte (Black)')
    white = des.appearances.itemByName('Plastic - Matte (White)')

    def off_plane(base, d, name):
        pi = L.constructionPlanes.createInput(); pi.setByOffset(base, adsk.core.ValueInput.createByReal(d))
        p = L.constructionPlanes.add(pi); p.name = name; p.isLightBulbOn = False; return p

    def dash_plane(zc, name):
        # vertical plane tangent to the bowed front at z = zc
        xz = face_x(zc)
        pz = off_plane(L.xYConstructionPlane, zc, name + ' axis plane')
        sk = L.sketches.add(pz); sk.isVisible = False
        ln = sk.sketchCurves.sketchLines.addByTwoPoints(sk.modelToSketchSpace(P(xz, 40, zc)), sk.modelToSketchSpace(P(xz, 160, zc)))
        slope = 2 * bow * zc / (zf * zf)
        for sgn in (1, -1):
            pi = L.constructionPlanes.createInput()
            pi.setByAngle(ln, adsk.core.ValueInput.createByReal(sgn * math.atan(slope)), L.yZConstructionPlane)
            p = L.constructionPlanes.add(pi)
            n = p.geometry.normal
            # wanted normal parallel to (-1, 0, slope)
            k = math.sqrt(1 + slope * slope)
            if abs(abs(-n.x / k + n.z * slope / k) - 1.0) < 1e-5:
                p.name = name; p.isLightBulbOn = False; return p
            p.deleteMe()
        raise RuntimeError('dash plane orientation')

    def place(pl, base, centre, h, read, out, depth, name, app):
        sk = L.sketches.add(pl)
        o = sk.sketchToModelSpace(P(0, 0, 0)); ux = o.vectorTo(sk.sketchToModelSpace(P(1, 0, 0)))
        uy = o.vectorTo(sk.sketchToModelSpace(P(0, 1, 0)))
        # angled planes (dash) can have any in-plane axes: rotate the decal so that its up is model +Y,
        # then pick the plain/mirrored SVG from the rotated reading axis
        up = V3(0, 1, 0) if abs(V3(*out).y) < 0.9 else V3(*read).crossProduct(V3(*out))
        rot = math.atan2(up.dotProduct(uy), up.dotProduct(ux)) - math.pi / 2
        rx = V3(ux.x * math.cos(rot) + uy.x * math.sin(rot), ux.y * math.cos(rot) + uy.y * math.sin(rot),
                ux.z * math.cos(rot) + uy.z * math.sin(rot))
        f = SVG + base + ('_R' if rx.dotProduct(V3(*read)) > 0 else '_L') + '.svg'
        sk.importSVG(f, 0, 0, PX)
        # ink box from the curves: sketchPoints include the sketch origin, which inflated the box by the ascent
        bbs = [cv.boundingBox for cv in sk.sketchCurves]
        x0, x1 = min(b.minPoint.x for b in bbs), max(b.maxPoint.x for b in bbs)
        y0, y1 = min(b.minPoint.y for b in bbs), max(b.maxPoint.y for b in bbs)
        sk.deleteMe()
        s = h / (y1 - y0)
        tc = None
        sk = L.sketches.add(pl); sk.name = name; sk.isComputeDeferred = True
        tc = sk.modelToSketchSpace(P(*centre))
        sk.importSVG(f, tc.x - s * (x0 + x1) / 2, tc.y - s * (y0 + y1) / 2, PX * s)
        sk.isComputeDeferred = False
        holes = set()
        def key(lp):
            pts = []
            for c in lp.profileCurves:
                b = c.boundingBox; pts += [b.minPoint, b.maxPoint]
            return (round(min(p.x for p in pts), 3), round(min(p.y for p in pts), 3), round(max(p.x for p in pts), 3), round(max(p.y for p in pts), 3))
        for i in range(sk.profiles.count):
            for lp in sk.profiles.item(i).profileLoops:
                if not lp.isOuter: holes.add(key(lp))
        profs = adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count):
            pr = sk.profiles.item(i)
            if key([lp for lp in pr.profileLoops if lp.isOuter][0]) not in holes: profs.add(pr)
        ext = L.features.extrudeFeatures
        ei = ext.createInput(profs, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal(depth))
        fe = ext.add(ei)
        c = fe.bodies.item(0).boundingBox; cm = P((c.minPoint.x + c.maxPoint.x) / 2, (c.minPoint.y + c.maxPoint.y) / 2, (c.minPoint.z + c.maxPoint.z) / 2)
        if P(*centre).vectorTo(cm).dotProduct(V3(*out)) < 0:
            fe.deleteMe(); ei = ext.createInput(profs, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal(-depth)); fe = ext.add(ei)
        fe.name = name
        if abs(rot) > 1e-4:     # Sketch.move ignores imported SVG curves, so turn the extruded bodies instead
            bodies = adsk.core.ObjectCollection.create()
            for b in fe.bodies: bodies.add(b)
            m = adsk.core.Matrix3D.create(); m.setToRotation(rot, ux.crossProduct(uy), P(*centre))
            mi = L.features.moveFeatures.createInput2(bodies); mi.defineAsFreeMove(m)
            L.features.moveFeatures.add(mi).name = name + ' upright'
        for b in fe.bodies:
            b.name = name
            if app: b.appearance = app
        sk.isVisible = False
        if abs(rot) > 1e-4: print('rotated %.0f deg:' % math.degrees(rot), name)
        return fe.bodies.count

    n = 0; D = 0.03
    # front numbers (paint colour: dark on light liveries, white on green)
    lv = int(round(ev('livery', '')))
    numc = white if lv == 3 else (des.appearances.itemByName('GT6 waist stripe') or black) if lv == 1 else black
    hy = ev('hl_y')
    for zc, base in ((-38.0, 'num' + no), (38.0, 'numar' + no)):
        pl = dash_plane(zc, 'Dash plane ' + base)
        n += place(pl, base, (face_x(zc) - 0.01, hy, zc), 15.0, (0, 0, 1), (-1, 0, 0), D, 'Decal front ' + base, numc)
    # destination + route blinds (black on white)
    st = ev('shell_t')
    pd = off_plane(L.yZConstructionPlane, face_x(0) + st + 4.0 - 0.16, 'Destination blind plane')
    n += place(pd, 'dest', (face_x(0) + st + 3.84, ev('dest_bot') + ev('dest_h') / 2, 0), 12.0, (0, 0, 1), (-1, 0, 0), 0.02, 'Decal destination', black)
    pr = off_plane(L.yZConstructionPlane, 11.0 - 0.5, 'Route blind plane')
    n += place(pr, 'route', (10.5, ev('crown_h') - 32 + (ev('route_h') + 29) / 2 + 4, 0), 17.0, (0, 0, 1), (-1, 0, 0), 0.02, 'Decal route', black)
    # operator name, both sides, under the windows of the A section
    ps = off_plane(L.xYConstructionPlane, hw - 0.01, 'Side +z decal plane')
    pn = off_plane(L.xYConstructionPlane, -(hw - 0.01), 'Side -z decal plane')
    yc = ev('belt_h') - 16
    n += place(ps, 'apta', (560.0, yc, hw - 0.01), 9.0, (1, 0, 0), (0, 0, 1), D, 'Decal side apta +z', numc)
    n += place(pn, 'apta', (520.0, yc, -(hw - 0.01)), 9.0, (-1, 0, 0), (0, 0, -1), D, 'Decal side apta -z', numc)
    # rear number plate (Western digits), viewed from behind reads along -Z
    xr = Lc - face_x(40) + 1.5 + 0.01
    prr = off_plane(L.yZConstructionPlane, xr, 'Rear plate plane')
    n += place(prr, 'num' + no, (xr, ev('bumper_y') + 24, -40.0), 8.0, (0, 0, -1), (1, 0, 0), D, 'Decal rear number', black)
    # livery 1: front "V" of the dark-blue waist stripe
    if lv == 1:
        tb = g['TB'](L)
        bs, belt = ev('belt_strip'), ev('belt_h'); dip = 34.0
        for s in (1, -1):
            for k in range(6):
                za, zb = s * (zf - 2) * (1 - k / 6.0), s * (zf - 2) * (1 - (k + 1) / 6.0)
                ya, yb = belt + bs / 2 - dip * (k / 6.0), belt + bs / 2 - dip * ((k + 1) / 6.0)
                xa, xb = face_x(za) - 0.05, face_x(zb) - 0.05
                ln = math.sqrt((xb - xa) ** 2 + (yb - ya) ** 2 + (zb - za) ** 2)
                ax = ((xb - xa) / ln, (yb - ya) / ln, (zb - za) / ln)
                tb.box('Stripe V', (xa + xb) / 2, (ya + yb) / 2, (za + zb) / 2, ln + 1.0, bs * 0.85, 0.1, ax=ax, ay=(0, 1, 0))
        tb.commit('Stripe V')
        blue = des.appearances.itemByName('GT6 waist stripe')
        for b in L.bRepBodies:
            if g['base'](b.name) == 'Stripe V' and blue: b.appearance = blue
    print('decal bodies', n)
