# Doors (component Doors): Duewag 4-panel folding doors on the right side (-z), closed.
# Each panel = lower leaf (body colour, below the waist) + upper leaf (window band colour, glazed) + glass,
# vertical grab handle on the leading panels; the front door also has the KS lower glazing.
# Panels follow the plan taper at the ends and the tumblehome above the waist. Interior entrance steps.
import math
import adsk.core, adsk.fusion
import os
ROOT = os.path.dirname(os.path.abspath(__file__))

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}; exec(open(g['__file__']).read(), g)
    o = {'__file__': os.path.join(ROOT, 'build_openings.py')}; exec(open(o['__file__']).read(), o)
    des = g['design'](); ev = g['ev_fn'](des)
    C = g['comp'](des, 'Doors'); g['wipe'](C)
    tb = g['TB'](C); tbm = tb.tbm
    hw, t, belt, eave = ev('half_w'), ev('tumble'), ev('belt_h'), ev('eave_h')
    L, tl, et, bow = ev('car_len'), ev('taper_len'), ev('end_taper'), ev('nose_bow')
    ang = math.atan2(t, eave - belt)
    def side_z(x):                  # plan half-width of the skin at x (linear taper approximation)
        if x < tl: return hw - et * (tl - x) / (tl - bow)
        if x > L - tl: return hw - et * (x - (L - tl)) / (tl - bow)
        return hw
    def yaw(x):
        if x < tl: return math.atan2(et, tl - bow)
        if x > L - tl: return -math.atan2(et, tl - bow)
        return 0.0
    def panel_box(name, cx, cy, lx, ly, lz, inset, tilt):
        a = yaw(cx); z = -(side_z(cx) - inset - (t * max(0.0, cy - belt) / (eave - belt) if tilt else 0.0))
        ax = (math.cos(a), 0, math.sin(a))          # along the panel; -z side so taper turns toward -x... small angle
        ay = (0, math.cos(ang), math.sin(ang)) if tilt else (0, 1, 0)
        d = sum(p * q for p, q in zip(ax, ay)); ay = tuple(q - d * p for p, q in zip(ax, ay))
        n = math.sqrt(sum(q * q for q in ay)); ay = tuple(q / n for q in ay)
        ob = adsk.core.OrientedBoundingBox3D.create(adsk.core.Point3D.create(cx, cy, z), adsk.core.Vector3D.create(*ax),
                                                    adsk.core.Vector3D.create(*ay), lx, ly, lz)
        return tbm.createBox(ob)
    lay = o['layout'](ev)
    floor = ev('floor_h'); n_doors = 0
    for x0, x1, y0, y1, k in lay['R']:
        if k != 'door':
            continue
        n_doors += 1
        front_door = abs(x0 - ev('door1_x')) < 1
        pw = (x1 - x0) / 4.0
        for i in range(4):
            cx = x0 + pw * (i + 0.5)
            lo = panel_box('', cx, (y0 + 1 + belt) / 2, pw - 0.5, belt - y0 - 1, 2.4, 2.0, False)
            ylo, yhi = belt, y1 - 1
            up = panel_box('', cx, (ylo + yhi) / 2, pw - 0.5, yhi - ylo, 2.4, 2.0, True)
            # upper window
            wy0, wy1 = belt + 9, yhi - 12
            hole = panel_box('', cx, (wy0 + wy1) / 2, pw - 11, wy1 - wy0, 6.0, 2.0, True)
            tbm.booleanOperation(up, hole, adsk.fusion.BooleanTypes.DifferenceBooleanType)
            tb.parts.append(('Door leaf upper', up))
            tb.parts.append(('Door glass', panel_box('', cx, (wy0 + wy1) / 2, pw - 9, wy1 - wy0 + 2, 0.6, 2.6, True)))
            if front_door:      # KS: extra lower glazing in the front door leaves
                ly0, ly1 = y0 + 34, belt - 20
                hole = panel_box('', cx, (ly0 + ly1) / 2, pw - 13, ly1 - ly0, 6.0, 2.0, False)
                tbm.booleanOperation(lo, hole, adsk.fusion.BooleanTypes.DifferenceBooleanType)
                tb.parts.append(('Door glass', panel_box('', cx, (ly0 + ly1) / 2, pw - 11, ly1 - ly0 + 2, 0.6, 2.6, False)))
            tb.parts.append(('Door leaf lower', lo))
            # rubber seals between panels
            tb.parts.append(('Door seal', panel_box('', x0 + pw * (i + 1) - 0.25 if i < 3 else x0 + 0.6, (y0 + y1) / 2, 0.8, y1 - y0 - 4, 2.8, 1.6, False)))
        # grab handles on the two centre panels (inside, stainless)
        for s in (-1, 1):
            hx = (x0 + x1) / 2 + s * pw * 0.7
            z = -(side_z(hx) - 6.0)
            tb.cyl('Door handle', (hx, belt - 20, z), (hx, belt + 45, z), 1.3)
        # interior steps: two risers from the door sill up to the floor
        zc = -(side_z((x0 + x1) / 2))
        for j, (yy, d0, d1) in enumerate(((ev('door_bot'), 2.5, 30.0), (ev('door_bot') + (floor - ev('door_bot')) / 2, 30.0, 58.0))):
            tb.box('Step tread', (x0 + x1) / 2, yy - 1.5, zc + (d0 + d1) / 2, x1 - x0 - 2, 3.0, d1 - d0)
            tb.box('Step riser', (x0 + x1) / 2, (yy + (yy + (floor - ev('door_bot')) / 2)) / 2 - 1.5, zc + d1, x1 - x0 - 2,
                   (floor - ev('door_bot')) / 2, 2.0)
    import time; t0 = time.time()
    tb.commit('Doors')
    print('commit s', round(time.time() - t0, 1))
    print('doors', n_doors, '| bodies', C.bRepBodies.count)
