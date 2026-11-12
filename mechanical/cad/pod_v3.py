"""
Pod v3 concept (no mould): the GRP751538 curved cell cast straight into the silicone band,
wrapped in Kapton, plus a small printed clasp insert holding a K&J B842-N52 block magnet
(12.7 x 6.35 x 3.18 mm, magnetised through the 3.18), and a matching fit-and-trim cap.

Same ring frame as collar_parts.py. Run: python3 pod_v3.py -> v3_*.step/.stl
"""
import math
import cadquery as cq
from collar_parts import (R0, th, place, box, W, loft_sections, ring_sector, radial_cyl, smooth,
                          band_w, band_t, skin)

# ---------------- cell (GRP751538) ----------------
R_in, cell_t, cell_w, cell_arc = 52.39, 6.94, 15.0, 38.10     # nominal thickness: silicone takes swelling
kap = 0.05                                                      # Kapton wrap
lead_allow = 2.5
Ri, Ro = R_in - kap, R_in + cell_t + kap
ww = cell_w + 2*kap
zc = -Ri                                   # cell centre in the cell frame (origin at R0 + skin, mid-cell)
r_base = R0 + skin

# ---------------- clasp: block magnet in a printed insert ----------------
mag = (3.18, 12.7, 6.35)                   # along band, across band, radial
pocket = (3.25, 12.8, 6.45)
mag_skin = 0.3
recess_depth, bevel = 0.4, 30.0            # shallow bevelled recess in the pod face
floor_y, floor_z = pocket[1] + 0.3, pocket[2] + 0.3          # recess floor size
grow = recess_depth/math.tan(math.radians(bevel))
open_y, open_z = floor_y + 2*grow, floor_z + 2*grow           # recess opening at the face
ins_y, ins_z = open_y + 1.0, open_z + 1.0                     # insert face (0.5 rim)
ins_len = 0.8 + pocket[0] + mag_skin + recess_depth           # back wall + magnet + skin + recess
ins_h0 = skin                                                  # insert sits 0.8 above the neck
clasp_h = ins_h0 + ins_z/2                                     # clasp axis height above R0
cap_gap = 0.2
cap_len = 20.0


def bx_of(pt):
    return 10.0 + (math.pi/2 - math.atan2(pt[1], pt[0]))*R0


def cell_pt(xc, phi, r):
    t0 = th(xc)
    c = r_base + zc
    t = t0 - phi
    return (c*math.cos(t0) + r*math.cos(t), c*math.sin(t0) + r*math.sin(t))


phi_half = (cell_arc/2)/R_in
phi_lid = phi_half + lead_allow/R_in
X_CELL = 80.0
for _ in range(40):                        # cell lid end (+ leads) starts at band x 80
    X_CELL += 80.0 - min(bx_of(cell_pt(X_CELL, -phi_lid, r)) for r in (Ri, Ro))
cell_end = max(bx_of(cell_pt(X_CELL, phi_half, r)) for r in (Ri, Ro))
FACE_BX = cell_end + 0.6 + ins_len


def cell_solid():
    def wedge(a0, a1, R=200):
        pts = [(0, zc)] + [(R*math.sin(a0 + (a1 - a0)*i/16), zc + R*math.cos(a0 + (a1 - a0)*i/16))
                           for i in range(17)]
        return cq.Workplane("XZ").polyline(pts).close().extrude(ww, both=True)
    ring = cq.Workplane("XZ").center(0, zc).circle(Ro).circle(Ri).extrude(ww/2, both=True)
    return place(ring.intersect(wedge(-phi_half, phi_half)), X_CELL, r_base)


def cell_top_h(x):
    """Radial height above R0 of the wrapped cell's outer face at band x (None if outside)."""
    t0, t = th(X_CELL), th(x)
    c = r_base + zc
    pcx, pcy = c*math.cos(t0), c*math.sin(t0)
    ux, uy = math.cos(t), math.sin(t)
    b = ux*pcx + uy*pcy
    s = b + math.sqrt(max(b*b - (pcx*pcx + pcy*pcy) + Ro**2, 0.0))
    # inside the cell's angular span?
    a = (th(X_CELL) - math.atan2(s*uy - pcy, s*ux - pcx))
    a = (a + math.pi) % (2*math.pi) - math.pi
    if abs(a) > phi_half + 0.002:
        return None
    return s - R0


def insert_local():
    """Clasp insert in the face frame (face at local x = 0, pod side at -x)."""
    zc0 = clasp_h - skin                   # axis height in the face frame (origin at R0 + skin)
    body = (cq.Workplane("YZ", origin=(-ins_len, 0, zc0)).rect(ins_y, ins_z).extrude(ins_len)
            .edges("|X").fillet(1.5))
    # magnet pocket, opening at the back (magnet pressed in from behind, then potted over)
    body = body.cut(cq.Workplane("YZ", origin=(-ins_len - 0.01, 0, zc0)).rect(pocket[1], pocket[2])
                    .extrude(0.8 + pocket[0] + 0.01))
    # bevelled recess in the face
    rec = (cq.Workplane("YZ", origin=(-recess_depth, 0, zc0)).rect(floor_y, floor_z)
           .workplane(offset=recess_depth + 0.01).rect(open_y, open_z).loft())
    body = body.cut(rec)
    # silicone key: a slot across the back so the cast silicone locks the insert in
    body = body.cut(cq.Workplane("YZ", origin=(-ins_len - 0.01, 0, zc0)).rect(ins_y + 1, 1.2).extrude(0.5))
    return body


