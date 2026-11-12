"""
Cat-tracker RF mock-up: collar ring for a saline "neck" phantom + tray/lid for the
current 27.5 x 21.4 mm board, with a groove for a Synzen SZK-C-2L28 FPC antenna
(50 x 8.5 x 0.2 mm, 70 mm coax) set into the band.
Units: mm. Run with CadQuery 2.x:  python3 collar_mockup.py
"""
import math, cadquery as cq

# ---------------- parameters ----------------
neck_d      = 72.0    # phantom bottle diameter (~cat neck)
fit_clear   = 0.5     # ring slides over the bottle
band_t      = 2.5     # band radial thickness
band_w      = 11.0    # band width (axial); 11 leaves 1 mm lips beside the 9 mm FPC groove
fpc_len, fpc_w, fpc_depth = 51.0, 9.0, 0.8     # groove for the 50 x 8.5 x 0.2 FPC (+ tape)
coax_w, coax_d = 1.8, 1.5                      # channel for the 1.13 mm coax
coax_run    = 45.0    # arc length of coax along the band between tray and FPC
pad_len     = 32.0    # flat seat on top of the ring for the tray
pad_proud   = 1.5     # seat height above the ring's outer surface
pin_d, pin_h, pin_x = 2.0, 1.5, 10.0           # locating pins on the seat
pin_dz      = 3.0     # pins sit off the band centre-line (the coax runs down the middle)

board_l, board_w = 27.5, 21.4                  # current tracker PCB
clr, wall, floor_t = 0.4, 1.2, 1.2
bat_h       = 3.5     # spacer under the board (battery now lives in the pod); keeps the board off the neck
board_t, top_parts = 1.6, 2.6
ledge       = 1.0
ufl_y       = 13.5    # U.FL (J4) distance from the board's top edge (from cattrax.6.kicad_pcb)
usb_x0, usb_x1 = 6.0, 16.0                     # micro-USB access along the bottom edge

Ri = neck_d/2 + fit_clear/2
Ro = Ri + band_t

def sector(r0, r1, a0, a1, z0, h, n=96):
    """Annular sector between angles a0..a1 (deg, CCW from +X), extruded h from z0."""
    outer = [(r1*math.cos(math.radians(a)), r1*math.sin(math.radians(a)))
             for a in [a0 + (a1-a0)*i/n for i in range(n+1)]]
    inner = [(r0*math.cos(math.radians(a)), r0*math.sin(math.radians(a)))
             for a in [a1 - (a1-a0)*i/n for i in range(n+1)]]
    return cq.Workplane("XY").workplane(offset=z0).polyline(outer+inner).close().extrude(h)

# ---------------- ring ----------------
ring = (cq.Workplane("XY").circle(Ro).circle(Ri).extrude(band_w))
# flat seat at the top (+Y)
pad_top = Ro + pad_proud
pad = (cq.Workplane("XY").center(0, (pad_top + Ri)/2)
       .rect(pad_len, pad_top - Ri).extrude(band_w))
ring = ring.union(pad).cut(cq.Workplane("XY").circle(Ri).extrude(band_w))
# locating pins on the seat (pointing +Y)
for x in (-pin_x, pin_x):
    pin = (cq.Workplane("XZ", origin=(x, pad_top, band_w/2 + pin_dz)).circle(pin_d/2).extrude(-pin_h))
    ring = ring.union(pin)

# angles: seat edge, coax channel, FPC groove (on the -X / left side, toward the U.FL end)
a_seat = 90 + math.degrees((pad_len/2)/Ro)
a_fpc0 = a_seat + math.degrees(coax_run/Ro)
a_fpc1 = a_fpc0 + math.degrees(fpc_len/Ro)
assert a_fpc1 < 268, "FPC would reach the bottom of the collar"
z_mid = band_w/2
ring = ring.cut(sector(Ro-fpc_depth, Ro+3, a_fpc0, a_fpc1, z_mid-fpc_w/2, fpc_w))
ring = ring.cut(sector(Ro-coax_d, Ro+3, 90+2, a_fpc0+1, z_mid-coax_w/2, coax_w))
# coax channel continues across the seat top to its left end
ring = ring.cut(cq.Workplane("XY").center(-(pad_len/4+1), pad_top-coax_d/2)
                .rect(pad_len/2+2, coax_d).extrude(coax_w).translate((0,0,z_mid-coax_w/2)))

# (re)add the pins after the channel cuts
for x in (-pin_x, pin_x):
    ring = ring.union(cq.Workplane("XZ", origin=(x, pad_top, band_w/2 + pin_dz)).circle(pin_d/2).extrude(-pin_h))

# ---------------- battery pod seat (right side) + lead channel ----------------
cell_l, cell_w, cell_t = 24.0, 20.0, 8.0       # bare pouch body (e.g. LP802024); edit to suit
pod_angle  = 300.0    # pod centre on the ring (deg, 270 = bottom, right side)
lead_w, lead_d = 2.0, 1.2                      # channel for the battery leads / flex
pod_seat_len = cell_l + 2*clr + 2*wall
def seat_at(angle, length):
    """Flat seat like the top one, rotated to `angle`."""
    p_top = Ro + pad_proud
    seat = (cq.Workplane("XY").center(0, (p_top + Ri)/2).rect(length, p_top - Ri).extrude(band_w))
    return seat.rotate((0,0,0), (0,0,1), angle - 90), p_top
pseat, _ = seat_at(pod_angle, pod_seat_len)
ring = ring.union(pseat).cut(cq.Workplane("XY").circle(Ri).extrude(band_w))
for x in (-pin_x, pin_x):
    pin = (cq.Workplane("XZ", origin=(x, pad_top, band_w/2 + pin_dz)).circle(pin_d/2).extrude(-pin_h)
           .rotate((0,0,0), (0,0,1), pod_angle - 90))
    ring = ring.union(pin)
