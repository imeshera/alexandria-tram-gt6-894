# Glazing + window rubbers (component Glazing): side windows follow the tumblehome (tilted panes),
# top hopper transom on saloon windows, two-pane windscreen + mullion following the bowed front,
# two-pane rear window, destination glass + white blind, route-number box glass.
import math
import adsk.core, adsk.fusion
import os
ROOT = os.path.dirname(os.path.abspath(__file__))

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}; exec(open(g['__file__']).read(), g)
    o = {'__file__': os.path.join(ROOT, 'build_openings.py')}; exec(open(o['__file__']).read(), o)
    des = g['design'](); ev = g['ev_fn'](des)
    C = g['comp'](des, 'Glazing'); g['wipe'](C)
    tb = g['TB'](C)
    hw, t, belt, eave = ev('half_w'), ev('tumble'), ev('belt_h'), ev('eave_h')
    st = ev('shell_t')
    ang = math.atan2(t, eave - belt)
    def wall_z(y):        # outer skin |z| at height y (window band)
        return hw - t * max(0.0, (y - belt)) / (eave - belt)
    lay = o['layout'](ev)
    hop = ev('hopper_h')
    for side, sgn in (('L', 1), ('R', -1)):
        ay = (0, math.cos(ang), -sgn * math.sin(ang))
        for x0, x1, y0, y1, k in lay[side]:
            if k == 'door':
                continue
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            zc = sgn * (wall_z(cy) - st - 0.6)
            tb.box('Glass', cx, cy, zc, x1 - x0 + 3.0, y1 - y0 + 3.0, 0.6, ay=ay)
            # rubber / frame ring just inside the opening edge, flush with the skin
            zr = sgn * (wall_z(cy) - 0.9)
            w, h, fr = x1 - x0, y1 - y0, 2.2
            tb.box('Window rubber', cx, y1 - fr / 2, sgn * (wall_z(y1) - 0.9), w, fr, 1.8, ay=ay)
            tb.box('Window rubber', cx, y0 + fr / 2, sgn * (wall_z(y0) - 0.9), w, fr, 1.8, ay=ay)
            tb.box('Window rubber', x0 + fr / 2, cy, zr, fr, h, 1.8, ay=ay)
            tb.box('Window rubber', x1 - fr / 2, cy, zr, fr, h, 1.8, ay=ay)
            if k == 'win':      # hopper transom + sliding vent pane
                yt = y1 - hop
                tb.box('Window frame', cx, yt, sgn * (wall_z(yt) - 1.6), w, 3.0, 1.8, ay=ay)
                tb.box('Window frame', cx, y1 - hop / 2, sgn * (wall_z(y1 - hop / 2) - 3.4), w * 0.52, hop - 2, 1.4, ay=ay)
                tb.box('Glass', x0 + w * 0.26 + 2, y1 - hop / 2, sgn * (wall_z(y1 - hop / 2) - 3.5), w * 0.48, hop - 6, 0.5, ay=ay)
            if k == 'cab':      # sliding cab-window split
                tb.box('Window frame', cx, cy, sgn * (wall_z(cy) - 1.6), 2.5, h, 1.8, ay=ay)

    # windscreen: two flat panes following the bowed face, centre mullion
    bow, et = ev('nose_bow'), ev('end_taper')
    zf = hw - et
    face_x = lambda z: bow * (z / zf) ** 2
    w2 = ev('ws_w') / 2; yb, yt = ev('ws_bot'), ev('ws_top'); cy = (yb + yt) / 2
    for s in (1, -1):
        za, zb = 0.0, s * (w2 + 1.5)
        xa, xb = face_x(za) + st + 0.6, face_x(zb) + st + 0.6
        L = math.hypot(xb - xa, zb - za); ax = ((xb - xa) / L, 0, (zb - za) / L)
        tb.box('Glass', (xa + xb) / 2, cy, (za + zb) / 2, L, yt - yb + 3, 0.8, ax=ax, ay=(0, 1, 0))
    tb.box('Window frame', face_x(0) + 0.8, cy, 0, 2.0, yt - yb, 6.0)
    # wiper
    tb.box('Wiper', face_x(0.3 * w2) - 0.4, yb + 22, 0.3 * w2, 0.6, 45, 1.2, ay=(0, math.cos(0.5), math.sin(0.5)))
    # destination glass + blind
    db, dh, dw = ev('dest_bot'), ev('dest_h'), ev('dest_w')
    tb.box('Glass', face_x(0) + st + 0.5, db + dh / 2, 0, 0.6, dh + 2, dw + 2)
    tb.box('Destination blind', face_x(0) + st + 4.0, db + dh / 2, 0, 0.3, dh, dw)
    # rear window: two panes + mullion
    Lc = ev('car_len'); rw2 = ev('rear_ws_w') / 2; rb, rt = ev('win_bot') - 4, ev('win_top'); rc = (rb + rt) / 2
    for s in (1, -1):
        za, zb = 0.0, s * (rw2 + 1.5)
        xa, xb = Lc - face_x(za) - st - 0.6, Lc - face_x(zb) - st - 0.6
        L = math.hypot(xb - xa, zb - za); ax = ((xb - xa) / L, 0, (zb - za) / L)
        tb.box('Glass', (xa + xb) / 2, rc, (za + zb) / 2, L, rt - rb + 3, 0.8, ax=ax, ay=(0, 1, 0))
    tb.box('Window frame', Lc - face_x(0) - 0.8, rc, 0, 2.0, rt - rb, 6.0)
    tb.commit('Glazing')
    print('glazing bodies', C.bRepBodies.count)
