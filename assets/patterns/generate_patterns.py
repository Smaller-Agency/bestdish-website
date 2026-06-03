"""Generate BestDish damask pattern tiles — the ornamental motif from the
packaging sleeves — as seamless, recolourable SVG tiles.

The motif is drawn once and placed so the tile repeats cleanly:
  - a central mirrored ogee/leaf spray
  - quarter-flowers in the corners (four corners form one bloom when tiled)
  - small filler dots on the mid-edges (mirror across edges)

Each colourway draws the ink in one brand colour at a chosen opacity over a
transparent ground, so the same tile layers over Cherry, Gravy, or Cream.
"""
import os

TILE = 240  # tile size in px
H = TILE / 2

# Brand palette (food names)
COLORWAYS = {
    "blueberry":  "#A4C4FC",
    "shrimp":     "#F4BCC4",
    "honeydew":   "#D0CCA0",
    "pistachios": "#BCAC0C",
    "orange":     "#E43C00",
    "cream":      "#FCFCF4",
    "cherry":     "#500008",
}


def leaf(cx, cy, w, h, rot=0, flip=1):
    """A single pointed leaf/petal as a quadratic-bezier path, centred at the
    base point (cx, cy), growing 'up' by h, width w. flip mirrors horizontally."""
    w *= flip
    # base -> right belly -> tip -> left belly -> base
    return (f"M {cx} {cy} "
            f"Q {cx + w} {cy - h*0.35} {cx} {cy - h} "
            f"Q {cx - w} {cy - h*0.35} {cx} {cy} Z")


def spray(cx, cy):
    """A symmetric leaf spray (the heart of the damask) rooted at (cx,cy)."""
    p = []
    # central stem leaf
    p.append(leaf(cx, cy, 26, 92))
    # paired side leaves, fanning out
    for (dx, dy, w, h, fl) in [
        (0, -14, 40, 60, 1), (0, -14, 40, 60, -1),
        (0, -40, 30, 46, 1), (0, -40, 30, 46, -1),
        (0, 2,   30, 40, 1), (0, 2,   30, 40, -1),
    ]:
        # approximate rotation by offsetting the tip via flip + belly width
        p.append(leaf(cx, cy + dy, w, h, flip=fl))
    return " ".join(p)


def bloom(cx, cy, r):
    """A small radial flower built from 6 petals + a centre dot."""
    import math
    parts = []
    for i in range(6):
        a = i * math.pi / 3
        px = cx + math.cos(a) * r * 0.55
        py = cy + math.sin(a) * r * 0.55
        parts.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{r*0.42:.1f}" ry="{r*0.22:.1f}" '
                     f'transform="rotate({math.degrees(a):.1f} {px:.1f} {py:.1f})"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r*0.28:.1f}"/>')
    return "".join(parts)


def tile_svg(ink, opacity):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{TILE}" height="{TILE}" viewBox="0 0 {TILE} {TILE}">
  <g fill="{ink}" fill-opacity="{opacity}" stroke="none">
    <!-- central ogee spray -->
    <path d="{spray(H, H + 30)}"/>
    <!-- mirrored top spray (drop) -->
    <g transform="rotate(180 {H} {H})"><path d="{spray(H, H + 30)}"/></g>
    <!-- corner quarter-blooms: full bloom forms across 4 tiled corners -->
    {bloom(0, 0, 34)}
    {bloom(TILE, 0, 34)}
    {bloom(0, TILE, 34)}
    {bloom(TILE, TILE, 34)}
    <!-- mid-edge filler dots (tile across edges) -->
    <circle cx="{H}" cy="0" r="5"/><circle cx="{H}" cy="{TILE}" r="5"/>
    <circle cx="0" cy="{H}" r="5"/><circle cx="{TILE}" cy="{H}" r="5"/>
  </g>
</svg>'''


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    made = []
    for name, ink in COLORWAYS.items():
        # texture weight: tuned to read as tone-on-tone damask over dark grounds
        op = 0.22 if name in ("cream",) else (0.30 if name in ("orange", "cherry") else 0.32)
        svg = tile_svg(ink, op)
        path = os.path.join(here, f"damask-{name}.svg")
        with open(path, "w") as fh:
            fh.write(svg)
        made.append(os.path.basename(path))
    print("Wrote:", ", ".join(made))


if __name__ == "__main__":
    main()
