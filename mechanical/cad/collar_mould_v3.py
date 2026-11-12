"""
v3 full-collar mould: tracker case (v2 pebble) + band + v3 pod (GRP751538 cast straight into the
silicone, Kapton-wrapped) + PETG clasp insert at the pod face + the extended flex with the breakaway
sensor. The cap is printed (cap_screw.py), not cast.

Closed two-part ring mould split on the band's mid-width plane (ring Z = 0), as in v2.

Casting orientation: the mould STANDS ON EDGE, ring axis horizontal, with the adjustment tail
pointing straight down. The pod is then at the bottom of the ring with its neck side facing up,
so air under the cell rises to the core, where it is vented.
  - Gate G1 (main): parting-plane runner into the pod crown at its lowest point; fill bottom-up with
    a syringe (DS20 NV / DS10 NV, degassed in the cup).
  - Gate G2: parting-plane runner into the tail tip (the tail hangs below the ring, so fill it first).
  - Vents: parting-plane grooves at the high points (ring top, case crown, pod face, tail root) and
    radial Ø1 vents through the core under the cell, into the mould's open centre.
Locating:
  - Case: 0.3 mm land pocket (as v2).
  - Clasp insert: a boss on the end wall filling its 0.4 mm recess.
  - Cell: Ø1.2 core pins touching the Kapton (underside at the cell edges, top, and sides). They
    leave small holes in the skin: dab-fill with the same silicone after demoulding.
  - Flex: Ø0.8–1.0 stilts to its underside (band at 1.6 mm, pod section at 0.35 mm, outside the
    traces), and stepped cores through the adjustment holes in the tail.

python3 collar_mould_v3.py -> v3m_* STEP/STL + assembly STEP.
"""
import math, time
import cadquery as cq
import collar_parts as cp
import pod_v3 as p
import sensor_h as sh
from collar_parts import R0, th, place, W, band_w, band_t, skin, ring_sector, radial_cyl, loft_sections

# ---------------- layout ----------------
x_tail0 = -70.0                       # band leaves the ring along a tangent (antenna copper ends at -62)
tail_end = -110.0                     # silicone tail tip (flex ends at -107.5)
tail_len = x_tail0 - tail_end
adj_x = [-75.2 - 5.0*i for i in range(7)]
T_case = 10.0
core_base_d, core_top_d = 3.0, 1.7    # stepped cores through the Ø1.8 flex holes
floor_t, rim = 4.0, 6.0
pin_d = 1.2                           # cell locating pins
vent_d, gate_d = 1.2, 3.0

# flex stilts: (x, z, height of the flex underside above the neck, diameter)
STILTS = [(x, z, cp.flex_z, 1.0) for x in (-14.0, -32.0, -50.0, -64.0, 30.0, 48.0) for z in (-2.5, 2.5)]
STILTS += [(x, z, cp.flex_z, 1.0) for x in (66.0, 72.0) for z in (-3.4, 3.4)]          # protector zone edges
STILTS += [(78.0, z, cp.flex_z, 1.0) for z in (-5.2, 5.2)]                            # widened pad section
STILTS += [(x, z, sh.tongue_h(x), 0.8) for x in (86.0, 92.5, 97.5, 102.5, 107.5) for z in (-3.6, 3.6)]
STILTS += [(x, z, sh.tongue_h(x) - sh.STIFF_T, 0.8) for x in (111.0, 115.0) for z in (-3.6, 3.6)]

# cell pins along the cell
CELL_PIN_X = (86.0, 113.0)
CORE_VENT_X = (89.5, 95.0, 100.0, 105.0, 110.0, 116.5)


def under_h(x):
    """Height above R0 of the wrapped cell's concave (neck-side) face at band x."""
    lo, hi = -p.phi_lid*1.2, p.phi_half*1.2
    for _ in range(60):
        m = (lo + hi)/2
        if p.bx_of(p.cell_pt(p.X_CELL, m, p.Ri)) < x:
            lo = m
        else:
            hi = m
    return math.hypot(*p.cell_pt(p.X_CELL, m, p.Ri)) - R0


