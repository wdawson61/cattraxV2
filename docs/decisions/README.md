# Decision log

One line per decision, newest first. Add a separate file only when the reasoning won't fit in
the linked brief or check.

| Date | Decision | Where it's argued |
|---|---|---|
| 2026-11-12 | New repo (cattraxV2); cattrax.6 archived in the old repo | — |
| 2026-11-12 | Firmware on the nRF Connect SDK, as a freestanding application | `firmware/README.md` |
| 2026-11-12 | Breakaway sensor: TMAG3001A2 on the flex tip under the cell, own I2C bus, sensor lines choked at x ≈ 60–64 | `checks/2026-11-12-hall-sensor.md` |
| 2026-11-12 | v3 pod: bare curved cell cast straight into silicone; block-magnet clasp; screw-clamped cap | `mechanical.md` (v3) |
| 2026-11-12 | Cell: Grepow GRP751538 curved 440 mAh (first choice), cell protector IC on the flex | `checks/2026-11-12-cells.md`, `integration.md` §3–4 |
| 2026-11-12 | Proposed: nPM1300 VTERM 4.35 V for either Grepow cell | `checks/2026-11-12-cells.md` |
| 2026-11-11 | Full silicone overmould; pebble case with a bare PETG dock face | `mechanical.md` |
| 2026-11-10 | nPM1300 rails swapped: BUCK2 = 3V3_A (390 kΩ VSET2), BUCK1 = 3V3_RF (off at boot) | `checks/2026-11-10-power-and-io.md` |
| earlier | 6-layer 17 × 20 mm main board at JLC; antenna and counterpoise on the flex strip | `electrical.md`, `interface.md` |
