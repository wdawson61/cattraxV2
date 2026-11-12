"""
Cat collar v2 — sleek, fully overmoulded. Printed inner parts, placed in the worn (ring) shape.

Ring frame: Z = ring axis (across the band). Neck surface = cylinder of radius R0 (226 mm
circumference, the 72 mm saline-bottle phantom). Band coordinate x (mm along the neck surface)
follows handoff_shared_interface.md: 0 = tracker board left edge, negative = antenna/tail side,
x increases clockwise.

Parts (exported in the ring frame; reorient for printing in the slicer):
  case_tray, case_cover   pebble tracker case, two glued halves; flat bare neck face for the dock
  pod_shell, pod_lid      602030 cell pod, curved along the neck; option-B cone socket at the
                          clasp end; magnet goes in through the cell cavity before the cell
  cap_a, cap_b            fit-and-trim cap, two glued halves (split at the band's mid-width):
                          nose cone + magnet, slot for the band tail, holes for two Ø2 mm pins
"""
import math
import cadquery as cq

# ---------------- ring ----------------
R0 = 226.0 / (2*math.pi)          # neck radius, 35.97 mm
band_w, band_t = 12.0, 3.6
flex_z = 1.6                       # flex above the neck surface
skin = 0.8                         # silicone over the printed parts
X_TOP = 10.0                       # board centre sits at the top of the ring


def th(x):
    """band x -> ring angle (rad)"""
    return math.pi/2 + (X_TOP - x)/R0


def frame(x, r):
    t = th(x)
    return cq.Plane(origin=(r*math.cos(t), r*math.sin(t), 0.0),
                    xDir=(math.sin(t), -math.cos(t), 0.0), normal=(math.cos(t), math.sin(t), 0.0))


def place(wp, x, r):
    """Local frame at band position x, origin at radius r: local X along +x (clockwise tangent),
    local Z radially out, local Y = -ring Z."""
    s = wp.val() if isinstance(wp, cq.Workplane) else wp
    return s.moved(cq.Location(frame(x, r)))


def W(s):
    return s if isinstance(s, cq.Workplane) else cq.Workplane("XY").add(s)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0))


def rrect_prism(L, Wd, r, z0, z1, cx=0.0):
    return (cq.Workplane("XY").workplane(offset=z0).center(cx, 0).rect(L, Wd).extrude(z1-z0)
            .edges("|Z").fillet(r))


def cyl_x(d, x0, x1, y=0.0, z=0.0):
    return cq.Workplane("YZ", origin=(x0, y, z)).circle(d/2).extrude(x1-x0)


def cone_x(r0, r1, x0, x1, y=0.0, z=0.0):
    """Truncated cone along +X from x0 (radius r0) to x1 (radius r1)."""
    return W(cq.Solid.makeCone(r0, r1, x1-x0, cq.Vector(x0, y, z), cq.Vector(1, 0, 0)))


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t*t*(3 - 2*t)


# ---------------- sections lofted along the ring ----------------
def rr_section(w, h, rt, rb=1.0, n=8):
    """Rounded rectangle, flat on the neck side. (u, v): u across the band, v radially from base."""
    rb = min(rb, h/3, w/4)
    rt = max(0.3, min(rt, w/2 - 0.01, h - rb - 0.01))
    pts = []
    def arc(cx, cy, r, a0, a1):
        for i in range(n+1):
            a = a0 + (a1 - a0)*i/n
            pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    arc(w/2 - rt, h - rt, rt, 0.0, math.pi/2)
    arc(-w/2 + rt, h - rt, rt, math.pi/2, math.pi)
    arc(-w/2 + rb, rb, rb, math.pi, 1.5*math.pi)
    arc(w/2 - rb, rb, rb, 1.5*math.pi, 2*math.pi)
    return pts


def section_wire(x, w, h, rt, r_base=R0):
    t = th(x)
    pts = [cq.Vector((r_base + v)*math.cos(t), (r_base + v)*math.sin(t), u) for (u, v) in rr_section(w, h, rt)]
    return cq.Wire.makePolygon(pts, close=True)


