# Breakaway Hall sensor: datasheet checks (2026-11-12)

Response to `claude/note_to_electrical_2026-11-12.md` (mechanical session). Part: TI
**TMAG3001A2YBGR**, checked against the TMAG3001 datasheet SLYS053C (Nov 2023, rev. May 2025),
`docs/tmag3001.pdf`. Flex rules are from JLCPCB's flex-PCB and PCBA capability pages (read
2026-11-12). "DS" means the datasheet; "inferred" means worked out from it, not stated in it.

**Summary.** The part fits electrically and mechanically, and a fixed threshold holds over
−10…45 °C with ≥3 mT margin (about 5 mT with the sensor's magnet tempco compensation on). Four things need action:
1. **The sensor lines must be RF-isolated where the counterpoise ends:** beads on VCC, SDA, SCL
   and INT at x ≈ 60–64, as well as on VBAT and GND.
2. **Put the sensor on its own I2C bus**, so damage to the band can't hang the PMIC/GNSS bus.
3. **The key-hole keep-in is tighter than the note says:** ±2.15 mm, not ±2.3.
4. **Two things to confirm with JLC before ordering:**
   - whether they'll place a WCSP on flex;
   - whether the longer strip is still within their size limit.

## 1. Package and land pattern

**Package (DS, YBG0006 drawing):**
- DSBGA-6, 2 × 3 balls, 0.4 mm pitch in both directions.
- Body 0.764–0.824 × 1.256–1.316 mm.
- **0.5 mm max height**, so the CAD's 0.5 is correct as a maximum. Ball height 0.14–0.20 mm,
  ball Ø 0.23–0.27 mm.
- Ballout (top view): A1 VCC, A2 ADDR, B1 INT, B2 GND, C1 SDA, C2 SCL.

**TI land pattern:** 6 × Ø0.23 mm pads, NSMD (preferred), mask opening ≤0.05 mm larger, so about
Ø0.33. Stencil 0.25 mm square, R0.05, for a 0.1 mm stencil.

**Against JLC flex rules:**
- **BGA pad Ø ≥ 0.25 mm on flex.** TI's 0.23 is below that, so use **0.25 mm pads**. TI notes
  that final dimensions may vary for manufacturing. That leaves 0.15 mm between pads.
- **BGA pad to trace ≥ 0.2 mm.**
  - Nothing can run between balls.
  - Every ball is on the perimeter (only 2 columns), so no via-in-pad is needed. Each ball's trace
    leaves straight outward: column 1 to −y, column 2 to +y.
  - With a 0.10 mm trace, the clearance to the neighbouring ball in the same column is
    0.4 − 0.125 − 0.05 = **0.225 mm**: OK.
- **Trace/space:** 3.5/3.5 mil on 18 µm copper. Use 0.10 mm traces.
- **Coverlay:** JLC's minimum coverlay bridge is 0.5 mm, so there's no web between these pads.
  - Use one gang window round all six pads, with traces necked to 0.10 mm inside it.
  - Opening-to-trace ≥ 0.15 mm applies outside the window.
  - Ask JLC whether LPI solder mask (rather than coverlay) is available in this local area; it
    would give per-pad openings.
- **Finish:** ENIG (JLC flex default), which suits WCSP.
- **Stiffener:** the note's 0.1 mm PI stiffener under x 109–115.5 is right. **Don't use stainless
  steel** there: JLC itself warns it is slightly magnetic and to keep it away from Hall sensors.

**Will JLC place a WCSP on flex?**
- JLC states they assemble FPCs, with a fixture fee of $23.57 per fixture. Their general fine-pitch
  limit is 0.35 mm (Standard), and 0.4 mm meets it.
- **They don't mention WCSP or BGA on flex specifically.** So this needs confirming with JLC
  support, or by setting "Confirm Production file" = Yes before paying.

**Fallbacks, best first:**
1. JLC assembles everything else on the flex, and we hand-place the TMAG3001: stencil or flux plus
   hot air on the PI-stiffened tip. It's doable but fiddly.
2. **TMAG5273A2 (SOT-23-6)** is too tall for the 0.34 mm of silicone over the flex under the cell.
   It would have to move to where the band is thicker, which is much farther from the clasp magnet.
   So it's a poor fallback.
3. No suitably small high-threshold Hall *switch* exists: the open-clasp field (~42 mT) is far
   above typical switch thresholds.

Stock: LCSC C31115089, TMAG3001A2YBGR, 4,624 in stock, $0.75 (1+) / $0.46 (1k+), checked
2026-11-12.

## 2. Range, sensitivity and axis (A2, ±120 mT)

DS §5.8, A2:

| Item | Value |
|---|---|
| Range | ±120 mT (X_Y_RANGE / Z_RANGE = 0) |
| Sensitivity | 273 LSB/mT in the 16-bit result |
| Sensitivity error | ±0.5 % typ, ±6 % max at 25 °C |
| Linearity error | ±0.1 % typ, 1.5 % max |
| Offset | ±75 µT typ, ±600 µT max |
| Offset drift | ±1 µT/°C typ, ±9.1 µT/°C max |
| RMS noise, 1×, LP_LN = 0 | X/Y 116 µT, Z 80 µT |
| RMS noise, 32× averaging | X/Y ~20 µT, Z ~14.5 µT |

Field at the sensor (mechanical model, open → closed):

| Component | Open | Closed | Step |
|---|---|---|---|
| X (along band) | 31 mT | 48 mT | 17 mT, +55 % |
| Z (radial) | 28 mT | 38 mT | 10 mT, +36 % |
| \|B\| (X, Z) | 42 mT | 61 mT | 19 mT |

All of these are well inside ±120 mT, and the ±240 mT range isn't needed. Noise (≤0.12 mT rms
at 1×) is negligible against the step.

