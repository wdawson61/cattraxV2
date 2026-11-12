"""
Closed two-part ring mould for the fully overmoulded collar (cast in the worn shape).

The silicone outer shape (the "envelope") is lofted from radial sections taken through the printed
parts, plus a 0.8 mm skin, blended into the 12 x 3.6 band with smooth tapers. The mould is split on
the band's mid-width plane (ring Z = 0) into a bottom and a top half.

Bare faces: the tracker's neck face sits in a 0.3 mm pocket in a flat land on the core; the pod's
cone face sits against the mould end wall with a cone boss filling the socket. The cap is printed,
not cast. The adjustment tail is cast straight along a tangent so it clears the pod.

python3 collar_mould.py -> STEP/STL for both mould halves, the cast band, and an assembly STEP.
"""
import math
import cadquery as cq
import collar_parts as cp
from collar_parts import R0, th, place, box, band_w, band_t, skin, smooth

# ---------------- band layout ----------------
x_tail0 = -70.0                     # band leaves the ring along a tangent here (antenna copper ends at -62)
tail_len = 52.5                     # straight tail, to x = -122.5
adj_x = [-74.5 - 5.0*i for i in range(7)]
T_case, T_pod = 10.0, 18.0          # taper lengths into the band
stilt_x = [-14.0, -32.0, -50.0, -64.0, 30.0, 48.0]
stilt_z = [-2.5, 2.5]
stilt_d = 1.0
core_base_d, core_top_d = 3.0, 2.0  # stepped adjustment-hole cores
floor_t = 4.0                       # mould wall beyond the widest part of the cavity
rim = 6.0

pod_face_bx = cp.FACE_BX            # band x of the clasp-face centre


def extents(shape, x):
    """Radial min/max and half-width (ring Z) of a part in the radial plane at band x."""
    t = th(x)
    s = shape.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -math.degrees(t))
    slab = cq.Solid.makeBox(200, 0.1, 100, cq.Vector(0, -0.05, -50))
    try:
        i = s.intersect(slab)
        if i.Volume() < 1e-6:
            return None
        bb = i.BoundingBox()
        return bb.xmin, bb.xmax, max(abs(bb.zmin), abs(bb.zmax))
    except Exception:
        return None


def envelope_profile(parts, x0, x1, step, taper, clamp_hi=None, crown=True, taper_hi=True):
    """Sample part extents (+ skin), give the lump a constant crown, and blend into the band with
    smooth tapers. Returns xs, ws, hs."""
    raw = []
    xs = []
    x = x0
    while x <= x1 + 1e-6:
        xs.append(x)
        e = None
        for p in parts:
            ee = extents(p, x)
            if ee:
                e = ee if e is None else (min(e[0], ee[0]), max(e[1], ee[1]), max(e[2], ee[2]))
        if e:
            raw.append((2*(e[2] + skin), e[1] - R0 + skin))
        else:
            raw.append(None)
        x += step
    if crown:
        hm = max(r[1] for r in raw if r)
        wm = max(r[0] for r in raw if r)
        raw = [(wm, hm) if r else None for r in raw]
    ws, hs = [], []
    for i, xi in enumerate(xs):
        w, h = band_w, band_t
        for j, xj in enumerate(xs):
            if raw[j] is None:
                continue
            d = abs(xi - xj)
            if not taper_hi and xi > xj:
                d = 0.0
            k = 1 - smooth(d / taper)
            w = max(w, band_w + (raw[j][0] - band_w)*k)
            h = max(h, band_t + (raw[j][1] - band_t)*k)
        ws.append(w)
        hs.append(h)
    return xs, ws, hs