def zcyl(x, h, z0, length, d):
    """Cylinder along ring Z at band x, height h above the neck, from z0 for length (signed)."""
    t = th(x)
    r = R0 + h
    return cq.Solid.makeCylinder(d/2, abs(length), cq.Vector(r*math.cos(t), r*math.sin(t), z0),
                                 cq.Vector(0, 0, 1 if length > 0 else -1))


def build():
    cav = W(cp.ring_sector(R0 - 0.3, R0 + band_t, -band_w/2, band_w/2, x_tail0, 75.0))
    tail_local = (cq.Workplane("XY").box(tail_len, band_w, band_t, centered=False)
                  .translate((-tail_len, -band_w/2, 0)).edges("|Z and <X").fillet(band_w/2 - 0.01))
    tail = place(tail_local, x_tail0, R0)
    cav = cav.union(W(tail))
    # case envelope (as v2)
    import collar_mould as m2
    cxs, cws, chs = m2.envelope_profile([cp.case_tray, cp.case_cover], cp.X_TOP - 11.3 - T_case,
                                        cp.X_TOP + 11.3 + T_case, 1.0, T_case)
    case_env = loft_sections(cxs, cws, [h + 0.3 for h in chs], [cp.cover_fillet + skin]*len(cxs), r_base=R0 - 0.3)
    cav = cav.union(W(case_env), tol=0.01)
    print('ring+tail+case vol', round(cav.val().Volume()))
    # pod envelope (v3: follows the cell and the insert exactly)
    _, pxs, pws, phs = p.envelope()
    rts = p.ENV_RTS
    pod_env = loft_sections(pxs, pws, [h + 0.25 for h in phs], rts, r_base=R0 - 0.25)   # 0.25: avoids coincident faces
    cav = cav.union(W(pod_env))
    assert cav.val().Volume() > 20000, cav.val().Volume()
    core = cq.Workplane("XY").circle(R0).extrude(80).translate((0, 0, -40))
    cav = cav.cut(core)
    # land + pocket under the tracker (as v2)
    L = cp.case_L/2
    zc = lambda xl: math.sqrt(R0**2 - xl**2) - R0
    prof = [(-L - 5, zc(L + 5)), (-L, 0.0), (L, 0.0), (L + 5, zc(L + 5)), (L + 5, -5), (-L - 5, -5)]
    land = place(cq.Workplane("XZ").polyline(prof).close().extrude(15, both=True), cp.X_TOP, R0)
    pocket = place(cp.rrect_prism(cp.case_L + 0.2, cp.case_W + 0.2, cp.case_r + 0.1, -cp.land_pocket, 0.01),
                   cp.X_TOP, R0)
    cav = cav.cut(W(land).cut(W(pocket))).union(W(pocket))
    # boss filling the insert's recess (locates the insert against the end wall)
    cav = cav.cut(W(place(p.recess_local(), p.FACE_BX, R0 + skin)))
    # flex stilts
    for x, z, h, d in STILTS:
        cav = cav.cut(W(radial_cyl(x, R0 - 0.5, h + 0.5, d, z=z)))
    # cell pins: underside at the cell edges, top, and sides
    half_w = p.ww/2
    for x in CELL_PIN_X:
        uh, toph = under_h(x), p.cell_top_h(x)
        for z in (-5.8, 5.8):
            cav = cav.cut(W(radial_cyl(x, R0 - 0.5, uh + 0.5, pin_d, z=z)))
        for z in (-4.0, 4.0):
            cav = cav.cut(W(radial_cyl(x, R0 + toph, skin + 3, pin_d, z=z)))
        hm = (uh + toph)/2
        cav = cav.cut(W(zcyl(x, hm, half_w, skin + 3, pin_d))).cut(W(zcyl(x, hm, -half_w, -(skin + 3), pin_d)))
    # stepped cores through the tail's adjustment holes
    for x in adj_x:
        d = x_tail0 - x
        c = (cq.Workplane("XY").center(-d, 0).circle(core_base_d/2).extrude(cp.flex_z + 0.5).translate((0, 0, -0.5))
             .faces(">Z").workplane().circle(core_top_d/2).extrude(band_t - cp.flex_z + 0.5))
        cav = cav.cut(W(place(c, x_tail0, R0)))
    return cav, case_env, pod_env, tail, (pxs, pws, phs, cxs, cws, chs)


