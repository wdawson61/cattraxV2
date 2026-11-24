# Decision log

One line per decision, newest first. Add a separate file only when the reasoning won't fit in
the linked brief or check.

| Date | Decision | Where it's argued |
|---|---|---|
| 2026-11-23 | RF switch PE4259 (LCSC C470892) in single-pin mode: VDD = LR_VIO, CTRL = DIO2 via 1 kΩ; replaces SKY13323 + LV1T34/LV1T04 (supersedes 2026-11-20 §5) | `checks/2026-11-20-power-rails.md` §5 (update) |
| 2026-11-20 | Keep the nPM1300 (nPM1304 not stocked at LCSC; BQ25190 and MAX77654 rejected) | `checks/2026-11-20-power-rails.md` §1 |
| 2026-11-20 | GNSS on its own TPS62840 1.8 V buck from VSYS, EN = GNSS_EN + 1 MΩ pull-down; replaces the TPS7A20 LDO | `checks/2026-11-20-power-rails.md` §2 |
| 2026-11-20 | SX1262 VBAT_IO via nPM1300 LOADSW1 (off at power-on, enabled by firmware) so VBAT_IO ≤ VBAT always | `checks/2026-11-20-power-rails.md` §3 |
| 2026-11-20 | Main rail stays 1.8 V nominal; 1.9 V over I2C is an acceptable fallback | `checks/2026-11-20-power-rails.md` §4 |
| 2026-11-20 | ~~RF switch SKY13323-378LF, driven by SN74LV1T34 (TX) + SN74LV1T04 (RX) at 3.3 V from DIO2~~ (superseded 2026-11-23) | `checks/2026-11-20-power-rails.md` §5 |
| 2026-11-19 | Dock USB-UART: WCH CH343P, VIO = 1.8 V from an LDO, core from USB 5 V | `checks/2026-11-19-dock-usb-uart.md`, `electrical/dock/README.md` |
| 2026-11-18 | Dock contacts VBUS, GND, UART TX/RX (MCUboot serial recovery); SWD only on internal test pads | `notes/2026-11-19-dock-to-elec.md` §2 |
| 2026-11-18 | Main rail 1.8 V (SX1262 VBAT_IO on it); 3.3 V rail for the SX1262 VBAT only; no level shifters | `notes/2026-11-19-dock-to-elec.md` §1 |
| 2026-11-12 | New repo (cattraxV2); cattrax.6 archived in the old repo | — |
| 2026-11-12 | Firmware on the nRF Connect SDK, as a freestanding application | `firmware/README.md` |
| 2026-11-12 | Breakaway sensor: TMAG3001A2 on the flex tip under the cell, own I2C bus, sensor lines choked at x ≈ 60–64 | `checks/2026-11-12-hall-sensor.md` |
| 2026-11-12 | v3 pod: bare curved cell cast straight into silicone; block-magnet clasp; screw-clamped cap | `mechanical.md` (v3) |
| 2026-11-12 | Cell: Grepow GRP751538 curved 440 mAh (first choice), cell protector IC on the flex | `checks/2026-11-12-cells.md`, `integration.md` §3–4 |
| 2026-11-12 | Proposed: nPM1300 VTERM 4.35 V for either Grepow cell | `checks/2026-11-12-cells.md` |
| 2026-11-11 | Full silicone overmould; pebble case with a bare PETG dock face | `mechanical.md` |
| 2026-11-10 | nPM1300 rails swapped: BUCK2 = 3V3_A (390 kΩ VSET2), BUCK1 = 3V3_RF (off at boot) | `checks/2026-11-10-power-and-io.md` |
| earlier | 6-layer 17 × 20 mm main board at JLC; antenna and counterpoise on the flex strip | `electrical.md`, `interface.md` |
