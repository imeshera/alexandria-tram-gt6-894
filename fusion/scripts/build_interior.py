# Interior: component Interior (wood-slat floor with step wells, wall linings, ribbed ceiling, fluorescent
# light strips, stainless stanchions + ceiling grab rails, heaters, conductor's desk + seat behind door 3),
# and two instanced seat components 'Seat double' / 'Seat single' (varnished wooden slats on a tubular steel
# frame, chrome grab bar on the back) placed as root occurrences: 2+1 layout, all facing the cab, 36 seats (KS).
# Seat material is E: Alexandria 2010 interior photo shows hard brown seat backs; Copenhagen trim unknown.
import math
import adsk.core, adsk.fusion
import os
ROOT = os.path.dirname(os.path.abspath(__file__))

def seat(g, des, name, width):
    root = des.rootComponent
    C = None
    for o in root.occurrences:
        if o.component.name == name: C = o.component
    if C is None:
        C = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component; C.name = name
    g['wipe'](C); tb = g['TB'](C)
    # local: origin on the floor under the seat centre, passenger faces -X, seat spans z +/- width/2
    w2 = width / 2; sy = 45.0; d = 44.0
    for k in range(5):                                    # seat slats (front to back)
        x = -d / 2 + 4.5 + k * 8.7
        tb.box('Seat slat', x, sy - 0.5 * (k / 4.0), 0, 7.2, 1.8, width - 2)
    tb.box('Seat slat', -d / 2 + 1.0, sy - 3.0, 0, 2.0, 5.0, width - 2)      # rounded front rail
    bt = math.radians(14)                                 # backrest rake
    for k in range(6):                                    # back slats rising + leaning back
        r = 8.0 + k * 8.4
        tb.box('Back slat', d / 2 - 2 + r * math.sin(bt), sy + 3 + r * math.cos(bt), 0, 1.8, 7.0, width - 2,
               ax=(math.cos(bt), -math.sin(bt), 0), ay=(math.sin(bt), math.cos(bt), 0))
    # frame: two side frames (legs + arm-less rails), cross tubes, grab bar on top of the back
    for s in (-1, 1):
        z = s * (w2 - 1.5)
        tb.cyl('Seat frame', (-d / 2 + 4, 0, z), (-d / 2 + 4, sy - 2, z), 1.3)
        tb.cyl('Seat frame', (d / 2 - 3, 0, z), (d / 2 - 3, sy - 2, z), 1.3)
        tb.cyl('Seat frame', (-d / 2 + 2, sy - 2, z), (d / 2 - 1, sy - 2, z), 1.3)
        top = (d / 2 - 2 + 56 * math.sin(bt), sy + 3 + 56 * math.cos(bt), z)
        tb.cyl('Seat frame', (d / 2 - 1, sy - 2, z), top, 1.3)
        tb.box('Seat foot', -d / 2 + 4, 0.4, z, 5, 0.8, 4)
        tb.box('Seat foot', d / 2 - 3, 0.4, z, 5, 0.8, 4)
    tb.cyl('Seat frame', (-d / 2 + 4, 8, -w2 + 1.5), (-d / 2 + 4, 8, w2 - 1.5), 1.1)
    tb.cyl('Seat frame', (d / 2 - 3, 8, -w2 + 1.5), (d / 2 - 3, 8, w2 - 1.5), 1.1)
    gx, gy = d / 2 - 2 + 60 * math.sin(bt), sy + 3 + 60 * math.cos(bt)
    tb.cyl('Grab bar', (gx, gy, -w2 + 3), (gx, gy, w2 - 3), 1.2)
    for s in (-1, 1):
        tb.cyl('Grab bar', (gx, gy, s * (w2 - 3)), (gx - 3.5, gy - 6, s * (w2 - 3)), 1.2)
    tb.commit(name)
    return C

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}; exec(open(g['__file__']).read(), g)
    o = {'__file__': os.path.join(ROOT, 'build_openings.py')}; exec(open(o['__file__']).read(), o)
    des = g['design'](); ev = g['ev_fn'](des); root = des.rootComponent
    I = g['comp'](des, 'Interior'); g['wipe'](I); tb = g['TB'](I)
    hw, fl, st = ev('half_w'), ev('floor_h'), ev('shell_t')
    L, la, gap, ax = ev('car_len'), ev('sec_a_len'), ev('artic_gap'), ev('artic_x')
    crown, eave, t, belt = ev('crown_h'), ev('eave_h'), ev('tumble'), ev('belt_h')
    tl, et, bow = ev('taper_len'), ev('end_taper'), ev('nose_bow')
    # outer skin half-width in plan: straight taper to the end, joined to the side by the taper_blend arc (R 15 m)
    Rb = ev('taper_blend'); th = math.atan(et / (tl - bow)); db = Rb * math.tan(th / 2)
    def side_z(x):
        u = x if x < L / 2 else L - x                  # distance from the nearer end
        if u >= tl + db: return hw
        if u > tl + db - Rb * math.sin(th):            # on the blend arc
            return hw - Rb + math.sqrt(Rb * Rb - (u - tl - db) ** 2)
        return hw - et * (tl - u) / (tl - bow)
    lay = o['layout'](ev)
    doors = [(x0, x1) for x0, x1, y0, y1, k in lay['R'] if k == 'door']
    secs = [(25.0, la - 2.0), (la + gap + 2.0, L - 25.0)]
    # ---- floor: longitudinal varnished slats, skipping the step wells at the doors (-z side, 58 cm deep)
    n_sl = 34; pitch = (2 * hw - 12) / n_sl
    for x0s, x1s in secs:
        for i in range(n_sl):
            z = -hw + 6 + pitch * (i + 0.5)
            segs = [(x0s, x1s)]
            if z < -hw + 60:
                for d0, d1 in doors:
                    nxt = []
                    for a, b in segs:
                        if d1 <= a or d0 >= b: nxt.append((a, b)); continue
                        if d0 > a: nxt.append((a, d0))
                        if d1 < b: nxt.append((d1, b))
                    segs = nxt
            for a, b in segs:
                xa, xb = a, b
                zz = abs(z) + pitch / 2
                if xa < tl and zz > side_z(xa) - st - 1: xa = min(tl, xa + (zz - (side_z(xa) - st - 1)) / et * (tl - bow) + 2)
                if xb > L - tl and zz > side_z(xb) - st - 1: xb = max(L - tl, xb - (zz - (side_z(xb) - st - 1)) / et * (tl - bow) - 2)
                if xb - xa > 5:
                    tb.box('Floor slat', (xa + xb) / 2, fl - 1.0, z, xb - xa, 2.0, pitch - 0.5)
        tb.box('Floor base', (x0s + x1s) / 2, fl - 3.5, 0, x1s - x0s - 4, 3.0, 2 * hw - 140)
    # ---- wall linings below the windows (wood veneer), between doors on the right
    for side, sgn in (('L', 1), ('R', -1)):
        for x0s, x1s in secs:
            spans = [(x0s + 150 if x0s < 100 else x0s, x1s)]
            if side == 'R':
                nxt = []
                for a, b in spans:
                    cur = a
                    for d0, d1 in sorted(doors):
                        if d1 <= cur or d0 >= b: continue
                        if d0 > cur: nxt.append((cur, d0))
                        cur = max(cur, d1)
                    if cur < b: nxt.append((cur, b))
                spans = nxt
            for a, b in spans:
                if b - a < 10: continue
                # (a single straight box at side_z(midpoint) poked through the skin in the taper zone)
                # taper zones (taper + blend arc) are cut into short chords; the straight middle is one box
                e0, e1 = tl + db, L - tl - db
                cuts = sorted(set([a, b] + [c for c in (e0, e1) if a < c < b] +
                                  [a + k * 30.0 for k in range(1, 40) if a + k * 30.0 < min(b, e0)] +
                                  [b - k * 30.0 for k in range(1, 40) if b - k * 30.0 > max(a, e1)]))
                for p, q in zip(cuts[:-1], cuts[1:]):
                    if q - p < 2: continue
                    xm = (p + q) / 2
                    s = (side_z(q) - side_z(p)) / (q - p)
                    n = (1 + s * s) ** 0.5; ax = (1 / n, 0, sgn * s / n)
                    ln = (q - p) * n
                    zin = (side_z(p) + side_z(q)) / 2 - st - 1.0      # chord midpoint lies inside the convex arc
                    tb.box('Wall lining', xm, (fl + ev('win_bot')) / 2 - 2, sgn * zin, ln,
                           ev('win_bot') - fl - 4, 1.2, ax=ax)
                    hp, hq = max(p, a + 10), min(q, b - 10)
                    if hq - hp > 5:
                        xh = (hp + hq) / 2
                        tb.box('Heater', xh, fl + 14, sgn * (zin - 7.0), (hq - hp) * n, 16, 7, ax=ax)
    # ---- ceiling: transverse ribs + two fluorescent light strips + ceiling grab rails
    a_ = hw - t; h_ = crown - eave; Rr = (a_ * a_ + h_ * h_) / (2 * h_); yc = crown - Rr
    roof_y = lambda z: yc + math.sqrt(max(0.0, Rr * Rr - z * z))
    for x0s, x1s in secs:
        nrib = int((x1s - x0s - 60) / 71.0)
        for k in range(nrib + 1):
            x = x0s + 30 + k * 71.0
            for j in range(8):
                za, zb = -a_ + 8 + j * (2 * a_ - 16) / 8, -a_ + 8 + (j + 1) * (2 * a_ - 16) / 8
                ya, yb = roof_y(za) - 4.5, roof_y(zb) - 4.5
                ln = math.hypot(zb - za, yb - ya)
                if abs(za) > side_z(x) - 15 or abs(zb) > side_z(x) - 15: continue
                tb.box('Ceiling rib', x, (ya + yb) / 2, (za + zb) / 2, 3.0, 2.0, ln,
                       ax=(1, 0, 0), ay=(0, (zb - za) / ln, -(yb - ya) / ln))
        for s in (1, -1):
            z = s * 52.0; y = roof_y(z) - 8
            tb.box('Light diffuser', (x0s + x1s) / 2, y, z, x1s - x0s - 260, 4.0, 9.0, ay=(0, 0.94, -s * 0.34))
            tb.box('Light housing', (x0s + x1s) / 2, y + 2.6, z, x1s - x0s - 250, 2.0, 11.0, ay=(0, 0.94, -s * 0.34))
            tb.cyl('Ceiling rail', (x0s + 60, 205.0, s * 40.0 - 15), (x1s - 60, 205.0, s * 40.0 - 15), 1.5)
            for k in range(int((x1s - x0s - 120) / 180) + 1):
                xx = x0s + 60 + k * 180
                tb.cyl('Rail bracket', (xx, 205.0, s * 40.0 - 15), (xx, roof_y(s * 40.0 - 15) - 4, s * 40.0 - 15), 0.9)
    # ---- stanchions at the door edges and along the aisle
    for d0, d1 in doors:
        for xx in (d0 - 5, d1 + 5):
            z = -(side_z(xx) - 28)
            tb.cyl('Grab pole', (xx, fl, z), (xx, roof_y(z) - 3, z), 1.6)
    for xx in (330.0, 490.0, 650.0, 1180.0, 1340.0, 1500.0, 1660.0):
        tb.cyl('Grab pole', (xx, fl, -18.0), (xx, roof_y(-18.0) - 3, -18.0), 1.6)
    # ---- cab partition (driver's back wall with glazed upper part, open on the door side)
    xp = 145.0
    tb.box('Cab partition', xp, (fl + 205) / 2, (side_z(xp) - 18) / 2 + 8, 3.0, 205 - fl, side_z(xp) + 18 - 16)
    tb.box('Cab partition glass', xp - 1.6, 175.0, (side_z(xp) - 18) / 2 + 8, 0.6, 50.0, side_z(xp) - 30)
    # ---- conductor's desk + seat behind door 3 (E: Alexandria city practice, 2010 urbanrail photo)
    d3 = ev('door3_x') + ev('door_w')
    zc = -(hw - 45)
    tb.box('Conductor desk', d3 + 40, fl + 52, zc + 30, 60, 104, 8)        # front panel facing the aisle
    tb.box('Conductor desk', d3 + 40, fl + 105, zc + 18, 64, 3, 34)       # desk top
    tb.box('Conductor desk', d3 + 10, fl + 52, zc + 8, 3, 104, 50)
    tb.box('Conductor desk', d3 + 70, fl + 52, zc + 8, 3, 104, 50)
    tb.box('Conductor seat', d3 + 40, fl + 50, zc - 10, 40, 4, 34)
    tb.cyl('Conductor seat', (d3 + 40, fl, zc - 10), (d3 + 40, fl + 48, zc - 10), 2.5)
    tb.box('Conductor seat', d3 + 40, fl + 75, zc - 28, 40, 45, 3)
    tb.box('Ticket box', d3 + 40, fl + 112, zc + 18, 26, 12, 20)
    tb.commit('Interior')

    # ---- seats as instanced components, all facing the cab (-X)
    sd = seat(g, des, 'Seat double', 92.0); ss = seat(g, des, 'Seat single', 46.0)
    zl = hw - 9 - 46.0; zr = -(hw - 9 - 23.0)
    xl = [240.0 + k * 80 for k in range(6)] + [1100.0 + k * 80 for k in range(7)]
    xr = [340.0 + k * 80 for k in range(5)] + [d3 + 120 + k * 80 for k in range(5)]
    def place(C, pts):
        occs = [oc for oc in root.occurrences if oc.component == C]
        while len(occs) < len(pts):
            occs.append(root.occurrences.addExistingComponent(C, adsk.core.Matrix3D.create()))
        for oc in occs[len(pts):]: oc.deleteMe()
        for oc, (x, z) in zip(occs, pts):
            m = adsk.core.Matrix3D.create(); m.translation = adsk.core.Vector3D.create(x, fl, z); oc.transform2 = m
    place(sd, [(x, zl) for x in xl]); place(ss, [(x, zr) for x in xr])
    if des.snapshots.hasPendingSnapshot:
        des.snapshots.add()
    print('interior bodies', I.bRepBodies.count, '| seats', 2 * len(xl) + len(xr))
