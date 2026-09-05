#!/usr/bin/env python3
"""Classify a GT5 screenshot (1280x720 game window) into a menu state by comparing fixed crops
against reference crops in tools/nav_ref.  Prints the state name (or 'unknown').
Usage: classify.py <shot.png> [--all]   (--all prints the distance to every state)"""
import sys, os
from PIL import Image, ImageChops, ImageStat

REF = os.path.expanduser('~/gt5re/tools/nav_ref')
# state -> (crop box (x, y, w, h), threshold)
GEOM = {
    'psn':      ((500, 325, 280, 22), 0.05),
    'nosignin': ((540, 313, 200, 40), 0.05),
    'p3dialog': ((500, 325, 280, 22), 0.05),
    'p4dialog': ((500, 325, 280, 22), 0.05),
    'install':  ((490, 250, 300, 20), 0.05),
    'language': ((540, 295, 200, 22), 0.05),
    'adjust':   ((285, 335, 700, 30), 0.05),
    'options':  ((270, 111, 170, 16), 0.05),
    'loading':  ((450, 318, 380, 40), 0.05),
    'track':    ((910, 288, 100, 14), 0.05),
    'car':      ((95, 642, 70, 14), 0.07),
    'arcade':   ((180, 62, 300, 20), 0.05),
    'demo':     ((990, 590, 160, 60), 0.08),
    'menubar':  ((730, 600, 50, 50), 0.13),
    'menubar2': ((955, 600, 50, 50), 0.13),
}
ORDER = list(GEOM)


def dist(img, state):
    x, y, w, h = GEOM[state][0]
    ref = Image.open(os.path.join(REF, state + '.png')).convert('RGB')
    crop = img.crop((x, y, x + w, y + h)).convert('RGB')
    if crop.size != ref.size:
        return 9.0
    diff = ImageChops.difference(crop, ref)
    st = ImageStat.Stat(diff)
    return (sum(v for v in st.rms) / 3) / 255.0


def classify(path):
    img = Image.open(path)
    if not (1270 <= img.size[0] <= 1290 and 710 <= img.size[1] <= 730):
        return 'badshot'
    best = None
    for s in ORDER:
        d = dist(img, s)
        if d < GEOM[s][1] and (best is None or d < best[1]):
            best = (s, d)
    return best[0] if best else 'unknown'


if __name__ == '__main__':
    p = sys.argv[1]
    if '--all' in sys.argv:
        img = Image.open(p)
        print(os.path.basename(p), ' '.join(f'{s}={dist(img, s):.3f}' for s in ORDER))
    else:
        print(classify(p))
