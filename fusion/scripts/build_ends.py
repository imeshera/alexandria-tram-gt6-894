# Front End + Rear End details (TemporaryBRep primitives, one base feature each).
# Front (x = 0): single round headlight low and centred, two round roof marker lamps either side of the
# destination box, raised route-number box on the roof dome, bowed bumper + anticlimber, amber indicators,
# tow pocket, round driver's mirror on the door (right, -z) side.
# Rear (x = car_len): two tail lamps + brake lamps, route-number box under the rear window, bumper, number plate.
import math
import adsk.core, adsk.fusion
import os
ROOT = os.path.dirname(os.path.abspath(__file__))

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}; exec(open(g['__file__']).read(), g)
    des = g['design'](); ev = g['ev_fn'](des)
    hw, crown, L = ev('half_w'), ev('crown_h'), ev('car_len')
    bow, et = ev('nose_bow'), ev('end_taper'); zf = hw - et
    rh = ev('roof_end_r'); rv = crown - ev('dest_bot') - ev('dest_h') - 0.8; cy = crown - rv
    def face_x(z, y=0.0):           # outer skin x at the front for lateral z and height y
        xb = bow * min(1.0, (z / zf) ** 2)
        if y > cy:
            u = min(1.0, (y - cy) / rv); xb = max(xb, rh - rh * math.sqrt(max(0.0, 1 - u * u)))
        return xb

    # ---------------- Front End
    F = g['comp'](des, 'Front End'); g['wipe'](F); tb = g['TB'](F)
    hy, hr = ev('hl_y'), ev('hl_d') / 2
    x0 = face_x(0)
    tb.cyl('Headlight ring', (x0 + 2.0, hy, 0), (x0 - 6.0, hy, 0), hr)
    tb.cyl('Headlight bezel', (x0 - 6.0, hy, 0), (x0 - 7.0, hy, 0), hr - 1.0, hr - 2.2)
    tb.cyl('Headlamp lens', (x0 - 6.5, hy, 0), (x0 - 8.0, hy, 0), hr - 3.2, hr - 4.0)
    # roof marker lamps
    ly, lz = ev('lamp_y'), ev('lamp_z')
    for s in (1, -1):
        xs = face_x(lz, ly)
        tb.cyl('Marker lamp housing', (xs + 4, ly, s * lz), (xs - 5.5, ly, s * lz), 7.5)
        tb.cyl('Marker lamp lens', (xs - 5.5, ly, s * lz), (xs - 7.0, ly, s * lz), 5.8)
        tb.cyl('Marker lamp lens', (xs - 7.0, ly, s * lz), (xs - 7.6, ly, s * lz), 4.5, 3.0)
    # route-number box on the dome
    rw, rhh = ev('route_w'), ev('route_h')
    bx0, bx1, by0, by1 = 11.0, 52.0, crown - 32.0, crown + rhh - 3.0
    tb.box('Route box', (bx0 + bx1) / 2, (by0 + by1) / 2, 0, bx1 - bx0, by1 - by0, rw)
    tb.box('Route box glass', bx0 - 0.9, (by0 + by1) / 2 + 4, 0, 0.6, (by1 - by0) - 16, rw - 6)
    tb.box('Route box blind', bx0 - 0.3, (by0 + by1) / 2 + 4, 0, 0.4, (by1 - by0) - 18, rw - 8)
    for s in (1, -1):        # glazing frame
        tb.box('Route box hood', bx0 - 0.9, (by0 + by1) / 2 + 4, s * (rw / 2 - 1.5), 1.6, (by1 - by0) - 14, 3.0)
    tb.box('Route box hood', bx0 + 4, by1 + 0.8, 0, 12, 1.6, rw + 2)
    # bumper: three segments following the bow, anticlimber ribs
    byb = ev('bumper_y')
    segs = [(-55.0, 55.0)] + [(55.0, 86.0)] + [(-86.0, -55.0)]
    for za, zb in segs:
        xa, xb = face_x(za) - 4.5, face_x(zb) - 4.5
        Lseg = math.hypot(xb - xa, zb - za); ax = ((xb - xa) / Lseg, 0, (zb - za) / Lseg)
        tb.box('Bumper', (xa + xb) / 2, byb + 6, (za + zb) / 2, Lseg + 1, 12, 9, ax=ax)
    for k in range(3):
        tb.box('Anticlimber rib', face_x(0) - 9.3, byb + 2.5 + k * 3.5, 0, 1.2, 1.2, 100)
    tb.box('Tow pocket', face_x(0) + 2, byb - 6, 0, 16, 9, 22)
    # amber indicators either side, at waist height
    for s in (1, -1):
        z = s * (zf - 12); y = ev('belt_h') - 18
        tb.box('Indicator', face_x(z) - 1.2, y, z, 3.0, 9, 6)
    # driver's round mirror on the door side (-z) at the cab corner
    za = -(hw - 4)
    tb.cyl('Mirror arm', (30.0, 236.0, za), (-6.0, 226.0, -(hw + 16)), 1.1)
    tb.cyl('Mirror', (-6.0, 226.0, -(hw + 16)), (-4.0, 226.0, -(hw + 16)), 9.0)
    tb.commit('Front End')

    # ---------------- Rear End
    Rr = g['comp'](des, 'Rear End'); g['wipe'](Rr); tr = g['TB'](Rr)
    rx = lambda z, y=0.0: L - face_x(z, y)
    for s in (1, -1):
        z = s * 52.0
        tr.cyl('Tail lamp housing', (rx(z) - 2, 98.0, z), (rx(z) + 3.0, 98.0, z), 6.5)
        tr.cyl('Tail lamp lens', (rx(z) + 3.0, 98.0, z), (rx(z) + 4.0, 98.0, z), 5.5)
        tr.cyl('Brake lamp lens', (rx(z) - 2, 114.0, z), (rx(z) + 3.5, 114.0, z), 4.5)
        tr.box('Indicator', rx(s * (zf - 12)) + 1.2, ev('belt_h') - 18, s * (zf - 12), 3.0, 9, 6)
    tr.box('Rear route box', rx(0) + 1.5, ev('win_bot') - 22, 0, 4.0, 26, 30)
    tr.box('Route box glass', rx(0) + 3.6, ev('win_bot') - 22, 0, 0.4, 20, 24)
    for za, zb in [(-55.0, 55.0), (55.0, 86.0), (-86.0, -55.0)]:
        xa, xb = rx(za) + 4.5, rx(zb) + 4.5
        Lseg = math.hypot(xb - xa, zb - za); ax = ((xb - xa) / Lseg, 0, (zb - za) / Lseg)
        tr.box('Bumper', (xa + xb) / 2, byb + 6, (za + zb) / 2, Lseg + 1, 12, 9, ax=ax)
    tr.box('Number plate', rx(-40) + 1.0, byb + 24, -40.0, 1.0, 12, 32)
    tr.commit('Rear End')
    print('front bodies', F.bRepBodies.count, '| rear bodies', Rr.bRepBodies.count)