def loft_sections(xs, ws, hs, rts, r_base=R0):
    wires = [section_wire(x, w, h, rt, r_base) for x, w, h, rt in zip(xs, ws, hs, rts)]
    return cq.Solid.makeLoft(wires, False)


def ring_sector(r0, r1, z0, z1, x0, x1):
    """Annular sector between band positions x0 < x1."""
    a0, a1 = th(x1), th(x0)
    s = (cq.Workplane("XZ").polyline([(r0, z0), (r1, z0), (r1, z1), (r0, z1)]).close()
         .revolve(math.degrees(a1 - a0), (0, 0, 0), (0, 1, 0))).val()
    if s.BoundingBox().ymax < 1e-6:
        s = s.mirror("XZ")
    return s.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), math.degrees(a0))


def radial_cyl(x, r_from, length, d, z=0.0):
    t = th(x)
    return cq.Solid.makeCylinder(d/2, length, cq.Vector(r_from*math.cos(t), r_from*math.sin(t), z),
                                 cq.Vector(math.cos(t), math.sin(t), 0))


# =====================================================================================
# Tracker case (local frame: origin on the case's neck face at the board centre)
# =====================================================================================
board_l, board_w, board_t = 20.0, 17.0, 1.54
target_h = 1.5                     # dock target height (parameter until the Mill-Max part is picked)
under_parts_h = 1.0                # tallest underside part (side strips)
top_parts_h = 1.2                  # tallest top-side part (MIA-M10Q 1.0 mm, chip antennas 0.6–1.1 mm)
case_clr, tray_wall, cover_wall = 0.3, 1.0, 0.8
case_L = board_l + 2*(case_clr + tray_wall)       # 22.6 along the band
case_W = board_w + 2*(case_clr + tray_wall)       # 19.6 across
case_r = 3.0
board_z0 = target_h                               # board bottom; target faces finish at the neck face
board_z1 = board_z0 + board_t
cover_in = top_parts_h + 0.3
case_top = board_z1 + cover_in + cover_wall       # ≈ 5.44
cover_fillet = 1.8
side_floor = board_z0 - under_parts_h             # 0.5
mid_floor = board_z0 - 0.15                       # 1.35: the flex lies on it under the board
mid_strip = 8.0
# target windows: two per side strip, asymmetric (placeholder positions; match the KiCad layout)
targets = [(-6.5, 6.25), (5.5, 6.25), (-5.5, -6.25), (6.5, -6.25)]
target_hole_d = 3.4
dimples = [(-9.6, 0.0), (9.6, 0.0)]               # dock locating dimples (in the centre strip)
dimple_d, dimple_depth = 1.6, 0.8
land_pocket = 0.3                                 # case sits 0.3 mm into a pocket in the mould land


def make_case():
    inL, inW = case_L - 2*tray_wall, case_W - 2*tray_wall
    tray = rrect_prism(case_L, case_W, case_r, 0.0, board_z1)
    tray = tray.cut(rrect_prism(inL, inW, case_r - tray_wall, side_floor, board_z1 + 1))
    tray = tray.union(box(-inL/2, inL/2, -mid_strip/2, mid_strip/2, 0.0, mid_floor))
    for (x, y) in targets:
        tray = tray.cut(cq.Workplane("XY").center(x, y).circle(target_hole_d/2).extrude(board_z0))
    for (x, y) in dimples:
        tray = tray.cut(cq.Workplane("XY").center(x, y).circle(dimple_d/2).extrude(dimple_depth))
    tray = tray.cut(box(-case_L/2 - 1, case_L/2 + 1, -4.3, 4.3, mid_floor - 0.05, mid_floor + 0.45))  # flex
    cover = rrect_prism(case_L, case_W, case_r, board_z1, case_top)
    cover = cover.faces(">Z").edges().fillet(cover_fillet)
    cover = cover.cut(rrect_prism(case_L - 2*cover_wall, case_W - 2*cover_wall, case_r - cover_wall,
                                  board_z1 - 0.01, board_z1 + cover_in))
    return tray, cover