**Use X.** It has the biggest single-axis step and the lowest current (a single-axis conversion).

**Orientation:**
- Lay the footprint out so the device X axis (DS Fig. 6-1) runs along the band.
- **Polarity matters.** The X/Y/Z threshold registers (THR_SEL = 2h) are *positive*-only 7-bit
  values, except in unipolar switch mode, where they are signed magnitude.
- DS: X reads positive for a **south** pole approaching (Y and Z positive for north).
- So either orient the magnet or footprint so closed-clasp X reads positive, or use unipolar switch
  mode with a signed threshold. Confirm the sign on the first prototype.

**Alternative:** the magnitude threshold (THR_SEL = 3h, |B| from the X and Z pair via ANGLE_EN = 3h).
- It's immune to the flex twisting in the band, which shifts field between X and Z.
- But it doubles the conversion energy.
- Keep it as a firmware option; it needs no hardware change.

## 3. Wake-up-and-sleep mode, interrupt and INT pin

**Current (DS §5.5), 1-channel conversion, LP_LN = 0, VCC = 3.3 V:**
- 0.5 µA typ / 1.3 µA max at a 5000 ms interval.
- 110 µA typ / 250 µA max at a 1 ms interval.
- Sleep 40 nA.

**At a 1 s interval (SLEEPTIME = 9h; inferred).** Fitting I = I_base + Q/T to those two points
gives about 0.11 µC per wake (typ):
- **≈0.6 µA typ, ≈1.5 µA max.**
- At 500 ms (SLEEPTIME = 8h): ≈0.7 / 1.75 µA.

Either is negligible against the 350 mAh budget. Keep Conv_AVG = 0h (1×, 50 µs conversion); more
averaging buys nothing here and costs energy.

**Recommended configuration (firmware; confirm on the bench):**

