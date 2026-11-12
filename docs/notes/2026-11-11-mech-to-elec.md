# Note to the electrical session (from the mechanical session, 2026-11-11)

The mechanical session applied the pending items from `claude/electrical_datasheet_checks_2026-11-10.md`
to the electrical files. Please review; they are yours from here.

## Changed in `hardware/respin/`
- **`handoff_electrical.md`, power tree:**
  - New bullet recording why the rails were swapped. VSET1 tops out at 2.7 V by resistor; VSET2
    reaches 3.3 V.
  - **BUCK2 = 3V3_A**, VSET2 = 390 kΩ 1 %. It feeds the nRF54L10, LIS2DW12, MIA-M10Q, the
    TMUX1101s, VDDIO and the pull-ups.
  - **BUCK1 = 3V3_RF**, SX1262 only. VSET1 goes to GND, so BUCK1 starts off; firmware sets 3.3 V
    over I2C and enables it. Three sub-notes:
    - Hold the SX1262 SPI/NSS/NRESET lines low or hi-Z while the rail is off.
    - Force PWM during TX (erratum [30]).
    - About −0.5 dB at the buck's −5 % tolerance, and more once the cell is below ~3.4 V.
- **`connections_draft_nrf54l10.csv`:** the 3V3_A and 3V3_RF rows swap VOUT1/SW1 and VOUT2/SW2.
  The VSET1 row is now GND (<100 Ω); the VSET2 row is 390k 1 %.
- **`collar_mockup.zip`:** its copies of `handoff_electrical.md` and the CSV were refreshed to match.

## Not changed, still open for you
- Line ~115 of `handoff_electrical.md` (via-in-pad on B6 VOUT1 / C6 VOUT2) mentions both buck
  outputs, so it isn't affected by the swap, but check it if the WLCSP is still under consideration.
- Item 4 of the datasheet checks: SWD series resistors and probe VTref wait. That's a dock/probe item.
- Datasheet PDFs are still not in `hardware/datasheets/`.

## Mechanical changes that touch the shared interface
- Pod line in `handoff_shared_interface.md`: now computed for the 802025 cell, ≈44.3 mm long
  including the taper (body ≈32.3 mm), 22.9 wide, 11.2 thick. These are the same outer numbers as
  before; only the wording and source changed. Nothing changes for the flex or the board.
