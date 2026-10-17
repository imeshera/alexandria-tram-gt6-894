# Shared helpers for the build scripts (comp, wipe, TB, base, ev_fn, project/folder lookup).
# Every script execs this file, directly or through nothing else, with __file__ set by the loader.
import os
import adsk.core, adsk.fusion, re
ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT = 'Eshera-Personal'                                # Fusion project holding the designs (save guards check it)
FOLDER = 'Alexandria Tram Model 3 - Duewag GT6 894'
DOC = 'Alexandria Heritage Tram 894'

def find_project(app):
    """The Fusion project PROJECT, looked up by name in the active hub (never app.data.activeProject)."""
    for i in range(app.data.activeHub.dataProjects.count):
        p = app.data.activeHub.dataProjects.item(i)
        if p.name == PROJECT:
            return p
    raise RuntimeError('Fusion project not found: ' + PROJECT)

def model_folder(app, create=True):
    """The model's folder (FOLDER) in the project root; created if missing."""
    root = find_project(app).rootFolder
    for i in range(root.dataFolders.count):
        if root.dataFolders.item(i).name == FOLDER:
            return root.dataFolders.item(i)
    if not create:
        return None
    return root.dataFolders.add(FOLDER)

def design():
    app = adsk.core.Application.get()
    d = [x for x in app.documents if x.name == DOC or x.name.startswith(DOC + ' v')]
    if not d:
        raise RuntimeError('document not open: ' + DOC)
    d[0].activate()
    return adsk.fusion.Design.cast(app.activeProduct)

def ev_fn(des):
    um = des.unitsManager
    return lambda e, u='cm': um.evaluateExpression(e, u)

def base(n):
    return re.sub(r'( \(\d+\))+$', '', n)

def comp(des, name, create=True):
    root = des.rootComponent
    for o in root.occurrences:
        if o.component.name == name:
            return o.component
    if not create:
        return None
    o = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    o.component.name = name
    return o.component

def wipe(c, sketches=True):
    f = c.features
    for coll in (f.moveFeatures, f.mirrorFeatures, f.combineFeatures, f.filletFeatures, f.shellFeatures, f.revolveFeatures,
                 f.extrudeFeatures, f.sweepFeatures, f.loftFeatures, f.splitFaceFeatures, f.baseFeatures):
        for i in range(coll.count - 1, -1, -1):
            coll.item(i).deleteMe()
    if sketches:
        for i in range(c.sketches.count - 1, -1, -1):
            c.sketches.item(i).deleteMe()
    for i in range(c.constructionPlanes.count - 1, -1, -1):
        c.constructionPlanes.item(i).deleteMe()
    for i in range(c.bRepBodies.count - 1, -1, -1):
        c.bRepBodies.item(i).deleteMe()

class TB:
    """TemporaryBRep body collector: build many primitives, commit them as named bodies in one base feature."""
    def __init__(self, c):
        self.c = c; self.tbm = adsk.fusion.TemporaryBRepManager.get(); self.parts = []
    P = staticmethod(adsk.core.Point3D.create)
    V = staticmethod(adsk.core.Vector3D.create)
    def box(self, name, cx, cy, cz, lx, ly, lz, ax=(1, 0, 0), ay=(0, 1, 0)):
        d = sum(p * q for p, q in zip(ax, ay)); ay = tuple(q - d * p for p, q in zip(ax, ay))
        n = sum(q * q for q in ay) ** 0.5; ay = tuple(q / n for q in ay)
        ob = adsk.core.OrientedBoundingBox3D.create(self.P(cx, cy, cz), self.V(*ax), self.V(*ay), lx, ly, lz)
        b = self.tbm.createBox(ob); self.parts.append((name, b)); return b
    def cyl(self, name, a, b, r, r2=None):
        t = self.tbm.createCylinderOrCone(self.P(*a), r, self.P(*b), r if r2 is None else r2)
        self.parts.append((name, t)); return t
    def sphere(self, name, c, r):
        t = self.tbm.createSphere(self.P(*c), r); self.parts.append((name, t)); return t
    def commit(self, feat_name, merge_same=False):
        """Adds all parts as bodies inside one base feature. merge_same unions same-named parts (slow for many parts)."""
        if not self.parts:
            return
        items = self.parts
        if merge_same:
            groups = {}
            for n, b in self.parts:
                if n in groups:
                    self.tbm.booleanOperation(groups[n], b, adsk.fusion.BooleanTypes.UnionBooleanType)
                else:
                    groups[n] = b
            items = list(groups.items())
        bf = self.c.features.baseFeatures.add(); bf.startEdit()
        for n, b in items:
            self.c.bRepBodies.add(b, bf).name = n
        bf.finishEdit(); bf.name = feat_name