def down_vec():
    t = th(x_tail0)
    return (-math.sin(t), math.cos(t))          # tail direction = down when casting


def mould_halves(cav, ring_h_max):
    bb = cav.val().BoundingBox()
    H = max(abs(bb.zmin), abs(bb.zmax)) + floor_t
    R_out = R0 + ring_h_max + rim
    outline = cq.Workplane("XY").circle(R_out).extrude(2*H).translate((0, 0, -H))
    hw = band_t/2 + rim + 4
    tl = (cq.Workplane("XY").box(tail_len + rim + 6, 2*H, 2*hw, centered=False)
          .translate((-tail_len - rim, -H, -hw)).edges("|Y").fillet(4))
    block = outline.union(W(place(tl.val(), x_tail0, R0 + band_t/2)))
    block = block.cut(cq.Workplane("XY").circle(R0 - 12).extrude(2*H + 2).translate((0, 0, -H - 1)))
    m = block.cut(cav)
    dx, dy = down_vec()

    def runner(x, h_from, d, length=40.0):
        """Parting-plane channel (z = 0) from the cavity surface radially outward."""
        t = th(x)
        r = R0 + h_from - 0.3
        return W(cq.Solid.makeCylinder(d/2, length, cq.Vector(r*math.cos(t), r*math.sin(t), 0),
                                       cq.Vector(math.cos(t), math.sin(t), 0)))
    chans = []
    # G1: pod crown at its lowest point when standing (the band x whose outward normal is most "down")
    xs = [80 + 0.5*i for i in range(int((p.FACE_BX - 1 - 80)/0.5))]
    xg = max(xs, key=lambda x: math.cos(th(x))*dx + math.sin(th(x))*dy)
    chans.append(("G1", runner(xg, p.cell_top_h(xg) + skin, gate_d)))
    # G2: tail tip, along the tail axis
    tip = place(cq.Workplane("XY").center(-tail_len + 0.5, 0).circle(gate_d/2).extrude(1), x_tail0, R0 + band_t/2)
    tb = tip.BoundingBox()
    g2 = cq.Solid.makeCylinder(gate_d/2, 20, cq.Vector((tb.xmin + tb.xmax)/2, (tb.ymin + tb.ymax)/2, 0),
                               cq.Vector(dx, dy, 0))
    chans.append(("G2", W(g2)))
    # vents at the high points when standing
    up_x = max([x/2 for x in range(-140, 40)], key=lambda x: -(math.cos(th(x))*dx + math.sin(th(x))*dy))
    chans.append(("V ring top", runner(up_x, band_t, vent_d)))
    for x in (cp.X_TOP - 11.3, cp.X_TOP, cp.X_TOP + 11.3):
        chans.append((f"V case {x:.0f}", runner(x, 5.0, vent_d)))
    chans.append(("V pod face", runner(p.FACE_BX - 0.8, phs_face(), vent_d)))
    chans.append(("V tail root", runner(x_tail0 + 1.0, band_t, vent_d)))
    chans.append(("V pod taper", runner(68.0, 3.0, vent_d)))
    # radial core vents under the cell (each half), into the open centre
    for x in CORE_VENT_X:
        for z in (-4.0, 4.0):
            t = th(x)
            r = R0 + 0.01
            chans.append((f"C {x}", W(cq.Solid.makeCylinder(0.5, 13.5, cq.Vector(r*math.cos(t), r*math.sin(t), z),
                                                          cq.Vector(-math.cos(t), -math.sin(t), 0)))))
    for _, c in chans:
        m = m.cut(c)
    top = m.intersect(cq.Workplane("XY").box(400, 400, H, centered=False).translate((-200, -200, 0)))
    bot = m.intersect(cq.Workplane("XY").box(400, 400, H, centered=False).translate((-200, -200, -H)))
    for i, ang in enumerate([20, 140, 260]):
        a = math.radians(ang); r = R_out - rim/2
        dw = cq.Workplane("XY").center(r*math.cos(a), r*math.sin(a)).circle(1.55).extrude(6).translate((0, 0, -6))
        top = top.cut(dw.translate((0, 0, 6))); bot = bot.cut(dw)
    for ang in [60, 100, 180, 220, 300, 340]:
        a = math.radians(ang); r = R_out - rim/2
        bolt = cq.Workplane("XY").center(r*math.cos(a), r*math.sin(a)).circle(1.7).extrude(2*H + 2).translate((0, 0, -H - 1))
        top = top.cut(bolt); bot = bot.cut(bolt)
    return top, bot, R_out, H, xg, up_x