def build():
    case_parts = [cp.case_tray, cp.case_cover]
    pod_parts = [cp.pod_shell, cp.pod_lid]
    # --- envelopes
    cxs, cws, chs = envelope_profile(case_parts, cp.X_TOP - 11.3 - T_case, cp.X_TOP + 11.3 + T_case, 1.0, T_case)
    case_rt = cp.cover_fillet + skin
    # lofts start 0.3 mm inside the neck surface (robust booleans), trimmed by the core below
    case_env = cp.loft_sections(cxs, cws, [h + 0.3 for h in chs], [case_rt]*len(cxs), r_base=R0 - 0.3)
    pxs = [cp.X_LID - T_pod + i for i in range(int(cp.FACE_BX - (cp.X_LID - T_pod)) + 1)] + [cp.FACE_BX]
    _, pws, phs = envelope_profile(pod_parts, pxs[0], pxs[-2], 1.0, T_pod, taper_hi=False, crown=False)
    pws.append(pws[-1]); phs.append(phs[-1])
    pod_rt_env = cp.pod_rt + skin
    pod_env = cp.loft_sections(pxs, pws, [h + 0.3 for h in phs], [pod_rt_env]*len(pxs), r_base=R0 - 0.3)
    face_w, face_h = pws[-1], phs[-1]
    global RING_H_MAX
    RING_H_MAX = max(max(phs), max(chs)) + 0.5
    # --- band: ring from the tail tangent point to under the pod, plus the straight tail
    band = cp.ring_sector(R0 - 0.3, R0 + band_t, -band_w/2, band_w/2, x_tail0, 80.0)
    tail_local = (cq.Workplane("XY").box(tail_len, band_w, band_t, centered=False)
                  .translate((-tail_len, -band_w/2, 0)).edges("|Z and <X").fillet(band_w/2 - 0.01))
    tail = place(tail_local, x_tail0, R0)
    cavity = cq.Workplane("XY").add(band).union(cq.Workplane("XY").add(tail))
    cavity = cavity.union(cq.Workplane("XY").add(case_env), tol=0.01).union(cq.Workplane("XY").add(pod_env), tol=0.01)
    core = cq.Workplane("XY").circle(R0).extrude(80).translate((0, 0, -40))
    cavity = cavity.cut(core)
    # --- core features (removed from the cavity = left as mould material)
    # land under the tracker: flat at the case neck-face plane + 0.3, ramping down to the neck circle
    L = cp.case_L/2
    zc = lambda xl: math.sqrt(R0**2 - xl**2) - R0
    prof = [(-L - 5, zc(L + 5)), (-L, 0.0), (L, 0.0), (L + 5, zc(L + 5)), (L + 5, -5), (-L - 5, -5)]
    land = (cq.Workplane("XZ").polyline(prof).close().extrude(15, both=True))
    land = place(land, cp.X_TOP, R0)
    pocket = place(cp.rrect_prism(cp.case_L + 0.2, cp.case_W + 0.2, cp.case_r + 0.1, -cp.land_pocket, 0.01),
                   cp.X_TOP, R0)
    land = cq.Workplane("XY").add(land).cut(cq.Workplane("XY").add(pocket))
    cavity = cavity.cut(land).union(cq.Workplane("XY").add(pocket))
    # cone boss filling the pod socket
    cavity = cavity.cut(cq.Workplane("XY").add(place(cp.socket_local(), cp.FACE_BX, cp.Rn)))
    # stilts (radial pins from the neck surface up to the flex)
    for x in stilt_x:
        t = th(x)
        for z in stilt_z:
            p = cq.Vector((R0 - 0.5)*math.cos(t), (R0 - 0.5)*math.sin(t), z)
            d = cq.Vector(math.cos(t), math.sin(t), 0)
            cavity = cavity.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(stilt_d/2, cp.flex_z + 0.5, p, d)))
    # stepped adjustment-hole cores in the straight tail
    for x in adj_x:
        d = x_tail0 - x
        c = (cq.Workplane("XY").center(-d, 0).circle(core_base_d/2).extrude(cp.flex_z + 0.5).translate((0, 0, -0.5))
             .faces(">Z").workplane().circle(core_top_d/2).extrude(band_t - cp.flex_z + 0.5))
        cavity = cavity.cut(cq.Workplane("XY").add(place(c, x_tail0, R0)))
    return cavity, case_env, pod_env, tail, face_w, face_h, pod_rt_env, (cxs, cws, chs, pxs, pws, phs)


RING_H_MAX = 14.5                   # updated from the envelopes in build()