def case_nubs():
    """0.8 mm skin standoffs: two on top, two on each side (local frame)."""
    n = None
    pts = [((x, 0.0, case_top - 0.3), (0, 0, 1)) for x in (-5.0, 5.0)]
    pts += [((x, s*(case_W/2 - 0.3), 2.6), (0, s, 0)) for x in (-5.0, 5.0) for s in (-1, 1)]
    for (p, d) in pts:
        c = W(cq.Solid.makeCylinder(0.6, skin + 0.3, cq.Vector(*p), cq.Vector(*d)))
        n = c if n is None else n.union(c)
    return n


# =====================================================================================
# Pod: Grepow GRP751538 curved cell (440 mAh), held on its concave face, walls hugging the cell.
# Shell lofted along the ring from the lid end (x = 78) to the radial clasp face.
# =====================================================================================
cell_R_in = 52.39                                 # concave (inner) face radius, ±1 (datasheet)
cell_t = 7.50                                     # max swollen thickness (6.94 at shipment)
cell_w = 15.0                                     # max width
cell_arc = 38.10                                  # max arc length along the inner face
lead_allow = 2.5                                  # tabs + leads at the lid end
pod_clr_t, pod_clr_w, pod_clr_l = 0.3, 0.25, 0.3
pod_wall = 0.8
Rn = R0 + skin                                    # pod neck face radius (skinned underneath)
in_w = cell_w + 2*pod_clr_w
pod_W = in_w + 2*pod_wall                         # 17.1
pod_rt = 2.2
X_LID = 78.0                                      # band side end of the pod (radial face)
lid_t = 1.2
cav_Ri = cell_R_in - pod_clr_t                    # cavity arcs, concentric with the cell
cav_Ro = cell_R_in + cell_t + pod_clr_t
top_R = cav_Ro + pod_wall                         # pod top follows the cell's convex face
zc = pod_wall - cav_Ri                            # cell centre in the pod frame (below the neck)
phi_clasp = (cell_arc/2 + pod_clr_l)/cell_R_in    # cavity half-angles about the cell centre
phi_lid = (cell_arc/2 + pod_clr_l + lead_allow)/cell_R_in
# option-B clasp: magnet pair Ø8 × 4.8 mm N52 (K&J 5/16 × 3/16 class); cone wall 35° from the face
mag_d, mag_l = 8.0, 4.8
cone_phi = 35.0
cone_depth = 0.6
cone_floor_r = mag_d/2 + 0.3
cone_mouth_r = cone_floor_r + cone_depth/math.tan(math.radians(cone_phi))   # ≈ 5.16
mag_skin = 0.3
clasp_h = 5.5                                     # clasp axis height above the pod neck face
cap_gap = 0.2
clasp_need = clasp_h + cone_mouth_r + 0.6         # section height needed round the cone mouth


def _bx(pt):
    """band x of a ring-plane point"""
    return X_TOP + (math.pi/2 - math.atan2(pt[1], pt[0]))*R0


def _cell_pt(xpod, phi, r):
    """Ring-plane point on the cell arc: angle phi (+ toward +x) about the cell centre, radius r."""
    t0 = th(xpod)
    c = (Rn + zc)
    pcx, pcy = c*math.cos(t0), c*math.sin(t0)
    t = t0 - phi
    return (pcx + r*math.cos(t), pcy + r*math.sin(t))


def _solve_xpod():
    x = X_LID + 25.0
    for _ in range(40):
        lid_end = min(_bx(_cell_pt(x, -phi_lid, r)) for r in (cav_Ri, cav_Ro))
        x += (X_LID + lid_t + 0.1) - lid_end
    return x


