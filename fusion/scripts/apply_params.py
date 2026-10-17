# Creates / updates all user parameters from params.py (expression + comment). Safe to re-run.
import adsk.core, adsk.fusion
import os
ROOT = os.path.dirname(os.path.abspath(__file__))

def run(_context: str):
    g = {'__file__': os.path.join(ROOT, 'common.py')}
    exec(open(g['__file__']).read(), g)
    exec(open(os.path.join(ROOT, 'params.py')).read(), g)
    des = g['design']()
    up = des.userParameters
    n_new = n_upd = 0
    for name, expr, unit, comment in g['PARAMS']:
        p = up.itemByName(name)
        if p is None:
            up.add(name, adsk.core.ValueInput.createByString(expr), unit, comment); n_new += 1
        else:
            if p.expression != expr:
                p.expression = expr; n_upd += 1
            p.comment = comment
    print('params new', n_new, 'updated', n_upd, 'total', up.count)