| Register | Setting | Meaning |
|---|---|---|
| Device_Config_1 | MAG_Tempco = 1h | 0.12 %/°C, NdFeB |
| Device_Config_1 | Conv_AVG = 0h | 1× averaging |
| Sensor_Config_1 | MAG_CH_EN = 1h, SLEEPTIME = 9h | X only, 1000 ms |
| Sensor_Config_2 | X_Y_Range = 0 | ±120 mT |
| Sensor_Config_3 | THR_SEL = 2h | B-field thresholds |
| THR_Config_1 | X_THR_LO ≈ midpoint, ~39.5 mT | |
| Device_Config_2 | THR_HYST = 5h | 64 LSB (12-bit) ≈ 3.75 mT, inferred |
| Device_Config_2 | Operating_Mode = 3h | W&S |

**Option A: unipolar switch mode (recommended).** INT_Mode = 5h.
- The device stays in W&S and INT simply follows the clasp state, with hysteresis.
- No I2C service is needed after an event, and it reports both open and close.
- DS: "If the device is configured as a switch and placed in a low power wake-up and sleep mode,
  the device remains in a low power wake-up and sleep mode in case if any interrupt event is
  detected."

**Option B: threshold interrupt.**
- Settings: INT_Mode = 1h, Threshold_INT = 1, INT_State = 0 (latched), MAG_THR_DIR = 1 (interrupt
  when the field falls *below* the threshold, i.e. clasp opened).
- After the MCU reads the part, it drops to standby, and firmware must re-arm W&S (DS §6.4.3).

**Threshold quantisation (inferred).**
- X_THR_LO/HI are 7-bit positive values. The DS doesn't state the LSB directly.
- Mapping to the top 7 bits of the 12-bit ±120 mT result gives ≈0.94 mT/LSB.
- THR_HYST steps are "LSB of threshold, 12 bit resolution", ≈0.059 mT each (2 to 256 LSB, about
  0.12 to 15 mT).
- **Verify both on the bench by sweeping a magnet.**

**INT pin:**
- DS: "The INT pin operates as an open drain output"; the pin table says a pull-up is needed for
  output use.
- *But* the switch-mode figures (DS Figs. 6-6, 6-7) label INT "Switch Mode – Push Pull". The DS
  contradicts itself here.
- **Fit an external pull-up either way, but a weak one: 470 kΩ–1 MΩ to 3V3_A**, and leave the
  nRF's ~13 kΩ internal pull-up off.
  - In switch mode INT sits at a level indefinitely, so a 13 kΩ pull-up would draw ~250 µA
    whenever INT is low.
  - With 1 MΩ, the worst case is 3.3 µA, and the edge rate is irrelevant for a level.
- **Pick the polarity so INT is released (high) in the normal, closed state** (INTB_POL plus
  INT_POL_EN, or MAG_THR_DIR). Then the pull-up only conducts after a breakaway.
- INT absolute max 7 V; VOL 0.4 V at 2 mA.

## 4. Supply, address, bus and pull-ups

**Supply:** VCC 1.65–3.6 V, so 3V3_A (BUCK2) is fine; I/O thresholds are 0.65/0.35 × VCC.
- Decoupling: TI asks for ≥0.01 µF close to the device. The note's 0201 at the sensor is right;
  use 100 nF.
- **Add ~47 Ω in series with VCC at the board end.** If the cat damages the band and VCC shorts
  on the flex, this limits the fault to ~70 mA instead of collapsing 3V3_A (MCU + GNSS).
- Active current is only ~2.4 mA for 50 µs, so the drop is negligible with the local cap.

**I2C address (DS Table 6-4):** ADDR to GND 0x34, VCC 0x35, SDA 0x36, SCL 0x37. Tie ADDR to GND
(0x34).
- It doesn't clash with the existing bus devices: LIS2DW12 0x18/0x19, MIA-M10Q 0x42,
  nPM1300 0x6B. Worth a quick look in each datasheet.
- **Don't use "interrupt through SCL"** (INT_Mode 3h/4h): TI says it can corrupt other devices'
  transactions on a shared bus.