X_POD = _solve_xpod()                             # band x of the cell centre line
_clasp_end = max(_bx(_cell_pt(X_POD, phi_clasp, r)) for r in (cav_Ri, cav_Ro))
FACE_BX = _clasp_end + (cone_depth + mag_skin + mag_l) - 1.0   # magnet pocket overlaps the cavity end


def _pod_height_at(x):
    """Radial height above Rn of the cell's top arc (+ wall) at band x."""
    t0, t = th(X_POD), th(x)
    c = Rn + zc
    pcx, pcy = c*math.cos(t0), c*math.sin(t0)
    ux, uy = math.cos(t), math.sin(t)
    b = ux*pcx + uy*pcy
    s = b + math.sqrt(max(b*b - (pcx*pcx + pcy*pcy) + top_R**2, 0.0))
    need = s - Rn
    x1 = FACE_BX - (cone_depth + mag_skin + mag_l + 1.0)   # full clasp height from here on
    k = smooth((x - (x1 - 5.0))/5.0)                        # blend up over 5 mm, no step
    return max(need, need + (clasp_need - need)*k) if clasp_need > need else need


def pod_profile(step=1.0):
    xs = []
    x = X_LID
    while x < FACE_BX - 0.5:
        xs.append(x)
        x += step
    xs.append(FACE_BX)
    hs = [_pod_height_at(x) for x in xs]          # follows the cell: no crown fill
    return xs, [pod_W]*len(xs), hs, [pod_rt]*len(xs)


def socket_local():
    """Cone socket in the clasp-face frame (face at local x = 0, pod on the -x side)."""
    return cone_x(cone_floor_r, cone_mouth_r, -cone_depth, 0.001, z=clasp_h)


def _cell_cavity():
    """Annular sector concentric with the cell, open through the lid end (pod frame)."""
    ring = (cq.Workplane("XZ").center(0, zc).circle(cav_Ro).circle(cav_Ri).extrude(in_w/2, both=True))
    def wedge(a0, a1, R=200):
        pts = [(0, zc)]
        for i in range(17):
            a = a0 + (a1 - a0)*i/16
            pts.append((R*math.sin(a), zc + R*math.cos(a)))
        return cq.Workplane("XZ").polyline(pts).close().extrude(in_w, both=True)
    return ring.intersect(wedge(-phi_lid - 0.3, phi_clasp))


def make_pod():
    xs, ws, hs, rts = pod_profile()
    outer = W(loft_sections(xs, ws, hs, rts, r_base=Rn))
    cav = place(_cell_cavity(), X_POD, Rn)
    shell = outer.cut(W(cav))
    mp = cyl_x(mag_d + 0.1, -(cone_depth + mag_skin + mag_l + 3.0), -(cone_depth + mag_skin), z=clasp_h)
    shell = shell.cut(W(place(mp, FACE_BX, Rn)))
    shell = shell.cut(W(place(socket_local(), FACE_BX, Rn)))
    lid = outer.intersect(W(cav)).intersect(W(ring_sector(R0, R0 + 30, -20, 20, X_LID - 1, X_LID + lid_t)))
    # lead hole through the lid, low down at one side, toward the flex BAT pads
    t = th(X_LID + lid_t/2)
    p = cq.Vector((Rn + 2.0)*math.cos(t), (Rn + 2.0)*math.sin(t), 4.0)
    d = cq.Vector(-math.sin(t), math.cos(t), 0)
    lid = lid.cut(W(cq.Solid.makeCylinder(1.25, 6, p - d*3, d)))
    return shell, lid


def pod_nubs():
    n = None
    for x in (X_POD - 10, X_POD + 10):
        h = _pod_height_at(x)
        for c in (radial_cyl(x, R0, skin + 0.3, 1.2), radial_cyl(x, Rn + h - 0.3, skin + 0.3, 1.2)):
            n = W(c) if n is None else n.union(W(c))
    return n


