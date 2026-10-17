# rect1d.py - 1-D projective rectification along a car side (reproduces heritage-dossier.md §3).
# Image x -> world X along the car: X(x) = K (x - x0) / (xv - x), with xv the vanishing point of the car's
# horizontal lines (from window-top / skirt lines), x0 the front end, and K fixed by the sourced length
# (19.095 m). Pixel picks were read off grid overlays made with grid.py (orig px coordinates).
import numpy as np

def fit_vp(line_a, line_b):
    """lines as ((x1,y1),(x2,y2)); returns x of intersection"""
    (a1, b1), (a2, b2) = line_a; (c1, d1), (c2, d2) = line_b
    ma = (b2 - b1) / (a2 - a1); mc = (d2 - d1) / (c2 - c1)
    return (d1 - b1 + ma * a1 - mc * c1) / (ma - mc)

def run_818():
    # KS 818, Sundby depot 1969 (Commons 41468165), left side, front at image left.
    # window-height ratio rear/front = 52/59 -> xv ~ 8160; skirt/top-line convergence -> 11169; mean used: 9500
    xv, x0, x1, L = 9500.0, 50.0, 1119.0, 19.095
    K = L * (xv - x1) / (x1 - x0); X = lambda x: K * (x - x0) / (xv - x)
    picks = {'cab window': (81, 163), 'A1': (181, 265), 'A2': (270, 350), 'A3': (355, 435), 'A4': (440, 516),
             'A5': (521, 596), 'A end': (619, 619), 'B start': (652, 652), 'B1': (682, 755), 'B2': (760, 830),
             'B3': (834, 902), 'B4': (907, 973), 'B5': (977, 1043), 'B6 (rear)': (1057, 1113),
             'front bogie frame': (200, 361), 'Jacobs bogie frame': (561, 711), 'rear bogie frame': (896, 1025),
             'pole base': (395, 395)}
    for k, (a, b) in picks.items():
        print(f'{k:20s} {X(a):6.2f} - {X(b):6.2f} m')
    s = K * (xv - x0) / (xv - 120) ** 2      # m/px along the car at the front window
    for name, y in (('roof crown', 421), ('gutter', 452), ('window top', 462), ('window bottom', 521),
                    ('waist (yellow top)', 529), ('skirt colour line', 575), ('skirt bottom', 596)):
        print(f'{name:20s} {(615 - y) * s:5.2f} m above rail (rail at y=615)')

def run_821():
    # APTA 821, Al Wardiyan 1974 (Commons 30257301), right/door side, front at image right; 3-point fit
    P = [(740, 0.0), (432, 9.90), (215, 19.095)]
    A = [[x, 1, -X * x] for x, X in P]; a, b, c = np.linalg.solve(A, [X for _, X in P])
    f = lambda x: (a * x + b) / (c * x + 1)
    for k, (p, q) in {'front door': (657, 593), 'door A2': (487, 455), 'door B1': (397, 355), 'rear door': (240, 217)}.items():
        print(f'{k:12s} {f(p):6.2f} - {f(q):6.2f} m')

if __name__ == '__main__':
    run_818(); print(); run_821()