a_seat_r = 90 - math.degrees((pad_len/2)/Ro)
a_pod_top = pod_angle + math.degrees((pod_seat_len/2)/Ro)
ring = ring.cut(sector(Ro - lead_d, Ro + 3, a_pod_top - 3 - 360, a_seat_r + 1, z_mid - lead_w/2, lead_w))

# ---------------- pod (battery box) + pod lid ----------------
p_in_l, p_in_w, p_in_h = cell_l + 2*clr, cell_w + 2*clr, cell_t + 0.6
pod = (cq.Workplane("XY").rect(p_in_l + 2*wall, p_in_w + 2*wall).extrude(p_in_h + floor_t)
       .cut(cq.Workplane("XY").workplane(offset=floor_t).rect(p_in_l, p_in_w).extrude(p_in_h)))
for x in (-pin_x, pin_x):
    pod = pod.cut(cq.Workplane("XY").center(x, -pin_dz).circle(pin_d/2 + 0.2).extrude(floor_t))
# lead exit through the floor at the end nearest the tracker (+X end after placement)
pod = pod.cut(cq.Workplane("XY").center(p_in_l/2 - 2, 0).rect(4 + 2*wall, lead_w + 0.6).extrude(floor_t + 2.5))
pod_lid = (cq.Workplane("XY").rect(p_in_l + 2*wall, p_in_w + 2*wall).extrude(1.2)
           .union(cq.Workplane("XY").workplane(offset=1.2).rect(p_in_l - 0.4, p_in_w - 0.4).extrude(0.8)
                  .cut(cq.Workplane("XY").workplane(offset=1.2).rect(p_in_l - 2.4, p_in_w - 2.4).extrude(0.8))))

# ---------------- tray ----------------
in_l, in_w = board_l + 2*clr, board_w + 2*clr
in_h = bat_h + board_t + top_parts
out_l, out_w, out_h = in_l + 2*wall, in_w + 2*wall, in_h + floor_t
tray = (cq.Workplane("XY").rect(out_l, out_w).extrude(out_h)
        .cut(cq.Workplane("XY").workplane(offset=floor_t).rect(in_l, in_w).extrude(in_h)))
# board ledges along the long walls at battery height
for s in (-1, 1):
    tray = tray.union(cq.Workplane("XY").workplane(offset=floor_t)
                      .center(0, s*(in_w/2 - ledge/2)).rect(in_l, ledge).extrude(bat_h))
# pin holes in the floor (tray Y = band axis, centred)
for x in (-pin_x, pin_x):
    tray = tray.cut(cq.Workplane("XY").center(x, -pin_dz).circle(pin_d/2 + 0.2).extrude(floor_t))
# coax entry: slot through the floor + left wall, under the U.FL end
y_ufl = in_w/2 - clr - ufl_y          # board top edge at +Y
tray = tray.cut(cq.Workplane("XY").center(-out_l/2 + wall + 2, 0)
                .rect(4 + 2*wall, coax_w + 0.6).extrude(floor_t + 2.5))
# micro-USB access in the bottom (-Y) wall, at board height
tray = tray.cut(cq.Workplane("XY").workplane(offset=floor_t + bat_h - 0.5)
                .center(-in_l/2 + clr + (usb_x0+usb_x1)/2, -(out_w/2))
                .rect(usb_x1-usb_x0, 2*wall + 1).extrude(top_parts + board_t + 1))

# ---------------- lid ----------------
lid = (cq.Workplane("XY").rect(out_l, out_w).extrude(1.2)
       .union(cq.Workplane("XY").workplane(offset=1.2)
              .rect(in_l - 0.4, in_w - 0.4).extrude(0.8)
              .cut(cq.Workplane("XY").workplane(offset=1.2)
                   .rect(in_l - 2.4, in_w - 2.4).extrude(0.8))))

if __name__ == "__main__":
    for name, part in (("ring", ring), ("tray", tray), ("lid", lid), ("pod", pod), ("pod_lid", pod_lid)):
        cq.exporters.export(part, f"{name}.step")
        cq.exporters.export(part, f"{name}.stl", tolerance=0.02, angularTolerance=0.1)
    asm = (cq.Assembly()
           .add(ring, name="ring", color=cq.Color(0.3, 0.3, 0.3))
           .add(tray, name="tray", color=cq.Color(0.2, 0.5, 0.8),
                loc=cq.Location((0, pad_top, band_w/2), (1, 0, 0), -90))
           .add(lid, name="lid", color=cq.Color(0.8, 0.8, 0.8),
                loc=cq.Location((0, pad_top + out_h + 1.2, band_w/2), (1, 0, 0), 90)))
    pod_h = p_in_h + floor_t
    asm.add(pod, name="pod", color=cq.Color(0.8, 0.5, 0.2),
            loc=cq.Location((0,0,0)) * cq.Location((0,0,0), (0,0,1), pod_angle - 90)
                * cq.Location((0, pad_top, band_w/2), (1, 0, 0), -90))
    asm.add(pod_lid, name="pod_lid", color=cq.Color(0.9, 0.7, 0.4),
            loc=cq.Location((0,0,0)) * cq.Location((0,0,0), (0,0,1), pod_angle - 90)
                * cq.Location((0, pad_top + pod_h + 1.2, band_w/2), (1, 0, 0), 90))
    asm.save("collar_mockup_assembly.step")
    print(f"Ri={Ri:.2f} Ro={Ro:.2f}  coax {a_seat:.0f}->{a_fpc0:.0f} deg, FPC {a_fpc0:.0f}->{a_fpc1:.0f} deg")
    print(f"tray outer {out_l:.1f} x {out_w:.1f} x {out_h:.1f} mm")
