# Saves viewport images of the heritage design to docs/renders/<date>_<name>.png.
# _context: comma-separated preset names from view.py (iso, isoL, isoR, left, right, front, rear, top, interior) or 'all'.
import adsk.core, adsk.fusion, datetime
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, '..', '..', 'docs', 'renders', '')

def run(_context: str):
    v = {'__file__': os.path.join(ROOT, 'view.py')}; exec(open(v['__file__']).read(), v)
    app = adsk.core.Application.get()
    names = (_context or 'iso').strip()
    if names == 'all':
        names = 'iso,isoL,left,right,front,rear'
    tag = datetime.date.today().isoformat()
    for n in names.split(','):
        v['run'](n)
        app.activeViewport.refresh()
        f = OUT + '%s_%s.png' % (tag, n)
        h = 1000 if n in ('left', 'right', 'iso', 'isoL', 'isoR') else 1400
        app.activeViewport.saveAsImageFile(f, 2400, h)     # the first capture after a camera change can come out blank
        app.activeViewport.saveAsImageFile(f, 2400, h)
        print('saved', f)
