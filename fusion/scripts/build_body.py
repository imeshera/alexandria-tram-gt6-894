# Body shell of the GT6: two sections (A = cab section, B = rear section) from one parametric cross-section.
#  1. 'Body Section' sketch (YZ plane): skirt, vertical lower side, tumblehome window band, eave fillet, arched roof.
#  2. Extrude A (0 .. sec_a_len) and B (sec_a_len + artic_gap .. car_len) with parameter expressions.
#  3. Plan taper + bowed end face at the outer ends (cut from the XZ plane).
#  4. Roof-end domes in elevation (elliptical corner cut from the XY plane), edge fillets where Fusion allows.
#  5. Shell (shell_t, closed).
# Openings are a separate script (build_openings.py). Idempotent: wipes the Body component and rebuilds.
import math
import adsk.core, adsk.fusion
import os
ROOT = os.path.dirname(os.path.abspath(__file__))

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}; exec(open(g['__file__']).read(), g)
    des = g['design'](); ev = g['ev_fn'](des)
    C = g['comp'](des, 'Body'); g['wipe'](C)
    P = adsk.core.Point3D.create
    VI = adsk.core.ValueInput.createByString
    feats = C.features
    hw, t = ev('half_w'), ev('tumble')
    sb, belt, eave, crown = ev('skirt_bot'), ev('belt_h'), ev('eave_h'), ev('crown_h')
    L, la, gap = ev('car_len'), ev('sec_a_len'), ev('artic_gap')

    def section(sk, x, d=0.0, eave_r=15.0, skirt_r=6.0):
        m = lambda y, z: sk.modelToSketchSpace(P(x, y, z))
        h = hw - d
        A, B = m(sb + d, -h), m(sb + d, h)
        Cc, Dd = m(belt, h), m(eave - d, h - t)
        E, F, G = m(crown - d, 0), m(eave - d, -(h - t)), m(belt, -h)
        Ln, Ar = sk.sketchCurves.sketchLines, sk.sketchCurves.sketchArcs
        l1 = Ln.addByTwoPoints(A, B); l2 = Ln.addByTwoPoints(l1.endSketchPoint, Cc)
        l3 = Ln.addByTwoPoints(l2.endSketchPoint, Dd)
        roof = Ar.addByThreePoints(l3.endSketchPoint, E, F)
        l5 = Ln.addByTwoPoints(roof.endSketchPoint if roof.endSketchPoint.geometry.distanceTo(F) < 1e-3 else roof.startSketchPoint, G)
        l6 = Ln.addByTwoPoints(l5.endSketchPoint, l1.startSketchPoint)
        Ar.addFillet(l6, l6.endSketchPoint.geometry, l1, l1.startSketchPoint.geometry, skirt_r)
        Ar.addFillet(l1, l1.endSketchPoint.geometry, l2, l2.startSketchPoint.geometry, skirt_r)
        Ar.addFillet(l3, l3.endSketchPoint.geometry, roof, l3.endSketchPoint.geometry, eave_r)
        Ar.addFillet(roof, l5.startSketchPoint.geometry, l5, l5.startSketchPoint.geometry, eave_r)

    sk = C.sketches.add(C.yZConstructionPlane); sk.name = 'Body Section'
    section(sk, 0)
    prof = sk.profiles.item(0)
    ext = feats.extrudeFeatures
    NEW, CUT = adsk.fusion.FeatureOperations.NewBodyFeatureOperation, adsk.fusion.FeatureOperations.CutFeatureOperation
    ei = ext.createInput(prof, NEW); ei.setDistanceExtent(False, VI('sec_a_len'))
    fa = ext.add(ei); fa.name = 'Section A'
    A = fa.bodies.item(0); A.name = 'Body A'
    if A.boundingBox.maxPoint.x < 1:                       # grew toward -X: flip
        fa.deleteMe(); ei = ext.createInput(prof, NEW); ei.setDistanceExtent(False, VI('-sec_a_len'))
        fa = ext.add(ei); fa.name = 'Section A'; A = fa.bodies.item(0); A.name = 'Body A'
    sgn = 1 if A.boundingBox.maxPoint.x > 1 else -1
    ei = ext.createInput(prof, NEW)
    ei.startExtent = adsk.fusion.OffsetStartDefinition.create(VI('sec_a_len + artic_gap'))
    ei.setDistanceExtent(False, VI('car_len - sec_a_len - artic_gap'))
    fb = ext.add(ei); fb.name = 'Section B'; B = fb.bodies.item(0); B.name = 'Body B'
    sk.isVisible = False

    # ---- plan taper + bowed end faces (sketch on XZ plane)
    et, tl, bow, er = ev('end_taper'), ev('taper_len'), ev('nose_bow'), ev('end_r')
    def plan_cut(body, front):
        skp = C.sketches.add(C.xZConstructionPlane); skp.name = 'Plan ' + ('front' if front else 'rear')
        X = (lambda x: x) if front else (lambda x: L - x)
        m = lambda x, z: skp.modelToSketchSpace(P(X(x), 0, z))
        Ln, Ar = skp.sketchCurves.sketchLines, skp.sketchCurves.sketchArcs
        xc = tl + 80.0
        # keep outline
        face = Ar.addByThreePoints(m(bow, hw - et), m(0, 0), m(bow, -(hw - et)))
        tp = Ln.addByTwoPoints(m(bow, hw - et), m(tl, hw)); tn = Ln.addByTwoPoints(m(bow, -(hw - et)), m(tl, -hw))
        sp = Ln.addByTwoPoints(m(tl, hw), m(xc, hw)); sn = Ln.addByTwoPoints(m(tl, -hw), m(xc, -hw))
        Ln.addByTwoPoints(m(xc, hw), m(xc, -hw))
        Ar.addFillet(face, m(bow, hw - et), tp, m(bow, hw - et), er)
        Ar.addFillet(face, m(bow, -(hw - et)), tn, m(bow, -(hw - et)), er)
        Ar.addFillet(tp, m(tl, hw), sp, m(tl, hw), ev('taper_blend'))
        Ar.addFillet(tn, m(tl, -hw), sn, m(tl, -hw), ev('taper_blend'))
        # outer frame
        r0, r1 = m(-60, -hw - 60), m(xc, hw + 60)
        Ln.addTwoPointRectangle(r0, r1)
        profs = adsk.core.ObjectCollection.create()
        for i in range(skp.profiles.count):
            pr = skp.profiles.item(i); bb = pr.boundingBox
            mn = skp.sketchToModelSpace(bb.minPoint); mx = skp.sketchToModelSpace(bb.maxPoint)
            if max(abs(mn.z), abs(mx.z)) > hw + 30:
                profs.add(pr)
        ci = ext.createInput(profs, CUT)
        ci.setSymmetricExtent(VI('crown_h * 2 + 1 m'), True)
        ci.participantBodies = [body]
        f = ext.add(ci); f.name = 'Plan taper ' + ('front' if front else 'rear')
        skp.isVisible = False
    plan_cut(A, True); plan_cut(B, False)

    # ---- roof-end domes in elevation (quarter-ellipse corner cut, XY plane)
    rh, rv = ev('roof_end_r'), ev('crown_h') - ev('dest_bot') - ev('dest_h') - 8.0
    def dome_cut(body, front):
        ske = C.sketches.add(C.xYConstructionPlane); ske.name = 'Dome ' + ('front' if front else 'rear')
        X = (lambda x: x) if front else (lambda x: L - x)
        m = lambda x, y: ske.modelToSketchSpace(P(X(x), y, 0))
        cx, cy = rh, crown - rv
        ske.sketchCurves.sketchEllipses.add(m(cx, cy), m(0, cy), m(cx, crown))
        ske.sketchCurves.sketchLines.addTwoPointRectangle(m(-50, cy), m(cx, crown + 50))
        profs = adsk.core.ObjectCollection.create()
        for i in range(ske.profiles.count):
            pr = ske.profiles.item(i)
            c = ske.sketchToModelSpace(pr.areaProperties().centroid)
            u = (abs(c.x - X(cx))) / rh; v = (c.y - cy) / rv
            inside_box = (c.y > cy) and (abs(c.x - X(cx / 2)) < cx / 2 + 50)
            if inside_box and (u * u + v * v > 1.0) and (abs(c.x - X(0)) < abs(X(cx) - X(0))):
                profs.add(pr)
        if profs.count:
            ci = ext.createInput(profs, CUT)
            ci.setSymmetricExtent(VI('body_w'), True)
            ci.participantBodies = [body]
            f = ext.add(ci); f.name = 'Roof dome ' + ('front' if front else 'rear')
        ske.isVisible = False
        return profs.count
    nd = dome_cut(A, True) + dome_cut(B, False)

    # ---- soften the dome / taper intersection edges
    nf = 0
    for body, x0 in ((A, 0.0), (B, L)):
        for r in (12.0,):
            oc = adsk.core.ObjectCollection.create()
            for e in body.edges:
                bb = e.boundingBox
                near = min(abs(bb.minPoint.x - x0), abs(bb.maxPoint.x - x0)) < tl + 10
                if near and bb.maxPoint.y > ev('dest_bot') - 1 and e.length > 5 and not e.geometry.curveType == adsk.core.Curve3DTypes.Line3DCurveType:
                    oc.add(e)
            if oc.count:
                try:
                    fi = feats.filletFeatures.createInput()
                    fi.edgeSetInputs.addConstantRadiusEdgeSet(oc, adsk.core.ValueInput.createByReal(r), True)
                    ff = feats.filletFeatures.add(fi); ff.name = 'Dome blend'; nf += 1
                except Exception as ex:
                    print('fillet skipped:', str(ex)[:80])

    # ---- shell both sections (closed)
    for body in (A, B):
        oc = adsk.core.ObjectCollection.create(); oc.add(body)
        si = feats.shellFeatures.createInput(oc, False)
        si.insideThickness = VI('shell_t')
        sf = feats.shellFeatures.add(si); sf.name = 'Shell ' + body.name
    print('body A bbox', [round(v) for v in (A.boundingBox.minPoint.x, A.boundingBox.maxPoint.x, A.boundingBox.maxPoint.y)],
          '| B bbox', [round(v) for v in (B.boundingBox.minPoint.x, B.boundingBox.maxPoint.x)], '| dome cuts', nd, '| fillets', nf, '| sgn', sgn)
