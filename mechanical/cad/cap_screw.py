"""
Screw-clamped fit-and-trim cap for the v3 pod (replaces the glued, pinned cap in pod_v3.py).

Split into an outer SHELL and a thin neck-side BASE plate (split surface at BASE_T above the neck).
Two M1.6 countersunk screws (DIN 965 / ISO 7046, M1.6 x 8) go in from the neck side, flush,
pass through base, band tail (+ flex) and shell, and thread into M1.6 hex nuts (DIN 934,
3.2 AF x 1.3) sitting flush in hex insets on the outside of the shell.
The screws clamp shell + tail + base together: no glue, and re-sizing is unscrew / move / re-screw.
The cap magnet drops into the shell from below and is held by a tongue on the base plate.

Run: python3 cap_screw.py -> v3s_cap_shell / v3s_cap_base (.step/.stl) + hardware placeholders.
"""
import math
import cadquery as cq
import pod_v3 as p
from collar_parts import R0, place, box, W, loft_sections, ring_sector, radial_cyl, smooth, band_w, band_t, skin

# ---- parameters
BASE_T = 1.5            # base plate under the tail (CSK head 0.96 deep sits in it)
SLOT_CLR = 0.3          # slot height = band_t + SLOT_CLR
TOP_T = 2.6             # shell wall above the slot: 1.35 nut inset + 1.25 under it
SLOT_LEN = 11.0
PITCH = 5.0
SCREW_X = (3.7, 8.7)    # screw positions back from the cap end (one pitch apart)
M = dict(d=1.6, clr=1.8, csk_d=3.1, csk_k=0.72, nut_af=3.2, nut_m=1.3, L=8.0)
END_H = BASE_T + band_t + SLOT_CLR + TOP_T      # cap height over the neck at the screws (8.0)
END_W = 14.4


def _hex_local(af, depth, z_top):
    """Hex prism (flat-to-flat af) in the local frame, from z_top - depth to z_top, radial axis."""
    return (cq.Workplane("XY", origin=(0, 0, z_top - depth)).polygon(6, af/math.cos(math.pi/6))
            .extrude(depth + 0.5))


def cap_parts(face_w, face_h):
    x0 = p.FACE_BX + p.cap_gap*R0/(R0 + p.clasp_h)
    xs = [x0 + i for i in range(int(p.cap_len) + 1)]
    x_end = xs[-1]
    # height ramps from the clasp face down to END_H, and holds END_H over the screw zone
    hs, ws = [], []
    for x in xs:
        t = min(1.0, (x - x0)/(p.cap_len - SLOT_LEN))
        hs.append(face_h + (END_H - face_h)*smooth(t))
        ws.append(face_w + (END_W - face_w)*smooth(t))
    rts = [min(3.0, h/2 - 0.2) for h in hs]
    c = W(loft_sections(xs, ws, hs, rts))
    zc0 = p.clasp_h - skin
    boss = (cq.Workplane("YZ", origin=(p.cap_gap - p.recess_depth, 0, zc0)).rect(p.floor_y - 0.2, p.floor_z - 0.2)
            .workplane(offset=p.recess_depth + 0.3).rect(p.open_y - 0.2, p.open_z - 0.2).loft())
    c = c.union(W(place(boss, p.FACE_BX, R0 + skin)))

    # magnet pocket, opened down to the split surface so the magnet drops in from below
    mx0 = p.cap_gap - p.recess_depth + p.mag_skin
    z_bot_mag = zc0 - p.pocket[2]/2                       # pocket floor, face frame (origin R0 + skin)
    split_local = BASE_T - skin                           # split surface in the same frame
    mp = (cq.Workplane("YZ", origin=(mx0, 0, 0)).center(0, (split_local - 0.05 + zc0 + p.pocket[2]/2)/2)
          .rect(p.pocket[1], (zc0 + p.pocket[2]/2) - (split_local - 0.05)).extrude(p.pocket[0]))
    c = c.cut(W(place(mp, p.FACE_BX, R0 + skin)))

    # tail slot sits on the base plate
    s0, s1 = R0 + BASE_T, R0 + BASE_T + band_t + SLOT_CLR
    c = c.cut(W(ring_sector(s0, s1, -(band_w + 0.4)/2, (band_w + 0.4)/2, x_end - SLOT_LEN, x_end + 2)))

    # screws: clearance through everything, CSK in the base (neck side), hex nut inset in the shell top
    screws_x = [x_end - d for d in SCREW_X]
    for x in screws_x:
        c = c.cut(W(radial_cyl(x, R0 - 1, 12, M["clr"])))
        csk = cq.Solid.makeCone(M["csk_d"]/2, M["clr"]/2, (M["csk_d"] - M["clr"])/2,
                                cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
        csk = csk.fuse(cq.Solid.makeCylinder(M["csk_d"]/2, 1.0, cq.Vector(0, 0, -1.0), cq.Vector(0, 0, 1)))
        c = c.cut(W(place(csk, x, R0)))
        c = c.cut(W(place(_hex_local(M["nut_af"] + 0.1, M["nut_m"] + 0.05, END_H), x, R0)))

    # split: base = everything below R0 + BASE_T, shell = above
    lo = W(ring_sector(R0 - 2, R0 + BASE_T, -20, 20, x0 - 5, x_end + 5))
    base = c.intersect(lo)
    shell = c.cut(lo)
    # tongue on the base: fills the pocket extension under the magnet and keys the front end
    tg = (cq.Workplane("YZ", origin=(mx0 + 0.05, 0, 0)).center(0, (split_local - 0.2 + z_bot_mag)/2)
          .rect(p.pocket[1] - 0.15, z_bot_mag - split_local + 0.2).extrude(p.pocket[0] - 0.1))
    base = base.union(W(place(tg, p.FACE_BX, R0 + skin)))

    # hardware placeholders (for sections / checks)
    hw = {}
    scr = None
    nut = None
    for x in screws_x:
        head = cq.Solid.makeCone(M["csk_d"]/2 - 0.05, M["d"]/2, M["csk_k"], cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
        shank = cq.Solid.makeCylinder(M["d"]/2, M["L"] - M["csk_k"], cq.Vector(0, 0, M["csk_k"]), cq.Vector(0, 0, 1))
        s = W(place(head.fuse(shank), x, R0))
        n = (cq.Workplane("XY", origin=(0, 0, END_H - M["nut_m"])).polygon(6, M["nut_af"]/math.cos(math.pi/6))
             .extrude(M["nut_m"]).faces(">Z").workplane().hole(M["d"]))
        n = W(place(n, x, R0))
        scr = s if scr is None else scr.union(s)
        nut = n if nut is None else nut.union(n)
    hw = {"screws": scr, "nuts": nut}
    return shell, base, hw, dict(x0=x0, x_end=x_end, screws_x=screws_x, slot=(BASE_T, BASE_T + band_t + SLOT_CLR))


if __name__ == "__main__":
    env, xs, ws, hs = p.envelope()
    shell, base, hw, info = cap_parts(ws[-1], hs[-1])
    for k, v in {"cap_shell": shell, "cap_base": base, "screws_M1.6x8": hw["screws"], "nuts_M1.6": hw["nuts"]}.items():
        cq.exporters.export(v, f"v3s_{k}.step")
        cq.exporters.export(v, f"v3s_{k}.stl", tolerance=0.02, angularTolerance=0.1)
        print(k, v.val().isValid(), len(v.solids().vals()), round(v.val().Volume(), 1))
    print(info, "END_H", END_H)