def recess_local():
    zc0 = clasp_h - skin
    return (cq.Workplane("YZ", origin=(-recess_depth, 0, zc0)).rect(floor_y, floor_z)
            .workplane(offset=recess_depth).rect(open_y, open_z).loft())


def envelope():
    """Silicone outline: wrapped cell + 0.8 mm skin, insert + skin, smooth tapers into the band."""
    step = 1.0
    xs = []
    x = 80.0 - 14.0
    while x < FACE_BX - 0.25:
        xs.append(x)
        x += step
    xs.append(FACE_BX)
    raw = []
    for x in xs:
        h = cell_top_h(x)
        hw = None
        if h is not None:
            hw = (ww + 2*skin, h + skin)
        if x >= FACE_BX - ins_len - 0.6:
            hi = (ins_y + 2*skin, ins_h0 + ins_z + skin)
            hw = hi if hw is None else (max(hw[0], hi[0]), max(hw[1], hi[1]))
        raw.append(hw)
    # dilate by two samples (2 mm) so the cell's end corners keep their skin
    raw = [max([r for r in raw[max(0, i - 2):i + 3] if r is not None], default=None,
               key=lambda r: r[1]) if any(r is not None for r in raw[max(0, i - 2):i + 3]) else None
           for i in range(len(raw))]
    ws, hs = [], []
    for xi, ri in zip(xs, raw):
        if ri is not None:                 # follow the part exactly: no fill between the ends
            ws.append(ri[0]); hs.append(ri[1]); continue
        w, h = band_w, band_t
        for xj, r in zip(xs, raw):
            if r is None:
                continue
            d = 0.0 if xi > xj else abs(xi - xj)
            k = 1 - smooth(d/14.0)
            w = max(w, band_w + (r[0] - band_w)*k)
            h = max(h, band_t + (r[1] - band_t)*k)
        ws.append(w)
        hs.append(h)
    # corner radius: over the cell / insert (sharp-cornered parts) keep the corner skin >= 0.5 mm:
    # skin_corner = r - sqrt(2)*(r - skin): r = 1.2 gives 0.63; tapers stay round
    rts = [1.2 if r is not None else min(3.0, h/2 - 0.2) for r, h in zip(raw, hs)]
    global ENV_RTS
    ENV_RTS = rts
    return W(loft_sections(xs, ws, hs, rts)), xs, ws, hs


def cap(face_w, face_h):
    x0 = FACE_BX + cap_gap*R0/(R0 + clasp_h)
    xs = [x0 + i for i in range(int(cap_len) + 1)]
    ws = [face_w + (14.4 - face_w)*smooth((x - x0)/cap_len) for x in xs]
    hs = [face_h + (5.7 - face_h)*smooth((x - x0)/cap_len) for x in xs]
    rts = [min(3.0, h/2 - 0.2) for h in hs]
    c = W(loft_sections(xs, ws, hs, rts))
    zc0 = clasp_h - skin
    boss = (cq.Workplane("YZ", origin=(cap_gap - recess_depth, 0, zc0)).rect(floor_y - 0.2, floor_z - 0.2)
            .workplane(offset=recess_depth + 0.3).rect(open_y - 0.2 + 0.6*0, open_z - 0.2).loft())
    c = c.union(W(place(boss, FACE_BX, R0 + skin)))
    mp = (cq.Workplane("YZ", origin=(cap_gap - recess_depth + mag_skin, 0, zc0))
          .rect(pocket[1], pocket[2]).extrude(pocket[0]))
    c = c.cut(W(place(mp, FACE_BX, R0 + skin)))
    x_end = xs[-1]
    c = c.cut(W(ring_sector(R0 + 0.8, R0 + 0.8 + band_t + 0.3, -(band_w + 0.4)/2, (band_w + 0.4)/2,
                            x_end - 11.0, x_end + 2)))
    for x in (x_end - 3.7, x_end - 8.7):
        c = c.cut(W(radial_cyl(x, R0 + 0.3, 12, 2.1)))
    a = c.intersect(box(-200, 200, -200, 200, 0, 50))
    b = c.intersect(box(-200, 200, -200, 200, -50, 0))
    return a, b


if __name__ == "__main__":
    cell = cell_solid()
    ins = place(insert_local(), FACE_BX, R0 + skin)
    env, xs, ws, hs = envelope()
    rec = place(recess_local(), FACE_BX, R0 + skin)
    sil = env.cut(W(cell)).cut(W(ins)).cut(W(rec))
    band = ring_sector(R0, R0 + band_t, -band_w/2, band_w/2, 40.0, 70.0)
    cap_a, cap_b = cap(ws[-1], hs[-1])
    out = {"cell": W(cell), "clasp_insert": W(ins), "pod_silicone": sil, "band_stub": W(band),
           "cap_a": cap_a, "cap_b": cap_b}
    for k, v in out.items():
        cq.exporters.export(v, f"v3_{k}.step")
        cq.exporters.export(v, f"v3_{k}.stl", tolerance=0.02, angularTolerance=0.1)
        print(k, v.val().isValid(), len(v.solids().vals()), round(v.val().Volume(), 1))
    mid = min(range(len(xs)), key=lambda i: abs(xs[i] - X_CELL))
    print(f"cell centre x {X_CELL:.1f}, face x {FACE_BX:.1f}, pod length (taper start to face) "
          f"{FACE_BX - xs[0]:.1f}; width {max(ws):.1f}; height over neck: middle {hs[mid]:.1f}, "
          f"max {max(hs):.1f}, at face {hs[-1]:.1f}")
    print(f"insert {ins_len:.2f} x {ins_y:.1f} x {ins_z:.1f}; recess opening {open_y:.1f} x {open_z:.1f}")
