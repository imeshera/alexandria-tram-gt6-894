# Running gear: Duewag tandem-drive motor bogie (one longitudinal motor driving both axles through cardan
# shafts and right-angle gearboxes, outside side frames, rubber chevron primary springs, magnetic track brakes)
# as one component 'Motor bogie' with two root occurrences (bogie_a_x, bogie_b_x), and the Jacobs trailer bogie
# 'Jacobs bogie' under the articulation (artic_x). Local frame: origin at bogie centre on top of rail.
import math
import adsk.core, adsk.fusion
import os
ROOT = os.path.dirname(os.path.abspath(__file__))

def build(g, des, ev, name, motor):
    root = des.rootComponent
    C = None
    for o in root.occurrences:
        if o.component.name == name:
            C = o.component
    if C is None:
        C = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component; C.name = name
    g['wipe'](C)
    tb = g['TB'](C)
    R = ev('wheel_d') / 2; wb = ev('bogie_wb'); b2 = ev('back_to_back') / 2; tw = ev('tread_w')
    fz = ev('gauge') / 2 + 22.0          # outside side-frame centre
    for sx in (-1, 1):
        x = sx * wb / 2
        for sz in (-1, 1):
            zi = sz * b2; zo = sz * (b2 + tw)
            tb.cyl('Wheel', (x, R, zi + sz * 0.0), (x, R, zo), R)                       # tread
            tb.cyl('Wheel', (x, R, zi - sz * 0.0), (x, R, zi + sz * 2.6), R + 2.4)       # flange
            tb.cyl('Wheel', (x, R, zi - sz * 3.0), (x, R, zo + sz * 2.0), 11.0)          # hub
            tb.cyl('Wheel', (x, R, zi + sz * 3.5), (x, R, zi + sz * 7.5), R - 5.0)       # web/rubber ring
            # axlebox + chevron springs + side-frame horn
            tb.box('Axlebox', x, R, sz * fz, 24, 22, 16)
            tb.cyl('Axlebox cover', (x, R, sz * (fz + 8)), (x, R, sz * (fz + 11)), 8.5)
            for dx in (-14, 14):
                tb.box('Primary spring', x + dx, R + 4, sz * fz, 8, 16, 14)
                tb.box('Primary spring', x + dx * 0.9, R + 12, sz * fz, 9, 2.5, 15)
        tb.cyl('Axle', (x, R, -(fz + 6)), (x, R, fz + 6), 6.5)
        if motor:          # right-angle gearbox on each axle
            tb.box('Gearbox', x - sx * 14, R, 0, 30, 34, 30)
            tb.cyl('Cardan shaft', (x - sx * 29, R, 0), (sx * 34, R, 0), 4.0)
    for sz in (-1, 1):
        # side frame: top chord, two end drops, central spring pocket
        tb.box('Side frame', 0, R + 24, sz * fz, wb + 70, 16, 12)
        tb.box('Side frame', 0, R + 6, sz * fz, 60, 30, 12)
        for sx in (-1, 1):
            tb.box('Side frame', sx * (wb / 2 + 26), R + 14, sz * fz, 12, 30, 12)
        # secondary (bolster) springs
        tb.cyl('Secondary spring', (-16, R + 32, sz * (fz - 8)), (-16, R + 52, sz * (fz - 8)), 10)
        tb.cyl('Secondary spring', (16, R + 32, sz * (fz - 8)), (16, R + 52, sz * (fz - 8)), 10)
        # magnetic track brake shoe between the wheels, over the rail
        tb.box('Track brake', 0, 7.5, sz * (b2 + tw / 2), wb - 2 * R - 18, 9, 9)
        tb.box('Track brake hanger', -(wb / 2 - R - 20), 18, sz * (b2 + tw / 2), 4, 18, 4)
        tb.box('Track brake hanger', (wb / 2 - R - 20), 18, sz * (b2 + tw / 2), 4, 18, 4)
        # sanding pipe
        tb.cyl('Sand pipe', (-(wb / 2 + R * 0.6), R + 10, sz * (b2 + tw / 2)), (-(wb / 2 + R * 0.25), 4, sz * (b2 + tw / 2)), 1.6)
    tb.box('Transom', 0, R + 22, 0, 36, 16, 2 * fz - 10)
    tb.box('Bolster', 0, R + 54, 0, 46, 12, 2 * fz + 4)
    tb.cyl('Slewing ring', (0, R + 60, 0), (0, R + 64, 0), 34)
    if motor:
        tb.cyl('Traction motor', (-34, R, 0), (34, R, 0), 22)
        tb.box('Motor feet', 0, R - 6, 0, 50, 10, 52)
        tb.cyl('Motor fan cowl', (34, R, 0), (40, R, 0), 18)
    else:
        tb.box('Articulation bearing', 0, R + 70, 0, 60, 10, 60)
    tb.commit(name)
    return C

def place(des, C, xs):
    root = des.rootComponent
    occs = [o for o in root.occurrences if o.component == C]
    while len(occs) < len(xs):
        occs.append(root.occurrences.addExistingComponent(C, adsk.core.Matrix3D.create()))
    for o in occs[len(xs):]:
        o.deleteMe()
    for o, x in zip(occs, xs):
        m = adsk.core.Matrix3D.create(); m.translation = adsk.core.Vector3D.create(x, 0, 0); o.transform2 = m
    if des.snapshots.hasPendingSnapshot:
        des.snapshots.add()

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}; exec(open(g['__file__']).read(), g)
    des = g['design'](); ev = g['ev_fn'](des)
    mb = build(g, des, ev, 'Motor bogie', True)
    jb = build(g, des, ev, 'Jacobs bogie', False)
    place(des, mb, [ev('bogie_a_x'), ev('bogie_b_x')])
    place(des, jb, [ev('artic_x')])
    print('motor bogie bodies', mb.bRepBodies.count, '| jacobs', jb.bRepBodies.count)
