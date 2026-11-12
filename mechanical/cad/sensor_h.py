"""
Breakaway sensor in the pod (concept): TI TMAG3001A2 3D linear Hall sensor (DSBGA-6, 0.83 x 1.32 mm,
~0.5 mm tall -- check the package drawing) on the main flex, which simply continues (full 8 mm width) under the cast-in cell.
It dives under the cell past the battery-tab pads at the lid end, and carries
VCC / GND / SDA / SCL / INT back along the band to the tracker PCB.

Sensor at band x = XS (about 7 mm behind the pod magnet's back face, under the cell end), where
the clasp-closed field stays inside the +/-120 mT range. Run sections_h.py for the views.
"""
import math, cadquery as cq
import pod_v3 as p
from collar_parts import R0, W, ring_sector, smooth

XS = 113.5                 # sensor centre, band x
IC = (1.32, 0.83, 0.50)    # along band, across band, height (DSBGA-6 YBG; height assumed)
TONGUE_W = 8.0            # full main-flex width: no branch, the main flex just continues
FLEX_T = 0.11
H_BAND = 1.6               # flex height in the band (bottom face, above the neck)
H_POD = 0.35               # tongue bottom face under the cell
X_DIVE = (81.0, 91.0)      # dives from H_BAND to H_POD after the battery tab pads (x 75.5-80.5)
X_START, X_END = 66.0, XS + 2.0


STIFF_T, STIFF_X0 = 0.1, 109.0   # PI stiffener under the sensor end (tip handling + flat mount)
KEY_D, KEY_PITCH, KEY_Y = 1.2, 5.0, 2.9   # silicone key holes along both edges (copper within +/-2.1, 0.5 web to the edge)


def tongue_h(x):
    t = (x - X_DIVE[0])/(X_DIVE[1] - X_DIVE[0])
    t = min(1.0, max(0.0, t))
    h = H_POD + (H_BAND - H_POD)*(1 - smooth(t))
    if x > STIFF_X0 - 3:                 # step up 0.1 onto the stiffener near the sensor
        h += STIFF_T*smooth(min(1.0, (x - (STIFF_X0 - 3))/3))
    return h


def tongue():
    s = None
    x = X_START
    while x < X_END - 1e-6:
        x1 = min(X_END, x + 0.5)
        h = tongue_h((x + x1)/2)
        seg = ring_sector(R0 + h, R0 + h + FLEX_T, -TONGUE_W/2, TONGUE_W/2, x, x1)
        s = seg if s is None else s.fuse(seg)
        x = x1
    s = W(s.clean())
    from collar_parts import radial_cyl
    x = 95.0
    while x < STIFF_X0 - 3:
        for y in (-KEY_Y, KEY_Y):
            s = s.cut(W(radial_cyl(x, R0, 3, KEY_D, z=y)))
        x += KEY_PITCH
    return s


def stiffener():
    h = tongue_h(X_END) - STIFF_T
    return W(ring_sector(R0 + h, R0 + h + STIFF_T, -TONGUE_W/2, TONGUE_W/2, STIFF_X0, X_END))


def sensor():
    h0 = tongue_h(XS) + FLEX_T
    ic = ring_sector(R0 + h0, R0 + h0 + IC[2], -IC[1]/2, IC[1]/2, XS - IC[0]/2, XS + IC[0]/2)
    cap = ring_sector(R0 + h0, R0 + h0 + 0.33, -0.3, 0.3, XS - 2.0, XS - 1.4)     # 0201 decoupling cap
    return W(ic), W(cap)
