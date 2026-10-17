# Roof Equipment: trolley pole (spring base, pole, trolley harp + wheel, retriever rope stub) on the A-section
# roof at pole_x, or (panto_on = 1) the diamond pantograph seen on the 2019 Raml-line cars; resistor cover with
# louvres, lightning arrester, roof cable conduit, pole hook on the B section.
import math
import adsk.core, adsk.fusion
import os
ROOT = os.path.dirname(os.path.abspath(__file__))

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}; exec(open(g['__file__']).read(), g)
    des = g['design'](); ev = g['ev_fn'](des)
    up = des.userParameters
    if up.itemByName('pole_ang') and up.itemByName('pole_ang').expression == '14 deg':
        up.itemByName('pole_ang').expression = '23 deg'
        up.itemByName('pole_ang').comment = 'Pole elevation on the wire (~5.5 m contact wire), V: KS 818 ~25 deg'
    C = g['comp'](des, 'Roof Equipment'); g['wipe'](C); tb = g['TB'](C)
    crown, hw, t, eave = ev('crown_h'), ev('half_w'), ev('tumble'), ev('eave_h')
    # roof surface height at lateral z (3-point arc through eave corners and crown)
    a = hw - t; h = crown - eave; Rr = (a * a + h * h) / (2 * h); yc = crown - Rr
    roof_y = lambda z: yc + math.sqrt(max(0.0, Rr * Rr - z * z))
    px = ev('pole_x')
    # resistor / equipment cover ahead of the pole base
    x0, x1 = 210.0, px - 45.0
    tb.box('Resistor cover', (x0 + x1) / 2, crown + 9, 0, x1 - x0, 18, 110)
    tb.box('Resistor cover', (x0 + x1) / 2, crown + 18.6, 0, x1 - x0 + 4, 1.2, 116)
    n = int((x1 - x0) / 9)
    for k in range(n):
        for s in (1, -1):
            tb.box('Louvre', x0 + 6 + k * 9, crown + 9, s * 55.4, 4.5, 11, 1.0)
    for s in (1, -1):
        for xx in (x0 + 12, x1 - 12):
            tb.box('Cover foot', xx, (roof_y(s * 48) + crown) / 2, s * 48, 8, crown - roof_y(s * 48) + 2, 8)
    tb.cyl('Cable conduit', (x0 - 30, roof_y(70) + 3, 70), (px + 40, roof_y(70) + 3, 70), 2.2)
    tb.cyl('Lightning arrester', (px + 45, crown, -30), (px + 45, crown + 16, -30), 4.5)
    tb.cyl('Insulator', (px + 45, crown + 16, -30), (px + 45, crown + 22, -30), 6.0)
    if round(ev('panto_on', '')) != 1:
        # trolley base: plate, swivel, twin springs, pivot
        tb.box('Pole base', px, crown + 4, 0, 70, 8, 56)
        tb.cyl('Pole base', (px, crown + 8, 0), (px, crown + 18, 0), 16)
        for s in (1, -1):
            tb.cyl('Pole spring', (px - 30, crown + 24, s * 9), (px + 24, crown + 24, s * 9), 4.2)
            tb.cyl('Pole spring rod', (px - 36, crown + 24, s * 9), (px + 30, crown + 24, s * 9), 1.2)
        tb.box('Pole pivot', px + 28, crown + 26, 0, 14, 14, 26)
        ang = ev('pole_ang', 'rad'); Lp = ev('pole_len')
        p0 = (px + 28, crown + 30, 0)
        tip = (p0[0] + Lp * math.cos(ang), p0[1] + Lp * math.sin(ang), 0)
        tb.cyl('Trolley pole', p0, (p0[0] + 0.5 * Lp * math.cos(ang), p0[1] + 0.5 * Lp * math.sin(ang), 0), 3.4, 2.8)
        tb.cyl('Trolley pole', (p0[0] + 0.5 * Lp * math.cos(ang), p0[1] + 0.5 * Lp * math.sin(ang), 0), tip, 2.8, 2.2)
        # harp + trolley wheel
        hx, hy = tip[0] + 4 * math.cos(ang), tip[1] + 4 * math.sin(ang)
        for s in (1, -1):
            tb.box('Trolley harp', hx + 3, hy + 3, s * 2.2, 10, 3, 0.8)
        tb.cyl('Trolley wheel', (hx + 6, hy + 5, -1.6), (hx + 6, hy + 5, 1.6), 5.5)
        tb.cyl('Trolley wheel', (hx + 6, hy + 5, -0.6), (hx + 6, hy + 5, 0.6), 6.4)
        tb.cyl('Retriever rope', tip, (tip[0] + 60, tip[1] - 120, 0), 0.4)
        # pole hook on the B roof
        hk = ev('sec_a_len') + ev('artic_gap') + 120.0
        tb.box('Pole hook', hk, crown + 10, 0, 6, 20, 30)
        tb.box('Pole hook', hk + 4, crown + 21, 0, 10, 3, 30)
    else:
        # diamond pantograph (2019 Raml-line GT6, UTM photo): insulators, base frame, crossed diamond, pan head
        bl, bw = 90.0, 70.0
        for sx in (-1, 1):
            for sz in (-1, 1):
                tb.cyl('Insulator', (px + sx * bl / 2, crown, sz * bw / 2), (px + sx * bl / 2, crown + 14, sz * bw / 2), 6.0)
        tb.box('Pantograph base', px, crown + 17, 0, bl + 10, 6, bw + 10)
        ph = ev('panto_up') if up.itemByName('panto_up') else 190.0
        y0 = crown + 20; yk = y0 + ph * 0.5; yt = y0 + ph
        for sz in (-1, 1):
            z = sz * 32.0
            tb.cyl('Pantograph frame', (px - 40, y0, z), (px, yk, z * 0.9), 1.8)
            tb.cyl('Pantograph frame', (px + 40, y0, z), (px, yk, z * 0.9), 1.8)
            tb.cyl('Pantograph frame', (px, yk, z * 0.9), (px - 38, yt, z * 0.7), 1.4)
            tb.cyl('Pantograph frame', (px, yk, z * 0.9), (px + 38, yt, z * 0.7), 1.4)
        tb.cyl('Pantograph frame', (px, yk, -30), (px, yk, 30), 1.6)
        for sx in (-1, 1):
            tb.cyl('Pantograph frame', (px + sx * 38, yt, -24), (px + sx * 38, yt, 24), 1.2)
            tb.box('Collector strip', px + sx * 12, yt + 4, 0, 5, 3, 110)
        for sz in (-1, 1):
            tb.cyl('Pantograph horn', (px, yt + 4, sz * 55), (px, yt - 6, sz * 78), 1.2)
        tb.cyl('Pantograph spring', (px - 40, y0, 0), (px + 40, y0, 0), 3.0)
    tb.commit('Roof Equipment')
    print('roof bodies', C.bRepBodies.count)
