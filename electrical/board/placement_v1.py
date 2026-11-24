"""Draft component placement for the cattraxV2 main board (17 x 20 mm), top and bottom.

Best-guess floorplan, not a layout. Coordinates in mm: x along the band (0 = left edge,
antenna side), y across the board (0 = centre line, +y = "north" edge). Both views are drawn
looking down on the TOP side (bottom side is shown x-ray, not mirrored), so they line up.

Sources:
- docs/interface.md: board size, 8 mm parts-free centre strip on the underside, flex pad
  positions, dock targets in the side strips.
- docs/electrical.md: parts, 2.4 GHz match rules (inner planes cut out, bottom-layer ground
  under the match), floorplan intent.
- Package sizes from the part datasheets / LCSC listings (see PARTS notes); items marked
  "assumed" still need checking against their datasheets.

Run: python3 placement_v1.py  ->  placement_v1.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

L, W = 20.0, 17.0           # board: x 0..20, y -8.5..+8.5
Y0, Y1 = -W / 2, W / 2

C = dict(rf915="#f4a261", rf24="#e76f51", mcu="#8ecae6", pwr="#ffd166", gnss="#90be6d",
         sens="#cdb4db", dock="#adb5bd", misc="#e9ecef", pad="#c9a227")

# (label, x0, y0, w, h, colour, note)   -- v1: pin sides from the datasheets
# SX1262 (DS rev 1.2 Fig 2-1): RF pins 21-24 on the top edge, SPI 16-19 right edge,
#   VREG/DCC_SW/VBAT/VBAT_IO/DIO2 bottom edge, XTA/XTB/DIO3 left edge.  Placed unrotated.
# nRF54L10 QFN48 (DS v0.8 Table 73): SPI P1.04-07 left edge; ANT 31 + XC1/XC2 34/35 right edge
#   (upper half); I2C/PMIC_INT/SWD right edge (lower half); DCC/DECD/DECA + UART P1.13/14 top edge.
# MIA-M10Q (IM R05 Fig 2): RF_IN = ball B9 (top-right corner) -> rotate so B9 faces the antenna.
# nPM1300 QFN32 (PS v1.3 Table 34): SW1/SW2 left edge, VBAT/VSYS/VBUS right edge, VOUT2 top.
TOP = [
    # 915 MHz radio, lower-left; RF edge faces up to the switch/match above it
    ("SX1262\nQFN24 4x4\n(RF edge up)", 2.4, -7.4, 4.0, 4.0, C["rf915"], ""),
    ("X3 32M\n2016", 0.3, -7.2, 1.7, 2.1, C["rf915"], "XTA/XTB left edge"),
    ("L 15u + VREG/VBAT caps", 2.0, -8.45, 5.6, 0.9, C["rf915"], "bottom-edge pins"),
    ("TX/RX match + balun\n+ SKY13323 (1x1)", 0.3, -3.2, 5.6, 2.9, C["rf915"], "above ANT feed"),
    ("VR_PA\ncaps", 0.3, -0.2, 2.4, 1.0, C["rf915"], ""),
    ("LV1T34\n+LV1T04", 6.7, -7.4, 1.6, 4.0, C["rf915"], "SKY13323 VCTL at 3.3 V"),
    # nRF54L10, centre
    ("nRF54L10\nQFN48 6x6", 7.6, 0.2, 6.0, 6.0, C["mcu"], ""),
    ("L1 4.7u + DECD/\nDECA caps, FB", 7.6, 6.4, 3.6, 2.0, C["mcu"], "pins 43-48 top edge"),
    ("X2 32M\n2016", 11.5, 6.6, 2.0, 1.6, C["mcu"], "XC1/XC2 pins 34-35"),
    ("X1 32k\n2012", 5.7, 4.3, 1.6, 1.25, C["mcu"], "XL1/XL2 pins 1-2"),
    ("VDD caps", 5.7, 2.9, 1.7, 1.2, C["mcu"], ""),
    ("2.4 GHz match\nL2-C11 (0201)", 13.8, 3.0, 2.6, 2.6, C["rf24"], "inner planes cut; bottom GND"),
    ("2.4 GHz\nchip ant.", 17.4, 5.0, 2.5, 3.2, C["rf24"], "part TBD"),
    # GNSS, upper-left; antenna in the top-left corner
    ("GNSS ant.\nACAG0301", 0.3, 6.8, 3.2, 1.6, C["gnss"], "size assumed"),
    ("MIA-M10Q\nLGA 4.5x4.5\n(B9 corner up-left)", 0.6, 0.9, 4.5, 4.5, C["gnss"], ""),
    ("TPS7A20\n1V8 LDO", 3.8, 5.6, 1.8, 1.0, C["gnss"], "GNSS_1V8 +-1.5%"),
    # power, lower-right over the GND/VBAT pads
    ("nPM1300\nQFN32 5x5", 14.8, -6.9, 5.0, 5.0, C["pwr"], "VBAT/VBUS edge faces right"),
    ("L SW1\n2.2u 0806", 12.4, -6.5, 2.0, 1.7, C["pwr"], "1V8"),
    ("L SW2\n2.2u 0806", 12.4, -4.5, 2.0, 1.7, C["pwr"], "3V3_RF"),
    ("VSYS/VBUS/VBAT caps", 14.8, -8.45, 5.0, 1.4, C["pwr"], ""),
    ("VOUT caps, VSET", 14.8, -1.7, 5.0, 1.4, C["pwr"], ""),
    ("LIS2DW12\n2x2", 9.6, -2.4, 2.0, 2.0, C["sens"], ""),
    ("I2C pull-ups", 9.0, -3.9, 3.0, 1.2, C["misc"], ""),
]

TOP_KEEPOUT = [  # (label, x0, y0, w, h)
    ("GNSS ant. clearance", 0.0, 5.3, 3.7, 3.2),
    ("2.4 GHz ant. clearance", 16.8, 4.6, 3.2, 3.9),
]

# Bottom side (x-ray from top). Centre strip y -4..+4 is parts-free; flex pads live there.
FLEX_PADS = [("ANT", 0.6, -2.5, 3.0, 5.0), ("MECH", 8.0, -2.5, 2.0, 5.0),
             ("GND", 15.0, -3.5, 4.4, 4.1), ("VBAT", 15.0, 1.4, 4.4, 1.9)]
TARGETS = [  # dock targets dia 3.2, centred in the 4.5 mm side strips (y = +-6.25); keyed pattern
    ("RX", 7.0, 6.25), ("TX", 11.2, 6.25), ("GND", 3.0, -6.25), ("VBUS", 16.6, -6.25)]
BOT = [
    ("TMUX\n(RX)", 5.4, -8.3, 2.0, 2.1, C["dock"], "SC70-5"),
    ("TMUX\n(TX)", 7.6, -8.3, 2.0, 2.1, C["dock"], "SC70-5"),
    ("SEL div.", 5.4, -5.9, 4.2, 1.1, C["dock"], "100k/150k"),
    ("ESD", 4.4, 4.4, 1.0, 0.6, C["dock"], "TPD1E10B06"),
    ("ESD", 12.8, 4.4, 1.0, 0.6, C["dock"], ""),
    ("ESD", 0.4, -4.9, 1.0, 0.6, C["dock"], ""),
    ("ESD", 18.6, -4.9, 1.0, 0.6, C["dock"], ""),
    ("SWD test pads\n(5 x 0.8)", 10.0, -8.3, 3.8, 2.4, C["misc"], "pogo fixture before potting"),
    ("GNSS UART /\nSAFEBOOT TPs", 10.0, -5.7, 3.8, 1.4, C["misc"], "u-center bring-up"),
]
BOT_KEEPOUT = [
    ("solid GND (under 2.4 GHz match)", 13.4, 4.0, 3.4, 4.5),
    ("no copper (2.4 ant.)", 16.8, 4.6, 3.2, 3.9),
    ("no copper (GNSS ant.)", 0.0, 5.3, 3.7, 3.2),
]


def board(ax, title):
    ax.add_patch(Rectangle((0, Y0), L, W, fc="#2d6a4f", ec="k", lw=1.5, alpha=0.18))
    ax.set_xlim(-1.5, L + 1.5)
    ax.set_ylim(Y0 - 1.5, Y1 + 1.5)
    ax.set_aspect("equal")
    ax.set_xticks(range(0, 21, 2))
    ax.set_yticks([-8, -6, -4, -2, 0, 2, 4, 6, 8])
    ax.grid(True, lw=0.3, alpha=0.5)
    ax.set_title(title, fontsize=11, weight="bold")
    ax.set_xlabel("x (mm, along band) — antenna arm ←   → counterpoise / pod")
    ax.set_ylabel("y (mm)")


def boxes(ax, items, fs=6):
    for lab, x, y, w, h, col, _ in items:
        ax.add_patch(Rectangle((x, y), w, h, fc=col, ec="k", lw=0.7))
        ax.text(x + w / 2, y + h / 2, lab, ha="center", va="center", fontsize=fs)


def keepouts(ax, items, hatch="////", col="#d62828"):
    for lab, x, y, w, h in items:
        ax.add_patch(Rectangle((x, y), w, h, fill=False, ec=col, lw=1, ls="--", hatch=hatch,
                               alpha=0.6))
        ax.text(x + w / 2, y + h + 0.05, lab.replace("\n", " "), ha="center", va="bottom", fontsize=5.5, color=col,
                bbox=dict(fc="white", ec="none", alpha=0.7, pad=0.5))


fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 7.2))
board(a1, "TOP (sky side) — v1, pin sides per datasheets")
keepouts(a1, TOP_KEEPOUT)
boxes(a1, TOP)

board(a2, "BOTTOM (neck side), x-ray from top — v1")
a2.add_patch(Rectangle((0, -4), L, 8, fc="#ffffff", ec="#495057", lw=0.8, ls=":", alpha=0.6))
a2.text(11.8, -3.6, "8 mm centre strip: no parts (flex lies here)", ha="center", va="center",
        fontsize=7, color="#495057")
for lab, x, y, w, h in FLEX_PADS:
    a2.add_patch(Rectangle((x, y), w, h, fc=C["pad"], ec="k", lw=0.7, alpha=0.85))
    a2.text(x + w / 2, y + h / 2, lab, ha="center", va="center", fontsize=7, weight="bold")
for lab, x, y in TARGETS:
    a2.add_patch(Circle((x, y), 1.6, fc="#ffe066", ec="k", lw=0.9))
    a2.text(x, y, lab, ha="center", va="center", fontsize=7, weight="bold")
keepouts(a2, BOT_KEEPOUT)
boxes(a2, BOT)
a2.plot([2.1], [-1.0], "ko", ms=3)
a2.annotate("915 feed via\n(beside pad)", (2.1, -1.0), (5.0, 1.5), fontsize=6,
            arrowprops=dict(arrowstyle="->", lw=0.6))

fig.text(0.5, 0.01,
         "v1: pin sides from SX1262 DS 1.2, nRF54L DS 0.8, MIA-M10Q IM R05, nPM1300 PS 1.3. Still assumed: antenna parts/clearances, "
         "LV1T gate package, inductor sizes.",
         ha="center", fontsize=8)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("placement_v1.png", dpi=170)
print("wrote placement_v1.png")
