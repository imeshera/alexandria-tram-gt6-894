# Livery + materials. The 'livery' user parameter selects the scheme (colours sampled from the dated photos,
# slightly desaturated/greyed for the "slightly weathered" brief):
#   1 Alexandria city, c. 2000-2015: all-over ochre-yellow (window band too), dark-blue waist stripe (+ front V decal),
#     pale roof and apron, blue numerals (Commons 'Tranvia de alejandria-2007' = 895, 856 'Bwyello' 2007)
#   2 APTA 1974-1980s: KS ochre-orange lower, cream upper (the 1974 reference photo of car 894)
#   3 green/white, 2016+ (894 in 2024, 856 in 2025)
#   4 Raml lines 5/6 refurbished, 2019: light blue lower, white upper
#   5 KS Copenhagen 1960-72: yellow lower, cream upper, grey waist strip
# Body shell faces are split at skirt_top / belt_h / belt_h + belt_strip / eave_h; inner faces (normal pointing
# toward the car centre-line) get the interior colour. Re-run after any body rebuild.
import adsk.core, adsk.fusion
import os
ROOT = os.path.dirname(os.path.abspath(__file__))

LIVERIES = {   # lower, upper, waist strip, skirt, roof
    1: ((206, 150, 46), (206, 150, 46), (30, 52, 112), (206, 202, 190), (196, 196, 190)),   # 895 (2007): all-over ochre, blue stripe, pale roof + apron
    2: ((206, 140, 66), (226, 214, 184), (124, 122, 114), (118, 116, 108), (140, 140, 134)),
    3: ((44, 116, 72), (232, 232, 224), (44, 116, 72), (60, 92, 70), (150, 150, 146)),
    4: ((84, 164, 212), (236, 236, 230), (236, 236, 230), (226, 226, 220), (170, 172, 170)),
    5: ((222, 176, 70), (234, 224, 196), (128, 128, 122), (128, 128, 122), (150, 150, 144)),
}

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}; exec(open(g['__file__']).read(), g)
    des = g['design'](); ev = g['ev_fn'](des); base = g['base']
    app = adsk.core.Application.get()
    lib = app.materialLibraries.itemByName('Fusion Appearance Library')
    root = des.rootComponent
    lv = int(round(ev('livery', ''))); lo, upc, strip, skirt, roofc = LIVERIES.get(lv, LIVERIES[1])

    def lib_app(name):
        a = des.appearances.itemByName(name)
        return a if a else des.appearances.addByCopy(lib.appearances.itemByName(name), name)

    def custom(name, src, rgb):
        a = des.appearances.itemByName(name)
        if not a:
            a = des.appearances.addByCopy(lib.appearances.itemByName(src), name)
        for i in range(a.appearanceProperties.count):
            p = a.appearanceProperties.item(i)
            if isinstance(p, adsk.core.ColorProperty) and any(k in p.id.lower() for k in ('color', 'albedo', 'diffuse')):
                v = p.value      # only write a changed colour: editing an in-use appearance spawns duplicates
                if v and (v.red, v.green, v.blue) == tuple(rgb): continue
                try: p.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
                except Exception: pass
        return a
    P = 'Paint - Enamel Glossy (Yellow)'
    A_lo = custom('GT6 lower (weathered)', P, lo); A_up = custom('GT6 upper (weathered)', P, upc)
    A_st = custom('GT6 waist stripe', P, strip); A_sk = custom('GT6 skirt', P, skirt)
    A_rf = custom('GT6 roof (weathered)', 'Paint - Metallic (Dark Grey)', roofc)
    A_in = custom('GT6 interior cream', 'Plastic - Matte (Yellow)', (226, 220, 196))
    A_uf = custom('GT6 underframe', 'Paint - Metallic (Dark Grey)', (48, 48, 46))
    A_wood = lib_app('Oak - Semigloss'); A_dwood = lib_app('Walnut'); A_mah = lib_app('Mahogany')
    A_glass, A_frost = lib_app('Glass (Clear)'), lib_app('Glass - Frosted Light')
    A_rub, A_chr = lib_app('Rubber - Hard'), lib_app('Chrome')
    A_alu, A_stl, A_rough = lib_app('Aluminum - Satin'), lib_app('Steel - Satin'), lib_app('Steel - Rough')
    A_ss = lib_app('Stainless Steel - Satin'); A_red = lib_app('Glass (Red)'); A_amb = lib_app('Phenolic (Amber)')
    A_wht = lib_app('Plastic - Matte (White)'); A_blk = lib_app('Plastic - Matte (Black)'); A_brz = lib_app('Bronze - Patina')
    A_leath = lib_app('Leather - Weathered')

    def comp(name):
        r = [o.component for o in root.occurrences if o.component.name == name]
        return r[0] if r else None

    # ---- body shell split + paint
    import time; t0 = time.time()
    import tempfile; LOG = open(os.path.join(tempfile.gettempdir(), 'appearance894.log'), 'w')   # progress log
    def log(*a):
        LOG.write('%6.1f ' % (time.time() - t0) + ' '.join(str(x) for x in a) + '\n'); LOG.flush()
    B = comp('Body')
    tag = 'Livery split'
    f = B.features
    resplit = (_context or '').strip() == 'resplit' or sum(1 for i in range(f.splitFaceFeatures.count)
                                                            if f.splitFaceFeatures.item(i).name.startswith(tag)) < 4
    for i in range(f.splitFaceFeatures.count - 1, -1, -1) if resplit else []:
        if f.splitFaceFeatures.item(i).name.startswith(tag): f.splitFaceFeatures.item(i).deleteMe()
    for i in range(B.constructionPlanes.count - 1, -1, -1) if resplit else []:
        if B.constructionPlanes.item(i).name.startswith(tag): B.constructionPlanes.item(i).deleteMe()
    for h in ('skirt_top', 'belt_h', 'belt_h + belt_strip', 'eave_h') if resplit else []:
        pi = B.constructionPlanes.createInput()
        pi.setByOffset(B.xZConstructionPlane, adsk.core.ValueInput.createByString(h))
        pl = B.constructionPlanes.add(pi)
        if pl.geometry.origin.y < 0:
            pl.deleteMe(); pi = B.constructionPlanes.createInput()
            pi.setByOffset(B.xZConstructionPlane, adsk.core.ValueInput.createByString('-(' + h + ')'))
            pl = B.constructionPlanes.add(pi)
        pl.name = tag + ' ' + h; pl.isLightBulbOn = False
        y = pl.geometry.origin.y
        faces = adsk.core.ObjectCollection.create()
        for bd in B.bRepBodies:
            for fc in bd.faces:
                bb = fc.boundingBox
                if bb.minPoint.y < y - 0.01 and bb.maxPoint.y > y + 0.01: faces.add(fc)
        if faces.count:
            si = f.splitFaceFeatures.createInput(faces, pl, True)
            sf = f.splitFaceFeatures.add(si); sf.name = tag + ' ' + h
    L = ev('car_len'); sk_t, belt, bs, eave = ev('skirt_top'), ev('belt_h'), ev('belt_strip'), ev('eave_h')
    log('splits done, resplit =', resplit)
    def want(fc):
        p = fc.pointOnFace; ok, n = fc.evaluator.getNormalAtPoint(p)
        c = adsk.core.Vector3D.create(min(max(p.x, 150.0), L - 150.0) - p.x, 170.0 - p.y, -p.z)
        if n.dotProduct(c) > 0:
            return A_in
        y = fc.centroid.y
        return A_sk if y < sk_t else A_lo if y < belt else A_st if y < belt + bs else A_up if y < eave else A_rf
    # Gotcha: setting a face appearance can reorder body.faces, so one pass skips faces. Repeat until stable.
    for bd in B.bRepBodies:
        if bd.appearance is None or bd.appearance.id != A_in.id: bd.appearance = A_in
        for it in range(8):
            nf = 0
            for i in range(bd.faces.count):
                fc = bd.faces.item(i); w = want(fc)
                if fc.appearance is None or fc.appearance.id != w.id:
                    fc.appearance = w; nf += 1
            log('body', bd.name, 'pass', it, 'faces changed', nf)
            if nf == 0: break

    def paint(cname, rule):
        C = comp(cname)
        if not C: return
        for bd in C.bRepBodies:
            a = rule(base(bd.name))
            if a: bd.appearance = a

    paint('Doors', lambda n: {'Door leaf lower': A_lo, 'Door leaf upper': A_up, 'Door glass': A_glass, 'Door seal': A_rub,
                              'Door handle': A_ss, 'Step tread': A_rough, 'Step riser': A_uf}.get(n))
    paint('Glazing', lambda n: {'Glass': A_glass, 'Window rubber': A_rub, 'Window frame': A_alu, 'Wiper': A_blk,
                                'Destination blind': A_wht}.get(n))
    bog = lambda n: A_stl if n in ('Wheel', 'Axle', 'Axlebox cover') else A_rub if n == 'Primary spring' else A_uf
    paint('Motor bogie', bog); paint('Jacobs bogie', bog)
    paint('Front End', lambda n: {'Headlight ring': A_chr, 'Headlight bezel': A_chr, 'Headlamp lens': A_glass,
                                  'Marker lamp housing': A_rf, 'Marker lamp lens': A_glass, 'Route box': A_rf,
                                  'Route box glass': A_glass, 'Route box blind': A_wht, 'Route box hood': A_rf,
                                  'Bumper': A_sk, 'Anticlimber rib': A_sk, 'Tow pocket': A_uf, 'Indicator': A_amb,
                                  'Mirror arm': A_blk, 'Mirror': A_chr}.get(n))
    paint('Rear End', lambda n: {'Tail lamp housing': A_chr, 'Tail lamp lens': A_red, 'Brake lamp lens': A_red,
                                 'Indicator': A_amb, 'Rear route box': A_lo, 'Route box glass': A_wht, 'Bumper': A_sk,
                                 'Number plate': A_lo}.get(n))
    paint('Roof Equipment', lambda n: A_wht if n == 'Insulator' else A_brz if n == 'Trolley wheel' else
          A_blk if n in ('Trolley pole', 'Retriever rope', 'Pole spring') else A_rough if n == 'Collector strip' else A_rf)
    paint('Articulation', lambda n: {'Bellows': A_rub, 'Portal ring': A_up, 'Turntable plate': A_rough,
                                     'Gangway lining': A_in}.get(n))
    paint('Interior', lambda n: {'Floor slat': A_wood, 'Floor base': A_uf, 'Wall lining': A_mah, 'Heater': A_uf,
                                 'Ceiling rib': A_in, 'Light diffuser': A_frost, 'Light housing': A_in,
                                 'Ceiling rail': A_ss, 'Rail bracket': A_ss, 'Grab pole': A_ss, 'Cab partition': A_mah,
                                 'Cab partition glass': A_glass, 'Conductor desk': A_dwood, 'Conductor seat': A_dwood,
                                 'Ticket box': A_alu}.get(n))
    seat = lambda n: A_dwood if n in ('Seat slat', 'Back slat') else A_ss if n == 'Grab bar' else A_uf
    paint('Seat double', seat); paint('Seat single', seat)
    paint('Cab', lambda n: A_chr if n in ('Gauge bezel', 'Controller handle', 'Blind handle') else
          A_wht if n == 'Gauge face' else A_leath if n == 'Driver seat' else A_red if n == 'Fire extinguisher' else
          A_blk if n in ('Instrument panel', 'Controller', 'Controller knob', 'Brake handle', 'Pedal', 'Switch', 'Sun blind')
          else A_uf if n in ('Dash console', 'Driver seat base', 'Cab heater', 'Brake valve') else A_in)
    for i in range(des.appearances.count - 1, -1, -1):      # purge unused duplicates left by earlier runs
        a = des.appearances.item(i)
        if a.name.startswith('GT6') and not a.isUsed:
            try: a.deleteMe()
            except Exception: pass
    log('done'); LOG.close()
    print('livery', lv, '| appearances', des.appearances.count)
