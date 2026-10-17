# Openings in the GT6 body shell (component Body), all from user parameters:
#  left (+z, no doors): cab window, 5 A windows, 5 B windows, B rear window
#  right (-z): cab window, front door, 3 windows, door 2 (or a window when door2_on = 0), narrow window |
#              narrow window, door 3, 3 windows, rear door
#  front: windscreen, destination glass; rear: rear window; inner ends: gangway openings.
# Also exports opening lists (used by build_glazing.py / build_doors.py through layout()).
import adsk.core, adsk.fusion
import os
ROOT = os.path.dirname(os.path.abspath(__file__))

def layout(ev):
    """Returns dict of side openings in cm: {'L': [(x0,x1,y0,y1,kind)], 'R': [...]}; kind = win|cab|door|narrow"""
    wb, wt = ev('win_bot'), ev('win_top')
    L = [(ev('cabwin_x0'), ev('cabwin_x1'), wb, wt, 'cab')]
    for i in range(5):
        x = ev('winA1_x') + i * ev('win_pitch'); L.append((x, x + ev('win_w'), wb, wt, 'win'))
    for i in range(5):
        x = ev('winB1_x') + i * ev('win_pitch_b'); L.append((x, x + ev('win_w_b'), wb, wt, 'win'))
    L.append((ev('rearwin_x0'), ev('rearwin_x0') + 111.0, wb, wt, 'win'))
    dw, db, dt = ev('door_w'), ev('door_bot'), ev('door_top')
    d1, d2, d3, d4 = ev('door1_x'), ev('door2_x'), ev('door3_x'), ev('door4_x')
    R = [(d1, d1 + dw, db, dt, 'door')]
    if d1 > ev('cabwin_x0') + 60: R.insert(0, (ev('cabwin_x0'), d1 - 12.0, wb, wt, 'cab'))
    R.append((d1 + dw + 12.0, ev('rwinA1_x') - 10.0, wb, wt, 'narrow'))          # narrow window behind door 1
    for i in range(3):
        x = ev('rwinA1_x') + i * ev('rwin_pitch_a'); R.append((x, x + ev('rwin_w_a'), wb, wt, 'win'))
    if round(ev('door2_on', '')) == 1:
        R.append((d2, d2 + dw, db, dt, 'door'))
    else:
        R.append((d2, d2 + dw, wb, wt, 'win'))
    la = ev('sec_a_len'); R.append((d2 + dw + 12.0, la - 14.0, wb, wt, 'narrow'))
    bs = la + ev('artic_gap'); R.append((bs + 14.0, d3 - 14.0, wb, wt, 'narrow'))
    R.append((d3, d3 + dw, db, dt, 'door'))
    for i in range(3):
        x = ev('rwinB1_x') + i * ev('rwin_pitch_b'); R.append((x, x + ev('rwin_w_b'), wb, wt, 'win'))
    R.append((d4, d4 + ev('door4_w'), db, dt, 'door'))
    return {'L': L, 'R': R}

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}; exec(open(g['__file__']).read(), g)
    des = g['design'](); ev = g['ev_fn'](des)
    C = g['comp'](des, 'Body', False)
    A, B = C.bRepBodies.itemByName('Body A'), C.bRepBodies.itemByName('Body B')
    feats = C.features; ext = feats.extrudeFeatures
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    VI, P = adsk.core.ValueInput.createByString, adsk.core.Point3D.create
    for i in range(ext.count - 1, -1, -1):
        if ext.item(i).name.startswith('Opening'):
            ext.item(i).deleteMe()
    for i in range(C.sketches.count - 1, -1, -1):
        if C.sketches.item(i).name.startswith('Openings'):
            C.sketches.item(i).deleteMe()

    def rrect(sk, m, x0, y0, x1, y1, r):
        Ln, Ar = sk.sketchCurves.sketchLines, sk.sketchCurves.sketchArcs
        c = [m(x0, y0), m(x1, y0), m(x1, y1), m(x0, y1)]
        ls = [Ln.addByTwoPoints(c[i], c[(i + 1) % 4]) for i in range(4)]
        if r > 0:
            for i in range(4):
                a, b = ls[i], ls[(i + 1) % 4]
                Ar.addFillet(a, a.endSketchPoint.geometry, b, b.startSketchPoint.geometry, r)

    lay = layout(ev); wr = ev('win_r'); hw = ev('half_w')
    n = 0
    for side, sgn in (('L', 1), ('R', -1)):
        sk = C.sketches.add(C.xYConstructionPlane); sk.name = 'Openings ' + side
        sk.isComputeDeferred = True
        m = lambda x, y: sk.modelToSketchSpace(P(x, y, 0))
        for x0, x1, y0, y1, k in lay[side]:
            rrect(sk, m, x0, y0, x1, y1, 4.0 if k == 'door' else wr); n += 1
        sk.isComputeDeferred = False
        oc = adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count): oc.add(sk.profiles.item(i))
        ci = ext.createInput(oc, CUT)
        ci.setDistanceExtent(False, adsk.core.ValueInput.createByReal(sgn * (hw + 10)))
        ci.participantBodies = [A, B]
        f = ext.add(ci); f.name = 'Opening side ' + side
        sk.isVisible = False

    # front: windscreen + destination glass (YZ plane at x = 0, cut +X)
    sk = C.sketches.add(C.yZConstructionPlane); sk.name = 'Openings front'
    m = lambda z, y: sk.modelToSketchSpace(P(0, y, z))
    w2 = ev('ws_w') / 2
    rrect(sk, m, -w2, ev('ws_bot'), w2, ev('ws_top'), 14.0)
    d2 = ev('dest_w') / 2
    rrect(sk, m, -d2, ev('dest_bot'), d2, ev('dest_bot') + ev('dest_h'), 3.0)
    oc = adsk.core.ObjectCollection.create()
    for i in range(sk.profiles.count): oc.add(sk.profiles.item(i))
    ci = ext.createInput(oc, CUT); ci.setDistanceExtent(False, VI('end_taper + nose_bow + 150 mm'))
    ci.participantBodies = [A]; f = ext.add(ci); f.name = 'Opening front'; sk.isVisible = False

    # rear window (plane at car_len, cut -X)
    pi = C.constructionPlanes.createInput(); pi.setByOffset(C.yZConstructionPlane, VI('car_len'))
    pl = C.constructionPlanes.add(pi); pl.name = 'Openings rear plane'; pl.isLightBulbOn = False
    sk = C.sketches.add(pl); sk.name = 'Openings rear'
    m = lambda z, y: sk.modelToSketchSpace(P(ev('car_len'), y, z))
    rrect(sk, m, -ev('rear_ws_w') / 2, ev('win_bot') - 4, ev('rear_ws_w') / 2, ev('win_top'), 12.0)
    oc = adsk.core.ObjectCollection.create(); oc.add(sk.profiles.item(0))
    ci = ext.createInput(oc, CUT); ci.setDistanceExtent(False, VI('-(end_taper + nose_bow + 150 mm)'))
    ci.participantBodies = [B]; f = ext.add(ci); f.name = 'Opening rear'; sk.isVisible = False

    # gangway openings through the inner end walls
    pi = C.constructionPlanes.createInput(); pi.setByOffset(C.yZConstructionPlane, VI('artic_x'))
    pl = C.constructionPlanes.add(pi); pl.name = 'Openings gangway plane'; pl.isLightBulbOn = False
    sk = C.sketches.add(pl); sk.name = 'Openings gangway'
    ax = ev('artic_x'); m = lambda z, y: sk.modelToSketchSpace(P(ax, y, z))
    rrect(sk, m, -60.0, ev('floor_h'), 60.0, ev('floor_h') + 195.0, 15.0)
    oc = adsk.core.ObjectCollection.create(); oc.add(sk.profiles.item(0))
    ci = ext.createInput(oc, CUT); ci.setSymmetricExtent(VI('artic_gap + 20 mm'), True)
    ci.participantBodies = [A, B]; f = ext.add(ci); f.name = 'Opening gangway'; sk.isVisible = False
    print('side openings', n)
