# grid.py <image> <out> x0 y0 x1 y1 [scale] [step]: crop, upscale and overlay a labelled pixel grid (original px coords)
import sys
from PIL import Image, ImageDraw
a = sys.argv
im = Image.open(a[1]).convert('RGB')
x0, y0, x1, y1 = map(int, a[3:7]); s = float(a[7]) if len(a) > 7 else 2.0; st = int(a[8]) if len(a) > 8 else 20
c = im.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * s), int((y1 - y0) * s)), Image.LANCZOS)
d = ImageDraw.Draw(c)
for x in range((x0 // st + 1) * st, x1, st):
    X = (x - x0) * s; big = x % (st * 5) == 0
    d.line([(X, 0), (X, c.height)], fill=(255, 0, 255) if big else (0, 255, 255), width=1)
    if big: d.text((X + 2, 2), str(x), fill=(255, 0, 255))
for y in range((y0 // st + 1) * st, y1, st):
    Y = (y - y0) * s; big = y % (st * 5) == 0
    d.line([(0, Y), (c.width, Y)], fill=(255, 0, 255) if big else (0, 255, 255), width=1)
    if big: d.text((2, Y + 2), str(y), fill=(255, 0, 255))
c.save(a[2])
