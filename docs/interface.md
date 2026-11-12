# Cat collar tracker – shared interface (mechanical ⇄ electrical)

Both sessions treat these as fixed. If one changes, update this section in both briefs.
All lengths are in mm. "x" is measured along the band from the tracker board's left edge;
negative x is the antenna side.

## Fit
- Design neck size is 226 mm circumference, the 72 mm saline-bottle phantom. The tracker sits on
  top of the neck, the clasp at the bottom.
- The adjustable cap gives 6 settings over 25 mm, about −10 / +15 mm around the design size
  (circumference 216 … 241 in 5 mm steps).

## Tracker board
- 17 × 20 mm, with the 20 mm side along the band. Six layers (JLC06161H-3313, 1.6 mm nominal, ≈1.54 mm built;
  0.1 mm L1–L2 prepreg to match Nordic's reference), parts on both sides (JLC Standard PCBA). It was 15 mm wide before the dock targets moved onto the board.
- The underside keeps an 8 mm-wide strip, centred across the board, free of parts. Parts go only in
  the 4.5 mm strips either side of it.
- **Dock contacts:** four SMT gold targets on the underside, two in each side strip, with an
  asymmetric (keyed) pattern. They are about 3.2 mm in diameter and 3 mm tall; the case floor is
  set so they finish flush with the outside of the case.
- Flex pads on the board underside:
  | Pad | x range | y range |
  |---|---|---|
  | ANT | 0.6–3.6 | −2.5 … +2.5 |
  | MECH (isolated) | 8.0–10.0 | −2.5 … +2.5 |
  | GND | 15.0–19.4 | −3.5 … +0.6 |
  | VBAT | 15.0–19.4 | +1.4 … +3.3 |

## Flex strip (one continuous 2-layer polyimide strip, JLC, adhesive-less PI)
(Updated 2026-11-12 by the mechanical session for the v3 pod, screw cap and breakaway sensor;
see `claude/note_to_electrical_2026-11-12.md` and `claude/hall_sensor_datasheet_checks_2026-11-12.md`.)
- **223 × 8 mm, running from x = −107.5 to +115.5** (was 197.5, −120.5 … +77.0). JLC's regular
  flex limit is 234 mm. Widened locally to 11 mm at the battery tab pads (below). It passes under
  the board and is soldered to the pads above.
- **Antenna arm** (x < 0):
  - Top-layer copper from the ANT pad out to x = −62. This length is a first guess, to be tuned.
  - Bare flex beyond that.
  - Silicone key holes, Ø1.8 mm on the centreline at 9 mm pitch, between the board and x = −62.
- **Adjustment holes (tail):** 7 holes, **Ø1.8 mm**, at **x = −75.2 … −105.2** (5 mm pitch), on the
  centreline. Two M1.6 countersunk screws in the cap pass through an adjacent pair; the tail-tip
  hole of the pair sets the size (−90.2 = 226 mm design size; −80.2 … −105.2 = 216 … 241). The tail
  is trimmed 1.8 mm past that hole at fitting, so the strip ends at −107.5 (the last possible trim
  line plus 0.7). The silicone band has matching holes; the mould cores pass through these flex
  holes, which locates the flex.
  - **0.2 mm PI stiffener** over x = −73.5 … −107.5 (one side). PI or FR4 only, never stainless.
  - No copper in the hole zone: it is cut to length at fitting.
- **Counterpoise / power arm** (x > 20):
  - GND on the bottom layer across the full width, out to x = 63.
  - VBAT on the top layer, 1.2 mm wide, at y = +2.2.
  - At x ≈ 60–64: a VBAT–GND bypass cap, then a ferrite bead in each line: VBAT, GND, and the four
    sensor lines (VCC, SDA, SCL, INT). These beads end the counterpoise at ≈63; everything past them
    must be choked.
  - **Cell protector** (integration note §4) between the beads and the tab pads, x ≈ 65–74, parts
    ≤ 1.2 mm tall.
  - **Battery tab pads** at x ≈ 76.5–79.5, centred at y ≈ ±3.75 (GRP751538 tabs 2.0 wide, ~7.5 ±1
    apart; tab length still to be confirmed by Grepow). The flex widens to 11 mm over x = 75.5–80.5
    for them.
  - ~~Anchor holes, Ø2 mm, at x = 74, y = ±2.5~~ — dropped: the v3 pod has no lid flange.
- **Pod section** (x 80.5 → 115.5, new; carries only the breakaway-sensor lines):
  - Dives from 1.6 mm to 0.35 mm above the neck over x = 81–91 (no pads, vias or stiffener there),
    then runs under the cast-in cell.
  - Silicone key holes Ø1.2 mm at y = ±2.9, x = 95, 100, 105. Copper within ±2.1 there.
  - No parts or stiffener over x ≈ 91–108 (0.34 mm of silicone over the flex at the cell middle).
  - **Breakaway sensor** TMAG3001A2 (DSBGA-6, 0.5 mm max) + 100 nF 0201 at x = 113.5, on a 0.1 mm
    PI stiffener over x = 109–115.5.
- **Planned additions, not yet drawn:**
  - plated 0.5–0.6 mm holes in each flex pad, for soldering through the flex (4–6 in GND);
  - two 0.8 mm non-plated alignment holes, matched by holes in the board.
- Source: `flex_strip.py` produces `flex_strip.png` and `flex_strip.dxf` (layers EDGE, TOP_CU,
  BOT_CU, HOLES, BOARD, PARTS; 1 unit = 1 mm). **Not yet updated for the changes above.**
  Mechanical model of the pod section: `cad_v3_pod/sensor_h.py`.

## Band
- 12 × 3.6 mm, platinum-cure silicone (Dragon Skin 20 class, skin safe).
- The flex sits 1.6 mm from the neck face, with 2.0 mm of silicone outside it (except in the pod,
  above).
- The neck faces of the band, pod, lip and cap are all flush.

## Pod (battery, right-hand / counterpoise side) and clasp
(v3 concept, 2026-11-12: `cad_v3_pod/`. The cell choice itself is open: see the integration note §3.)
- **Cell:** designed around the Grepow GRP751538 (440 mAh, 15 × 38.1 arc × 6.94 mm, 7.50 swollen,
  pre-curved R52.4), bare, Kapton-wrapped and cast straight into the silicone. Lid end + leads at
  x = 80, cell to ≈118.9.
- **Pod:** silicone only, 0.8 mm skin round the cell. About 16.7 wide; height over the neck 8.6 mid,
  ~9.7 at the cell ends, 10.7 at the clasp face (x = 124.3).
- **Clasp magnets:** one K&J B842-N52 block (12.7 × 6.35 × 3.18, magnetised through the 3.18) each
  side: in a printed PETG insert in the pod, and in the cap. ~0.8 mm magnet-to-magnet gap. Release
  force to be measured (target about 1–2 kg).
- **Cap:** 20 mm long, PETG shell + 1.5 mm base plate, clamped by two M1.6 × 8 countersunk screws
  (from the neck side) into flush M1.6 nuts, at 11.3 and 16.3 mm from the clasp face (x = 135.8 and
  140.8 in the pod frame). Replaceable without touching the pod.
- **Breakaway sensor:** see the flex pod section. Modelled field at the sensor: clasp open ~42 mT,
  closed ~61 mT.
- **Clearance:** at the smallest setting, the antenna copper end is about 26 mm from the cap
  magnet and 13 mm from the nearer screw.

## Tracker case
- Sealed and potted. Four dock contacts: VBUS, GND, SWDIO, SWCLK (nRF54L10).
  They are the board-mounted targets, on the neck side.
- About 2 mm wider than before, to fit the 17 mm board.
- The flex passes through the case and the potting covers the solder joints, which is the strain
  relief.
