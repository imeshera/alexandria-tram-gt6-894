# Guarded save of the 894 document: _context = version message. Saves only if the document lives in project
# Eshera-Personal (PROJECT in common.py).
import os
import adsk.core
ROOT = os.path.dirname(os.path.abspath(__file__))

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}; exec(open(g['__file__']).read(), g)
    app = adsk.core.Application.get(); DOC = g['DOC']
    d = [x for x in app.documents if x.name == DOC or x.name.startswith(DOC + ' v')]
    if not d: raise RuntimeError('document not open: ' + DOC)
    doc = d[0]
    if doc.dataFile is None or doc.dataFile.parentProject.name != g['PROJECT']:
        raise RuntimeError('save guard: parent project is not ' + g['PROJECT'])
    doc.activate()
    print('saved' if doc.save(_context or 'checkpoint') else 'save returned False')
