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

Run: python3 placement_v0.py  ->  placement_v0.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

L, W = 20.0, 17.0           # board: x 0..20, y -8.5..+8.5
Y0, Y1 = -W / 2, W / 2

C = dict(rf915="#f4a261", rf24="#e76f51", mcu="#8ecae6", pwr="#ffd166", gnss="#90be6d",
         sens="#cdb4db", dock="#adb5bd", misc="#e9ecef", pad="#c9a227")

# (label, x0, y0, w, h, colour, note)
TOP = [
    # 915 MHz radio, left end, over the ANT feed
    ("SX1262\nQFN24 4×4", 0.6, 3.4, 4.0, 4.0, C["rf915"], "RF pins face down, to the switch"),
    ("X3 32M\n2016", 4.9, 6.6, 2.0, 1.6, C["rf915"], "crystal or TCXO (DIO3)"),
    ("L/VREG", 4.9, 4.6, 1.6, 1.6, C["rf915"], "DCC_SW inductor + VREG cap"),
    ("PE4259\nSC70-6", 0.6, 0.4, 2.2, 2.1, C["rf915"], ""),
    ("915 TX/RX match\n+ balun (0201/0402)", 0.4, -2.4, 5.2, 2.5, C["rf915"], "feed via beside ANT pad"),
    # nRF54L10
    ("nRF54L10\nQFN48 6×6", 7.4, 0.0, 6.0, 6.0, C["mcu"], "ANT pin 31 on right side"),
    ("DC-DC L1 0603\n+ DECx caps", 7.1, 6.3, 3.4, 2.0, C["mcu"], "pins 43–48 top-left"),
    ("X1 32k\n2012", 5.6, 2.2, 1.6, 1.25, C["mcu"], "pins 1–2"),
    ("X2 32M\n2016", 11.0, 6.5, 2.0, 1.6, C["mcu"], "pins 34–35"),
    ("2.4 GHz match\nL2–C11 (0201)", 13.6, 2.6, 2.8, 2.6, C["rf24"], "inner planes cut out; bottom GND"),
    ("2.4 GHz\nchip ant.", 17.4, 5.0, 2.5, 3.2, C["rf24"], "part TBD (2450AT42E010B?)"),
    # power, right end, over GND/VBAT pads
    ("nPM1300\nQFN32 5×5", 14.6, -6.8, 5.0, 5.0, C["pwr"], ""),
    ("L BUCK1\n2016", 14.0, -8.4, 2.0, 1.6, C["pwr"], "1V8"),
    ("L BUCK2\n2016", 16.2, -8.4, 2.0, 1.6, C["pwr"], "3V3_RF"),
    ("VSET, VBUS/\nVSYS caps", 14.6, -1.6, 5.0, 1.6, C["pwr"], ""),
    # GNSS, lower left
    ("MIA-M10Q\nLGA 4.5×4.5", 5.6, -8.2, 4.5, 4.5, C["gnss"], "RF_IN side toward antenna (check)"),
    ("GNSS ant.\nACAG0301", 0.3, -8.3, 3.2, 1.6, C["gnss"], "size assumed 3.2×1.6"),
    ("LIS2DW12\n2×2", 11.0, -2.6, 2.0, 2.0, C["sens"], ""),
    ("I2C pull-ups,\nGNSS caps", 10.4, -6.5, 3.6, 2.0, C["misc"], ""),
]

TOP_KEEPOUT = [  # (label, x0, y0, w, h)
    ("GNSS ant. clearance", 0.0, -8.5, 5.2, 3.6),
    ("2.4 GHz ant. clearance", 16.8, 4.6, 3.2, 3.9),
]

# Bottom side (x-ray from top). Centre strip y -4..+4 is parts-free; flex pads live there.
FLEX_PADS = [("ANT", 0.6, -2.5, 3.0, 5.0), ("MECH", 8.0, -2.5, 2.0, 5.0),
             ("GND", 15.0, -3.5, 4.4, 4.1), ("VBAT", 15.0, 1.4, 4.4, 1.9)]
TARGETS = [  # dock targets Ø3.2, centred in the 4.5 mm side strips (y = ±6.25); keyed pattern
    ("RX", 2.6, 6.25), ("TX", 10.6, 6.25), ("GND", 8.0, -6.25), ("VBUS", 16.6, -6.25)]
BOT = [
    ("TMUX\n(RX)", 4.6, 4.6, 2.0, 2.1, C["dock"], "SC70-5"),
    ("TMUX\n(TX)", 7.0, 4.6, 2.0, 2.1, C["dock"], "SC70-5"),
    ("SEL div.", 4.6, 7.0, 3.0, 1.2, C["dock"], "100k/150k"),
    ("ESD", 0.3, 4.4, 1.0, 0.6, C["dock"], "TPD1E10B06"),
    ("ESD", 12.6, 4.4, 1.0, 0.6, C["dock"], ""),
    ("ESD", 10.0, -4.9, 1.0, 0.6, C["dock"], ""),
    ("ESD", 18.6, -4.9, 1.0, 0.6, C["dock"], ""),
    ("SWD test pads\n(5 × Ø0.8)", 11.0, -8.3, 3.6, 2.4, C["misc"], "pogo fixture before potting"),
    ("GNSS UART\nTPs", 5.4, -5.4, 2.4, 1.2, C["misc"], "u-center bring-up"),
]
BOT_KEEPOUT = [
    ("solid GND\n(under 2.4 GHz\nmatch)", 13.4, 4.0, 3.4, 4.5),
    ("no copper\n(2.4 ant.)", 16.8, 4.6, 3.2, 3.9),
    ("no copper\n(GNSS ant.)", 0.0, -8.5, 5.2, 3.6),
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
board(a1, "TOP (sky side) — draft v0")
keepouts(a1, TOP_KEEPOUT)
boxes(a1, TOP)

board(a2, "BOTTOM (neck side), x-ray from top — draft v0")
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
a2.annotate("915 feed via\n(beside pad)", (2.1, -1.0), (4.2, -3.2), fontsize=6,
            arrowprops=dict(arrowstyle="->", lw=0.6))

fig.text(0.5, 0.01,
         "Draft from datasheet package sizes + docs/interface.md constraints. Not to-pin accurate: check "
         "SX1262 / MIA-M10Q pin sides, antenna part and clearances, nPM1300 inductor size before layout.",
         ha="center", fontsize=8)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("placement_v0.png", dpi=170)
print("wrote placement_v0.png")