def mould_halves(cavity):
    bb = cavity.val().BoundingBox()
    zmax = max(abs(bb.zmin), abs(bb.zmax))
    H = zmax + floor_t
    R_out = R0 + RING_H_MAX + rim     # ring part only; the straight tail gets its own outline
    outline = cq.Workplane("XY").circle(R_out).extrude(2*H).translate((0, 0, -H))
    # cover the straight tail
    hw = band_t/2 + rim + 4
    tl = (cq.Workplane("XY").box(tail_len + rim + 6, 2*H, 2*hw, centered=False)
          .translate((-tail_len - rim, -H, -hw)).edges("|Y").fillet(4))
    tl = cq.Workplane("XY").add(place(tl, x_tail0, R0 + band_t/2))
    block = outline.union(tl)
    block = block.cut(cq.Workplane("XY").circle(R0 - 12).extrude(2*H + 2).translate((0, 0, -H - 1)))
    m = block.cut(cavity)
    # sprue + vents (vertical holes through the top half into the top of the cavity)
    holes = []
    def hole_at(x, r_off, d):
        t = th(x)
        r = R0 + r_off
        return cq.Workplane("XY").center(r*math.cos(t), r*math.sin(t)).circle(d/2).extrude(H + 1)
    holes.append(hole_at(-40.0, band_t/2, 5.0))                     # sprue (funnel it, or inject)
    for x, ro in ((cp.X_TOP, 3.0), (cp.X_POD, 6.0), (cp.FACE_BX - 3, 6.0), (cp.X_LID - 2, 4.0), (-8.0, 2.0),
                  (28.0, 2.0), (66.0, 2.5), (x_tail0 + 1, band_t/2)):
        holes.append(hole_at(x, ro, 1.6))
    # tail-end vent
    tv = place(cq.Workplane("XY").center(-tail_len + 3, 0).circle(0.8).extrude(1), x_tail0, R0 + band_t/2)
    bbv = tv.BoundingBox()
    holes.append(cq.Workplane("XY").center((bbv.xmin + bbv.xmax)/2, (bbv.ymin + bbv.ymax)/2)
                 .circle(0.8).extrude(H + 1))
    top = m.intersect(cq.Workplane("XY").box(400, 400, H, centered=False).translate((-200, -200, 0)))
    bot = m.intersect(cq.Workplane("XY").box(400, 400, H, centered=False).translate((-200, -200, -H)))
    for h in holes:
        top = top.cut(h)
    # dowels (3) and M3 clamp holes (6) around the rim
    for i, ang in enumerate([20, 140, 260]):
        a = math.radians(ang)
        r = R_out - rim/2
        p = (r*math.cos(a), r*math.sin(a))
        dw = cq.Workplane("XY").center(*p).circle(1.55).extrude(6).translate((0, 0, -6))
        top = top.cut(dw.translate((0, 0, 6)))
        bot = bot.cut(dw)
    for ang in [60, 100, 180, 220, 300, 340]:
        a = math.radians(ang)
        r = R_out - rim/2
        p = (r*math.cos(a), r*math.sin(a))
        bolt = cq.Workplane("XY").center(*p).circle(1.7).extrude(2*H + 2).translate((0, 0, -H - 1))
        top = top.cut(bolt)
        bot = bot.cut(bolt)
    return top, bot, R_out, H


if __name__ == "__main__":
    import time
    t0 = time.time()
    cavity, case_env, pod_env, tail, fw, fh, frt, prof = build()
    cxs, cws, chs, pxs, pws, phs = prof
    print("cavity built", round(time.time() - t0, 1), "s; face section", round(fw, 2), round(fh, 2))
    print("case env w/h max", round(max(cws), 1), round(max(chs), 1), " pod env w/h max", round(max(pws), 1), round(max(phs), 1))
    top, bot, R_out, H = mould_halves(cavity)
    print("mould R_out", round(R_out, 1), "half height", round(H, 1))
    cap_a, cap_b, pins, x_end = cp.make_cap(fw, fh, frt)
    # the silicone: cavity minus the parts' filled outlines (their insides are not silicone)
    case_fill = place(cp.rrect_prism(cp.case_L, cp.case_W, cp.case_r, 0.0, cp.case_top)
                      .faces(">Z").edges().fillet(cp.cover_fillet), cp.X_TOP, R0 - cp.land_pocket)
    xs_, ws_, hs_, rts_ = cp.pod_profile()
    pod_fill = cp.loft_sections(xs_, ws_, hs_, rts_, r_base=cp.Rn)
    band_cast = cavity.cut(cq.Workplane("XY").add(case_fill)).cut(cq.Workplane("XY").add(pod_fill))
    out = {"mould_top": top, "mould_bottom": bot, "band_cast": band_cast,
           "case_tray": cq.Workplane("XY").add(cp.case_tray_print), "case_cover": cq.Workplane("XY").add(cp.case_cover_print),
           "pod_shell": cq.Workplane("XY").add(cp.pod_shell_print), "pod_lid": cq.Workplane("XY").add(cp.pod_lid),
           "cap_a": cap_a, "cap_b": cap_b}
    for k, v in out.items():
        cq.exporters.export(v, f"v2_{k}.step")
        cq.exporters.export(v, f"v2_{k}.stl", tolerance=0.02, angularTolerance=0.1)
        s = v.val()
        print(k, "valid", s.isValid(), "solids", len(v.solids().vals()), "vol", round(s.Volume(), 1))
    asm = cq.Assembly()
    asm.add(bot, name="mould_bottom", color=cq.Color(0.55, 0.7, 0.9, 0.5))
    asm.add(band_cast, name="band_cast", color=cq.Color(0.2, 0.2, 0.22))
    for k, col in (("case_tray", (0.3, 0.3, 0.32)), ("case_cover", (0.4, 0.4, 0.42)),
                   ("pod_shell", (0.85, 0.55, 0.2)), ("pod_lid", (0.9, 0.75, 0.45)),
                   ("cap_a", (0.6, 0.6, 0.65)), ("cap_b", (0.55, 0.55, 0.6))):
        asm.add(out[k], name=k, color=cq.Color(*col))
    asm.save("v2_collar_assembly.step")
    print("pins at band x", [round(p, 1) for p in pins], "cap end x", round(x_end, 1),
          "silicone cm3", round(band_cast.val().Volume()/1000, 2), "total", round(time.time() - t0, 1), "s")