**Recommendation: give it its own bus.** The sensor sits at the end of a ~105 mm line through
the band, the part of the collar most likely to be chewed, wetted or torn. A short there must
not hang the bus that talks to the PMIC, GNSS and accelerometer.
- Proposed pins, from the brief's spares:
  - **SDA P1.02, SCL P1.03** (both NFC pins, set as GPIO in UICR; P1.03 is clock-capable as SCL
    needs);
  - **INT P1.13** (P1 has GPIOTE).
- Use a TWIM instance other than 21, which SPIM21 already holds for the SX1262: TWIM20 or TWIM22.
  Confirm in the nRF54L PS.
- That uses the last P1 spares except P1.14. GNSS RESET_N/EXTINT stay on P1.11/P1.12.

**Pull-ups (inferred capacitance):**
- A 0.1 mm trace over a ground layer through 25 µm PI is ≈0.15–0.2 pF/mm, so ≈15–20 pF for
  ~105 mm.
- **On a dedicated bus** (~35 pF total), **4.7 kΩ** gives about 140 ns rise time: fine at
  400 kHz (300 ns limit).
- On the shared bus (≈70–80 pF), 4.7 kΩ gives ≈300 ns. That's marginal at 400 kHz, so use
  2.2 kΩ there or run at 100 kHz.
- Put the pull-ups on the tracker board.
- Run a GND trace between SDA and SCL along the flex to cut crosstalk, since past x = 63 there's
  no ground plane under them (see item 6).

## 5. Temperature: does a fixed threshold hold (−10…45 °C)?

**Inputs:**
- **Magnet:** N52 NdFeB, −0.12 %/°C. The v3 pod uses a K&J B842-N52 block, so it's N52. *The
  shared interface still says N42 discs; that line is stale.* N42 has about the same tempco.
- **Sensor sensitivity drift (DS):** −0.063…+0.042 %/°C below 25 °C, and −0.018…+0.072 %/°C
  from 25 to 85 °C.
- **Offset:** ±0.6 mT + ±9.1 µT/°C (max).

Worst case on X with **no** compensation (MAG_Tempco = 0), relative to the modelled 31/48 mT
at 25 °C:

| | −10 °C | 45 °C |
|---|---|---|
| Closed, minimum | 49.3 mT | **46.7 mT** |
| Open, maximum | **33.0 mT** | 30.7 mT |

Adding offset (≤0.9 mT including drift) and threshold quantisation (~0.5 mT):
- Worst open ≈ 34.4 mT, worst closed ≈ 45.3 mT.
- With the threshold at 39.5 mT and ±1.9 mT hysteresis (trip points ≈37.6/41.4 mT), **margin is
  ≈3.2 mT on the open side and ≈3.9 mT on the closed side.**
- MAG_Tempco = 1h cancels most of the magnet's drift, which widens both margins to ≈5 mT.

**So yes, a fixed threshold holds over −10…45 °C.** Temperature isn't the limiting factor:

- **Sensitivity error ±6 % (max, untrimmed).** Uncalibrated, this alone eats ~2.5 mT of each
  margin. **Calibrate at fitting**, as the note says: read X open and closed, then store the
  midpoint.
- **Real field versus the ideal-N52 model.** Grade tolerance, magnet position in the print and
  flex height in the cast can easily shift both levels by 10–20 %. Fitting calibration also
  covers this.
- **Ferromagnetic parts nearby.** The pouch cell's negative tab is usually nickel (magnetic), and
  the protection PCB sits beside it. They will bend the field a little: calibrate with the cell
  in place.
- Silicone creep moving the magnet relative to the sensor over time. Re-calibration can be done
  over BLE.

## 6. Points in the note I disagree with or can't route as drawn

