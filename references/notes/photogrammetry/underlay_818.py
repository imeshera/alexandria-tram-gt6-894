# underlay_818.py <src> <out>: rectified left-side elevation of KS 818 (Commons 41468165) for a Fusion canvas.
# Same 1-D projective model as rect1d.py: X(x) = K (x - x0) / (xv - x); vertical m/px = c / (xv - x);
# all car-parallel lines (incl. the rail line) converge to the VP (xv, 423). Output: 100 px per metre,
# X from -1.0 m to +20.5 m, Y from -0.5 m to +4.5 m (model origin = front end, top of rail).
import sys, numpy as np
from PIL import Image
src = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)
xv, x0, x1, L = 9500.0, 50.0, 1119.0, 19.095
K = L * (xv - x1) / (x1 - x0)
s120 = K * (xv - x0) / (xv - 120) ** 2; c = s120 * (xv - 120)          # m/px vertical at x: c / (xv - x)
yh = 423.0; yr0 = 615.0                                                 # horizon y, rail y at x = 120
ppm = 100; Xs = np.arange(-1.0, 20.5, 1 / ppm); Ys = np.arange(4.5, -0.5, -1 / ppm)
X, Y = np.meshgrid(Xs, Ys)
xs = (X * xv + K * x0) / (K + X)
yrail = yr0 + (yh - yr0) * (xs - 120) / (xv - 120)
ys = yrail - Y / (c / (xv - xs))
h, w, _ = src.shape
xi = np.clip(np.round(xs).astype(int), 0, w - 1); yi = np.clip(np.round(ys).astype(int), 0, h - 1)
out = src[yi, xi]; out[(xs < 0) | (xs > w - 1) | (ys < 0) | (ys > h - 1)] = 255
Image.fromarray(out.astype(np.uint8)).save(sys.argv[2], quality=92)
print('saved', sys.argv[2], out.shape[1], 'x', out.shape[0], '| origin px (u0, v0 from top) =', 100, int(4.5 * ppm), '| mm/px', 1000 / ppm)
