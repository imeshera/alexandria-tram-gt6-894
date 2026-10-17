# Cab (component Cab): one-man front cab of the single-ended GT6 (E from KS/Duewag practice + 830/890 photos):
# full-width dash console under the windscreen, angled instrument panel (speedometer, line voltmeter, brake
# pressure), Duewag hand controller (Fahrschalter) on a column with crank handle to the driver's left,
# reverser key, push-button + switch panel, foot gong / deadman pedals, sun blind, driver's swivel seat,
# destination-blind winding handle, fire extinguisher, cab heater.
import math
import adsk.core, adsk.fusion
import os
ROOT = os.path.dirname(os.path.abspath(__file__))

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}; exec(open(g['__file__']).read(), g)
    des = g['design'](); ev = g['ev_fn'](des)
    C = g['comp'](des, 'Cab'); g['wipe'](C); tb = g['TB'](C)
    hw, fl, wsb = ev('half_w'), ev('floor_h'), ev('ws_bot')
    bow, et = ev('nose_bow'), ev('end_taper'); zf = hw - et
    face_x = lambda z: bow * min(1.0, (z / zf) ** 2)
    st = ev('shell_t')
    # dash console: three segments following the bowed front, top just under the windscreen
    for za, zb in [(-50.0, 50.0), (50.0, zf - 6), (-(zf - 6), -50.0)]:
        xa, xb = face_x(za) + st + 20, face_x(zb) + st + 20
        Ls = math.hypot(xb - xa, zb - za); ax = ((xb - xa) / Ls, 0, (zb - za) / Ls)
        tb.box('Dash console', (xa + xb) / 2, (fl + wsb) / 2 - 1, (za + zb) / 2, Ls, wsb - fl - 2, 36, ax=ax)
        tb.box('Dash top', (xa + xb) / 2 - 2, wsb - 1.5, (za + zb) / 2, Ls, 3, 44, ax=ax)
    # instrument panel facing the driver (driver sits on the centre-line, slightly left)
    zd = 10.0
    tilt = math.radians(35)
    px, py = 42.0, wsb + 6
    tb.box('Instrument panel', px, py, zd, 6.0, 26, 64, ax=(math.cos(tilt), math.sin(tilt), 0), ay=(-math.sin(tilt), math.cos(tilt), 0))
    for k, dz in enumerate((-20.0, 0.0, 20.0)):
        cx, cy = px + 3.4 * math.cos(tilt), py + 3.4 * math.sin(tilt)
        n = (math.cos(tilt), math.sin(tilt), 0)
        a = (cx, cy, zd + dz); b = (cx + 1.2 * n[0], cy + 1.2 * n[1], zd + dz)
        tb.cyl('Gauge bezel', a, b, 7.2)
        tb.cyl('Gauge face', b, (b[0] + 0.3 * n[0], b[1] + 0.3 * n[1], b[2]), 6.4)
    # controller column + crank (driver's left = +z side when facing -X)
    cz = zd + 38
    tb.cyl('Controller', (55.0, fl, cz), (55.0, fl + 95, cz), 9.0)
    tb.cyl('Controller', (55.0, fl + 95, cz), (55.0, fl + 101, cz), 11.0)
    tb.cyl('Controller handle', (55.0, fl + 101, cz), (55.0, fl + 106, cz), 2.0)
    tb.cyl('Controller handle', (55.0, fl + 106, cz), (40.0, fl + 106, cz + 8), 1.5)
    tb.cyl('Controller knob', (40.0, fl + 106, cz + 8), (40.0, fl + 113, cz + 8), 2.4)
    tb.box('Reverser key', 55.0, fl + 102, cz - 10, 3, 2, 8)
    # brake valve / handle to the driver's right
    bz = zd - 36
    tb.cyl('Brake valve', (52.0, fl + 60, bz), (52.0, fl + 92, bz), 6.5)
    tb.cyl('Brake handle', (52.0, fl + 94, bz), (36.0, fl + 96, bz - 10), 1.4)
    # switch panel on the right wing of the dash
    tb.box('Switch panel', 30.0, wsb + 1.0, -62.0, 22, 2.0, 30)
    for i in range(6):
        tb.cyl('Switch', (24.0 + (i % 3) * 6, wsb + 2.0, -70.0 + (i // 3) * 12), (24.0 + (i % 3) * 6, wsb + 4.0, -70.0 + (i // 3) * 12), 1.4)
    # pedals
    for dz in (-10.0, 6.0, 22.0):
        tb.box('Pedal', 44.0, fl + 8, zd + dz, 16, 2.5, 9, ax=(math.cos(0.5), math.sin(0.5), 0), ay=(-math.sin(0.5), math.cos(0.5), 0))
    # driver's seat on a pedestal
    sx = 105.0
    tb.cyl('Driver seat base', (sx, fl, zd), (sx, fl + 45, zd), 5.0)
    tb.box('Driver seat', sx, fl + 50, zd, 46, 9, 46)
    tb.box('Driver seat', sx + 21, fl + 82, zd, 8, 58, 44, ax=(math.cos(-0.2), math.sin(-0.2), 0), ay=(math.sin(0.2), math.cos(0.2), 0))
    # sun blind, destination winding handle, extinguisher, heater
    tb.box('Sun blind', face_x(0) + 18, ev('ws_top') - 8, 0, 2, 16, 110)
    tb.cyl('Blind handle', (face_x(0) + 12, ev('dest_bot') - 6, 40), (face_x(0) + 22, ev('dest_bot') - 6, 40), 0.9)
    tb.cyl('Fire extinguisher', (135.0, fl, 80.0), (135.0, fl + 52, 80.0), 7.0)
    tb.box('Cab heater', 70.0, fl + 12, 70.0, 40, 22, 14)
    tb.commit('Cab')
    print('cab bodies', C.bRepBodies.count)
