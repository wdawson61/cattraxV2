# Note to the electrical session (from the dock / power discussion, 2026-11-18 → 19)

Decisions made with the user in the dock discussion that the board brief (`docs/electrical.md`),
the pin table (`electrical/board/connections_nrf54l10.csv`) and `docs/interface.md` don't reflect
yet. Please fold them in.

## 1. Main rail is 1.8 V; 3.3 V only for the SX1262 PA (decided 2026-11-18)
- **1V8** (main): nRF54L10, MIA-M10Q (1.76–3.6 V; u-blox has 1.8 V reference designs), LIS2DW12,
  nPM1300 VDDIO, I2C pull-ups, TMUX1101s, **SX1262 VBAT_IO**.
- **3V3_RF**: SX1262 **VBAT only**, for full +22 dBm.
- **No level shifters:** the SX1262's VBAT_IO pin supplies all its digital I/O except DIO3, so its
  SPI, BUSY, DIO1, NRESET and DIO2 run at 1.8 V while VBAT is 3.3 V.
- Suggested buck mapping (fits the VSET limits in `checks/2026-11-10-power-and-io.md` §1):
  - **BUCK1 = 1V8, VSET1 = 47 kΩ** (PS Table 18: 47k → 1.8 V), up at power-on with no I2C.
  - **BUCK2 = 3V3_RF, VSET2 grounded** so it starts off; firmware sets 3.3 V over I2C and enables it
    before using the radio (as BUCK1 did in the 2026-11-10 swap). Verify VSET2 < 100 Ω = off.
  - Re-check erratum [30] (force PWM during TX) against whichever buck now feeds 3V3_RF.
- To verify in the SX1262 datasheet: VBAT_IO powered while VBAT is off (allowed? leakage?), any
  VBAT_IO ≤ VBAT rule, and power-up order. The old "keep SPI/NRESET low while 3V3_RF is off" note
  may no longer be needed, since the I/O domain stays powered.
- DIO2 drives the 915 MHz RF switch at 1.8 V. **Proposed switch: pSemi PE4259** (LCSC C470892,
  SC-70-6; JLC Economic and Standard assembly; check stock):
  - VDD 1.8–3.3 V: power it from **1V8**. Control high ≥ 0.7 × VDD (≈1.26 V at 1.8 V), so DIO2 at
    1.8 V drives it directly.
  - **Single-pin control mode** (pin 4 = CTRL from DIO2, pin 6 = VDD): no inverter, no MCU pin.
  - Input P1dB at 1 GHz, VDD 1.8–2.3 V: 29.5 dBm min / 30.5 typ, about 7 dB above the SX1262's
    +22 dBm. Insertion loss 0.35 dB, isolation 30 dB at 1 GHz.
  - **To check in the PE4259 datasheet (open):**
    1. **Port wiring:** the SX1262 drives DIO2 high during TX (`SetDio2AsRfSwitchCtrl`). Wire the
       PE4259 port that is selected when CTRL is high (single-pin truth table) to the TX path (RFO
       match), and the other port to the RX path (RFI_P/RFI_N balun).
    2. **DC-blocking caps:** whether the RF ports (RFC, RF1, RF2) need series DC blocks, and the
       values Semtech's 915 MHz reference design uses around the switch.
  - Smaller alternative: Skyworks SKY13351-378LF (LCSC C129189, DFN-6 1 × 1 mm, control 1.8–5 V,
    P1dB 30 dBm), but it needs complementary VC1/VC2 (DIO2 + inverter or an MCU pin) and isolation
    is about 24 dB.
- Bench debugging at 1.8 V: a probe that follows VTref (J-Link, or the nRF54L15 DK's J-Link OB via
  Debug out, 1.8–3.6 V targets). The Raspberry Pi debugprobe is 3.3 V only.

## 2. Dock contacts: VBUS, GND, UART TX, UART RX (decided 2026-11-18)
- Replaces SWDIO / SWCLK on the dock targets. A dock then needs only a cheap USB-UART, not a debug
  probe, and the outside contacts give no debug access.
- nRF54L10: **UARTE20 on P1.13 (TX) / P1.14 (RX)**. Not UARTE21, which shares its ID with SPIM21
  (SX1262 bus). These were the spare analog pins.
- TMUX1101s and TPD1E10B06s move to TX/RX; TMUX1101 VDD = 1V8. SEL divider unchanged (100k/150k;
  SEL is fail-safe to 5.5 V regardless of VDD).
- Updates over the dock: MCUboot serial recovery (wait-for-DFU window at boot; no extra pin).
  Field updates: BLE OTA (swap with revert, watchdog, confirm after a BLE self-test).
- **SWD moves to internal test pads** (SWDIO, SWCLK, RESET, 1V8, GND; bare pads or a Tag-Connect
  TC2030-NL footprint) for a pogo fixture before potting. Flash at manufacture, then enable access
  port protection. Keep the pads reachable on prototypes.
- `docs/interface.md` "Tracker case" line needs the new contact list (contract change; both sides).

## 3. Dock side
- `electrical/dock/README.md` and `docs/checks/2026-11-19-dock-usb-uart.md`: CH343P USB-UART with
  VIO = 1.8 V, 1 kΩ series resistors and delayed VIO to avoid back-powering the collar's 1V8 through
  the TMUX1101s while it wakes.