# =====================================================================================
# Cap (fit and trim): continues the pod's outline, nose cone into the socket, magnet,
# a slot for the band tail, two radial Ø2 mm pin holes. Split at mid-width into two halves.
# =====================================================================================
cap_len = 21.0
cap_floor, slot_t, slot_w, cap_top_wall = 0.8, band_t + 0.3, band_w + 0.4, 1.0
cap_end_h = cap_floor + slot_t + cap_top_wall      # 5.7
cap_end_w = slot_w + 2.0                          # 14.4
pin_d = 2.0
pin_pitch = 5.0


def make_cap(face_w, face_h, face_rt):
    """face_*: the silicone envelope section at the pod face, so the cap continues its outline."""
    x0 = FACE_BX + cap_gap*R0/(R0 + clasp_h)
    xs = [x0 + i*1.0 for i in range(int(cap_len) + 1)]
    ws, hs, rts = [], [], []
    for x in xs:
        s = smooth((x - x0)/cap_len)
        ws.append(face_w + (cap_end_w - face_w)*s)
        hs.append(face_h + (cap_end_h - face_h)*s)
        rts.append(face_rt + (2.0 - face_rt)*s)
    cap = W(loft_sections(xs, ws, hs, rts))
    nose = cone_x(cone_floor_r - 0.1, cone_mouth_r - 0.1, -cone_depth + cap_gap, cap_gap + 0.5, z=clasp_h)
    cap = cap.union(W(place(nose, FACE_BX, Rn)))
    mp = cyl_x(mag_d + 0.1, cap_gap + mag_skin, cap_gap + mag_skin + mag_l + 0.1, z=clasp_h)
    cap = cap.cut(W(place(mp, FACE_BX, Rn)))
    x_end = xs[-1]
    cap = cap.cut(W(ring_sector(R0 + cap_floor, R0 + cap_floor + slot_t, -slot_w/2, slot_w/2,
                                x_end - 12.5, x_end + 2)))
    pins = [x_end - 3.7, x_end - 3.7 - pin_pitch]
    for x in pins:
        cap = cap.cut(W(radial_cyl(x, R0 + 0.3, 12, pin_d + 0.1)))
    a = cap.intersect(box(-200, 200, -200, 200, 0, 50))
    b = cap.intersect(box(-200, 200, -200, 200, -50, 0))
    return a, b, pins, x_end


# =====================================================================================
tray_l, cover_l = make_case()
case_tray = place(tray_l, X_TOP, R0 - land_pocket)
case_cover = place(cover_l, X_TOP, R0 - land_pocket)
case_nub_set = place(case_nubs(), X_TOP, R0 - land_pocket)
pod_shell_w, pod_lid_w = make_pod()
pod_shell = pod_shell_w.val()
pod_lid = pod_lid_w.val()

if __name__ == "__main__":
    xs, ws, hs, rts = pod_profile(2.0)
    print("pod band x", round(X_LID, 1), "->", round(FACE_BX, 1), "cell centre", round(X_POD, 1))
    print("pod heights", [round(h, 1) for h in hs])
    print("case", case_L, case_W, round(case_top, 2), "mouth Ø", round(2*cone_mouth_r, 2))
    for n, s in (("tray", case_tray), ("cover", case_cover), ("pod", pod_shell), ("lid", pod_lid)):
        print(n, s.isValid(), len(s.Solids()), round(s.Volume(), 1))


# printable versions with the 0.8 mm skin standoffs (nubs) added
def _with_nubs():
    nl = case_nubs()
    tray_n = tray_l.union(nl.intersect(box(-50, 50, -50, 50, -5, board_z1)))
    cover_n = cover_l.union(nl.intersect(box(-50, 50, -50, 50, board_z1, 20)))
    return (place(tray_n, X_TOP, R0 - land_pocket), place(cover_n, X_TOP, R0 - land_pocket),
            pod_shell_w.union(pod_nubs()).val())


case_tray_print, case_cover_print, pod_shell_print = _with_nubs()
