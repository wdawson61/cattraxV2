"""
Concept layout for the single collar flex: antenna arm (left) + battery/counterpoise arm (right),
continuous under a 15 x 20 mm tracker board. x = 0 at the board's left edge, along the band.
Outputs flex_strip.png (dimensioned sketch) and flex_strip.dxf (layers: EDGE, TOP_CU, BOT_CU,
HOLES, BOARD, PARTS) for import into KiCad (File > Import > Graphics, 1 unit = 1 mm).
All lengths are first guesses for a ~72 mm neck; re-run the NEC sweep before ordering.
"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
import ezdxf

# ---------------- geometry (mm) ----------------
W = 8.0                    # flex width
pull = 0.5                 # copper pull-back from the flex edge
board_l, board_w = 20.0, 17.0
# adjustment holes for the pinned cap (from the board edge; must match band_mould.py)
adj_s0, adj_n, adj_pitch, adj_hole = 74.5, 7, 5.0, 2.1
left_band = adj_s0 + (adj_n - 1)*adj_pitch + 18.0 - 2.0   # flex ends 2 mm short of the band's tail end
right_band = 51.0          # board edge -> pod lid (49 mm pod incl. taper)
into_flange = 6.0          # flex runs this far into the cap / pod-lid anchor flange
x_L = -left_band           # flex left end, 2 mm inside the band's tail
x_R = board_l + right_band + into_flange
arm_cu = 62.0              # antenna copper length from the board edge (tune with the NEC sweep / VNA)
bead_x = board_l + right_band - 8.0     # beads just before the pod: isolates pod + cell from the antenna
hole_d, hole_pitch = 1.8, 9.0
vbat_w, vbat_y = 1.2, 2.2               # VBAT trace (top layer) offset from the centreline
anchor_y = 2.5                          # matches the anchor holes in the cap / pod-lid flanges

# pads under the board (bottom side of the tracker PCB)
pads = [  # (name, x0, x1, y0, y1, layer)
    ("ANT",  0.6, 3.6, -2.5, 2.5, "TOP_CU"),
    ("MECH", 8.0, 10.0, -2.5, 2.5, "TOP_CU"),     # isolated, just holds the flex flat
    ("GND",  15.0, 19.4, -3.5, 0.6, "TOP_CU"),
    ("VBAT", 15.0, 19.4, 1.4, 3.3, "TOP_CU"),
]

rects, circles, lines = [], [], []    # (layer, ...) for the DXF + plot
def R(layer, x0, x1, y0, y1, label=None): rects.append((layer, x0, x1, y0, y1, label))
def C(layer, x, y, d): circles.append((layer, x, y, d))

R("EDGE", x_L, x_R, -W/2, W/2)
R("BOARD", 0, board_l, -board_w/2, board_w/2, "tracker PCB 17 x 20 (above flex)")
# antenna arm: solid copper, top layer, from the ANT pad out to arm_cu
R("TOP_CU", -arm_cu, 3.6, -W/2 + pull, W/2 - pull)
# counterpoise arm: GND bottom layer from under the board to the beads; VBAT trace on top
R("BOT_CU", 15.0, bead_x, -W/2 + pull, W/2 - pull)
R("TOP_CU", 15.0, bead_x, vbat_y - vbat_w/2, vbat_y + vbat_w/2)
# after the beads: plain narrow traces to the cell-lead pads at the pod flange
R("BOT_CU", bead_x + 2.0, x_R - into_flange - 3.0, -2.6, -1.2)               # GND to cell -
R("TOP_CU", bead_x + 2.0, x_R - into_flange - 3.0, vbat_y - 0.6, vbat_y + 0.6) # VBAT to cell +
R("TOP_CU", x_R - into_flange - 3.5, x_R - into_flange - 0.5, 0.9, 3.3, "BAT+")
R("TOP_CU", x_R - into_flange - 3.5, x_R - into_flange - 0.5, -3.3, -0.9, "BAT-")           # via to BOT_CU
for p in pads:
    R(p[5], p[1], p[2], p[3], p[4], p[0])
# parts on the flex (0402): cap before the beads, beads in GND and VBAT
parts = [("C 100p+100n (VBAT-GND)", bead_x - 3.0, 0.9), ("FB VBAT", bead_x + 1.0, vbat_y), ("FB GND", bead_x + 1.0, -1.9)]
# silicone key holes: centreline on the antenna arm, offset on the battery arm
x = -8.0
while x > -adj_s0 + 4:
    if abs(x + arm_cu) > 2.0:          # keep holes clear of the copper's end
        C("HOLES", x, 0.0, hole_d)
    x -= hole_pitch
x = board_l + 5.0
while x < bead_x - 5:
    C("HOLES", x, -1.2, hole_d); x += hole_pitch
# adjustment holes (cap pins bear on the polyimide here) + pod-lid flange anchors
for i in range(adj_n):
    C("HOLES", -(adj_s0 + i*adj_pitch), 0.0, adj_hole)
for y in (-anchor_y, anchor_y):
    C("HOLES", x_R - into_flange/2, y, 2.0)

# ---------------- DXF ----------------
doc = ezdxf.new(units=4)
msp = doc.modelspace()
for lay in ("EDGE", "TOP_CU", "BOT_CU", "HOLES", "BOARD", "PARTS"):
    doc.layers.add(lay)
for lay, x0, x1, y0, y1, _ in rects:
    msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": lay})
for lay, x, y, d in circles:
    msp.add_circle((x, y), d/2, dxfattribs={"layer": lay})
for name, x, y in parts:
    msp.add_lwpolyline([(x-0.5, y-0.25), (x+0.5, y-0.25), (x+0.5, y+0.25), (x-0.5, y+0.25)],
                       close=True, dxfattribs={"layer": "PARTS"})
doc.saveas("flex_strip.dxf")

# ---------------- drawing ----------------
col = {"EDGE": ("#f3e2b8", "#a07a2a"), "TOP_CU": ("#d9822b", "none"), "BOT_CU": ("#3f7fbf", "none"),
       "BOARD": ("none", "#2a7a2a")}
def draw(ax, x0, x1, detail):
    for lay, a, b, c, d, lab in rects:
        if lay not in col: continue
        fc, ec = col[lay]
        alpha = 0.55 if lay == "BOT_CU" else (0.85 if lay == "TOP_CU" else 1)
        ls = "--" if lay == "BOARD" else "-"
        ax.add_patch(Rectangle((a, c), b - a, d - c, fc=fc, ec=ec, lw=1.2 if lay in ("EDGE", "BOARD") else 0,
                               alpha=alpha, ls=ls, zorder={"EDGE": 1, "BOT_CU": 2, "TOP_CU": 3, "BOARD": 5}[lay]))
        if lab and detail and x0 <= (a+b)/2 <= x1 and lay != "BOARD":
            ax.text((a+b)/2, (c+d)/2, lab, ha="center", va="center", fontsize=7, zorder=9, color="black")
    for lay, x, y, d in circles:
        ax.add_patch(Circle((x, y), d/2, fc="white", ec="#555", lw=0.6, zorder=6))
    for name, x, y in parts:
        ax.add_patch(Rectangle((x-0.5, y-0.25), 1.0, 0.5, fc="#222", zorder=7))
        if detail: ax.annotate(name, (x, y), (x, y + 6.5 if "VBAT" in name else y - 6.8 if "GND" in name else y + 6.5),
                               fontsize=7, ha="center", arrowprops=dict(arrowstyle="-", lw=0.5))
    ax.set_xlim(x0, x1); ax.set_aspect("equal"); ax.set_yticks([])
    ax.spines[["left", "right", "top"]].set_visible(False)

fig = plt.figure(figsize=(14, 7.6))
ax1 = fig.add_axes([0.03, 0.66, 0.94, 0.28])
draw(ax1, x_L - 3, x_R + 3, False); ax1.set_ylim(-12, 12)
ax1.set_title(f"Collar flex, {x_R - x_L:.0f} x {W:.0f} mm (2-layer PI)   orange = top Cu, blue = bottom Cu, "
              "dashed green = tracker PCB above", fontsize=10)
def dim(ax, a, b, y, text):
    ax.annotate("", (a, y), (b, y), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text((a+b)/2, y + 0.8, text, ha="center", fontsize=8)
dim(ax1, -arm_cu, 0, 8.5, f"antenna arm copper {arm_cu:.0f} (tune)")
dim(ax1, x_L, -arm_cu, 8.5, f"bare tail {-x_L - arm_cu:.0f}")
dim(ax1, board_l, bead_x, 8.5, f"counterpoise: GND + VBAT, {bead_x - board_l:.0f} to beads")
dim(ax1, bead_x, x_R, -10.5, "to cell")
ax1.text(-(adj_s0 + 3*adj_pitch) - 12, -7.5, "adjustment holes: cap pins, 5 mm steps", fontsize=8); ax1.text(x_R - 18, 5, "pod-lid flange ←", fontsize=8)
ax1.set_xlabel("mm from the tracker board's left edge (along the band)", fontsize=8)

ax2 = fig.add_axes([0.03, 0.08, 0.52, 0.48])
draw(ax2, -8, 26, True); ax2.set_ylim(-9.5, 9.5)
ax2.set_title("Under the tracker board (board bottom side keeps these pad areas clear)", fontsize=9)
ax2.text(1.5, -9, "feed: ANT pad → matching network\nGND/VBAT: board ground + battery", fontsize=7)
ax3 = fig.add_axes([0.6, 0.08, 0.37, 0.48])
draw(ax3, bead_x - 8, x_R + 1, True); ax3.set_ylim(-9.5, 9.5)
ax3.set_title("Pod end: RF bypass, ferrite beads, cell-lead pads", fontsize=9)
fig.savefig("flex_strip.png", dpi=130)
print(f"flex {x_R - x_L:.1f} mm long; antenna Cu {arm_cu} mm; beads at {bead_x:.1f} mm "
      f"({bead_x - board_l:.0f} mm past the board)")