1. **RF: the sensor lines extend the 915 MHz counterpoise.** This is the main issue.
   - The power arm is the dipole's second half. Its GND ends at x = 63, with beads in VBAT and GND
     at x ≈ 60–64 to stop it there.
   - Five sensor conductors running on to x = 115.5 would lengthen the counterpoise by ~50 mm
     and detune the antenna.
   - **Fix (confirmed with the user 2026-11-12):** isolate every sensor line at x ≈ 60–64,
     beside the existing VBAT/GND beads.
     - Ferrite beads (the same high-Z-at-915 MHz part) on **VCC, SDA and SCL**. Not resistors on
       SDA/SCL: a 1 kΩ series resistor with the 4.7 kΩ pull-ups lifts VOL to ≈1 V, too near the
       nRF's VIL, and a smaller one isolates poorly.
     - A **≈10 kΩ series resistor on INT**, which is enough with the 1 MΩ pull-up.
     - The sensor's GND comes from the battery side of the existing GND bead.
   - That's 3 extra 0402 beads and one resistor; they fit across 8 mm. Bead DCR and inductance are
     harmless at I2C speeds.
   - Reason: the power arm is the dipole's second half, not a ground plane (the 17 × 20 mm
     board is far too small to act as one at 915 MHz). Without isolation the lines would nearly
     double that arm's length.
   - Re-run the NEC sweep / VNA check with the lines present.
2. **Key-hole keep-in:** Ø1.5 holes at y = ±3.1 put the hole edges at ±2.35 mm.
   - JLC needs **≥0.20 mm from NPTH to copper**, so **copper must stay within ±2.15 mm**
     (trace edges, GND pour included), not ±2.3.
   - The outer edge of each hole is at ±3.85, leaving only **0.15 mm of PI to the flex edge**.
     That's fragile, and probably below JLC's hole-to-outline minimum. Suggest y = ±2.9 (0.35 mm
     web) and copper within ±1.95, or Ø1.2 holes.
   - Five lines at 0.1/0.15 mm still fit easily within ±1.95.
3. **Anchor holes at x = 74, y = ±2.5, Ø2:** the sensor lines have to pass between them.
   - With 0.2 mm clearance, copper must stay within **±1.3 mm** from x ≈ 72.8 to 75.2.
   - Four 0.1 mm lines plus a GND trace fit in 2.6 mm.
   - They also have to get past the BAT+/BAT− pads at x = 67.5–70.5. **I need the pad geometry**
     (which layer, what width) to confirm a route; the lines can go on the side opposite the VBAT
     run.
4. **Flex length / JLC size limit.**
   - If the antenna end is still at x = −120.5, ending at x = 115.5 makes the strip **236 mm**.
     That's over JLC's regular flex maximum of 234 mm; up to 250 mm needs edge rails and
     confirmation from support.
   - The note also mentions "the full 175 mm strip", which doesn't match either figure. Please
     confirm the new strip extent and update the shared interface.
5. **Dive x 76–88 (h 1.6 → 0.35):** fine. Keep it free of pads, vias and stiffener, with traces
   running straight through it; RA copper helps.
6. **Stiffeners:**
   - Hole zone, 0.2 mm PI: fine.
   - Sensor tip, 0.1 mm PI: fine and recommended for WCSP assembly.
   - Both must be PI (or FR4), never stainless near the sensor.
   - Note that JLC lists FR4 stiffeners as chipping easily.
7. **RA copper:** JLC's flex capability page doesn't list an RA/ED choice. Ask support whether RA
   is available, and at what cost, before relying on it.
8. **No components or stiffener between x 88 and 108:** agreed; nothing electrical needs to be
   there.

## Changes to make in the electrical files (pending)
- Add U-sensor (TMAG3001A2YBGR), C (100 nF 0201), R (47 Ω, series VCC), R (1 MΩ INT pull-up) and
  4.7 kΩ pull-ups on the dedicated bus.
- Add 3 more ferrite beads (VCC, SDA, SCL) and a ≈10 kΩ INT series resistor at x ≈ 60–64.
- Pins: SDA P1.02, SCL P1.03, INT P1.13; TWIM20 or TWIM22.
- Shared interface: magnet grade N52 (B842), new strip extent, key-hole y and keep-in, and the
  anchor-hole keep-in.
