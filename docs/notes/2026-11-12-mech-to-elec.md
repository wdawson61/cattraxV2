# Note to the electrical session (from the mechanical session, 2026-11-12)

> **Update (rev 3, after `claude/hall_sensor_datasheet_checks_2026-11-12.md`):** the flex section
> of `hardware/respin/handoff_shared_interface.md` now holds the agreed numbers and supersedes
> this note where they differ. Changes: key holes Ø1.2 at y ±2.9 (copper within ±2.1); dive moved
> to x 81–91; battery tab pads at x 76.5–79.5 with the flex widened to 11 mm there; pod-lid anchor
> holes dropped (no lid in v3); strip now x −107.5 … +115.5 = 223 mm; tail holes at x −75.2 …
> −105.2; sensor lines choked with beads at x ≈ 60–64 as you proposed. `flex_strip.py` is not yet
> updated.

Flex requirements coming out of the v3 clasp/cap work (`hardware/respin/cad_v3_pod/cap_screw.py`,
`cap_screw_sections.png`) and the breakaway sensor concept (`sensor_h.py`,
`hall_sensor_sections.png`). The flex layout, parts and fab order are yours; these are the
mechanical asks.

## Band tail (adjustment zone, the free end that goes into the cap)
- **Holes:** Ø1.8 mm (was Ø2.1) at 5 mm pitch, on the band centreline. M1.6 countersunk screws
  pass through them and clamp the tail inside the cap. The hole zone is bare flex (as in the
  brief): keep the antenna and any other copper out of it, since it gets cut to length at fitting.
- **Stiffener:** 0.2 mm polyimide stiffener over the whole hole zone, on one side. The screws bear
  on the hole edges until the magnet breakaway lets go, so the edges need the reinforcement.
  JLCPCB naming is `pit_*` (top) or `pib_*` (bottom). For KiCad, draw it on a spare user layer,
  export it as its own Gerber, describe it in the order remarks, and set "Confirm Production
  file" to Yes (JLCPCB reviews non-EasyEDA stiffener layers by hand).
- Stiffen locally; the rest of the strip can stay on the thinner build so the band stays supple.

## Breakaway sensor (concept, no branch)
- **Part:** TI TMAG3001A2 (3D linear Hall, I2C, DSBGA-6 0.83 × 1.32 mm, 0.5 mm max, ±120/±240 mT,
  0.45 µA wake-up-and-sleep with threshold interrupt). LCSC C31115089.
- **Flex:** the main 8 mm flex continues past the battery tab pads, dives from h 1.6 to h 0.35
  between x 81 and 91, runs under the cell and ends at x ≈ 115.5. The sensor and a 0201 decoupling
  cap sit on its end, at band x 113.5 (~7 mm behind the pod magnet's back face).
- **Stiffener:** 0.1 mm PI under the end, x 109 to 115.5, for tip handling and a flat mount.
- **Key holes:** Ø1.2 at y ±2.9, x 95, 100, 105, so the silicone locks through the flex. Copper
  within ±2.1 there.
- **Lines:** VCC, GND, SDA, SCL, INT back along the band to the tracker PCB, alongside the
  battery lines, choked at x ≈ 60–64.
- **Field (modelled, ideal N52):** clasp open ~42 mT, closed ~61 mT at the sensor; largest single
  component ~48 mT (X, along the band). Use the ±120 mT range; calibrate the threshold at fitting.
- Thinnest point is under the cell middle (0.34 mm silicone above the flex, 0.35 below): no
  components or stiffener between x ≈ 91 and 108.

## Whole strip
- **Copper:** prefer Rolled Annealed over Electro-deposited, if JLC offers it. The collar flexes
  constantly, and RA copes with repeated bending much better.

## Position
- Inside the cap the tail now sits 0.7 mm higher than before (on a 1.5 mm base plate), with the
  flex still 1.6 mm above the tail's underside. Nothing changes outside the cap.