_PHS = {}


def phs_face():
    return _PHS["face"]


if __name__ == "__main__":
    t0 = time.time()
    cav, case_env, pod_env, tail, prof = build()
    pxs, pws, phs, cxs, cws, chs = prof
    _PHS["face"] = phs[-1]
    ring_h = max(max(phs), max(chs)) + 0.5
    print("cavity", round(time.time() - t0, 1), "s; valid", cav.val().isValid())
    top, bot, R_out, H, xg, up_x = mould_halves(cav, ring_h)
    print(f"mould R_out {R_out:.1f}, half {H:.1f}; G1 at band x {xg:.1f}; ring top at x {up_x:.1f}")
    # the cast: cavity minus parts that are in it
    cell = W(p.cell_solid())
    ins = W(place(p.insert_local(), p.FACE_BX, R0 + skin))
    case_fill = place(cp.rrect_prism(cp.case_L, cp.case_W, cp.case_r, 0.0, cp.case_top)
                      .faces(">Z").edges().fillet(cp.cover_fillet), cp.X_TOP, R0 - cp.land_pocket)
    cast = cav.cut(W(case_fill)).cut(cell).cut(ins)
    # clearance tail <-> pod envelope (mould wall between them)
    dist = tail.distance(pod_env)
    print("tail to pod envelope clearance", round(dist, 2), "mm")
    out = {"mould_top": top, "mould_bottom": bot, "band_cast": cast}
    for k, v in out.items():
        cq.exporters.export(v, f"v3m_{k}.step")
        cq.exporters.export(v, f"v3m_{k}.stl", tolerance=0.02, angularTolerance=0.1)
        print(k, "valid", v.val().isValid(), "solids", len(v.solids().vals()), "vol", round(v.val().Volume(), 1))
    bbt = top.val().BoundingBox()
    print("mould half bbox", round(bbt.xlen, 1), "x", round(bbt.ylen, 1), "x", round(bbt.zlen, 1))
    asm = cq.Assembly()
    asm.add(bot, name="mould_bottom", color=cq.Color(0.55, 0.7, 0.9, 0.5))
    asm.add(cast, name="band_cast", color=cq.Color(0.2, 0.2, 0.22))
    asm.add(cell, name="cell", color=cq.Color(0.95, 0.62, 0.2))
    asm.add(ins, name="clasp_insert", color=cq.Color(0.3, 0.5, 0.95))
    asm.add(W(cp.case_tray), name="case_tray", color=cq.Color(0.3, 0.3, 0.32))
    asm.add(W(cp.case_cover), name="case_cover", color=cq.Color(0.4, 0.4, 0.42))
    asm.save("v3m_collar_assembly.step")
    print("silicone cm3", round(cast.val().Volume()/1000, 2), "total", round(time.time() - t0, 1), "s")
