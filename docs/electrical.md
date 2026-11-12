# Handoff brief – cat collar tracker: PCB electrical and layout

Context for a new session. Attach `handoff_shared_interface.md`, and `collar_mockup.zip` for
`flex_strip.py`. The shared interface holds the board outline, the flex pad positions and the flex
geometry; this brief adds the electrical decisions and open work.

## Project
- A LoRa + GPS cat tracker for a 26-acre property. The gateway is a RAK7289V2 on TTN.
- This is a respin of the KiCad board "cattrax.6", fabbed and assembled at JLCPCB.
- The current board uses a Murata 1SJ (SX1262 + STM32L0); the 1SJ-295 has no stock until 11/2027.
  It also has a MIA-M10Q GNSS with an ACAG0301-1575 chip antenna, a BQ21088 charger, a TPS631000
  buck-boost and a LIS2DE12 accelerometer. It is 27.5 × 21.4 mm, 4 layers.
- Goals: range never worse than today, minimum board size, lower cost, a battery pod on the band,
  and a pogo dock.
- Preference: always check the relevant datasheets and design docs, and ask for help finding them
  if needed.
- Radio certification is not a factor.

## Decisions made
- **MCU + radio:**
  - MCU is now the nRF54L10 (see the topology section; the ESP32-H2 was dropped).
  - LoRa stays at 915 MHz only; 2.4 GHz LoRa would lose about 26 dB of uplink budget.
  - **LoRa radio: SX1262IMLTRT (LCSC C191341), replacing the LR1121 (2026-11-10).**
    - With 915 MHz only on TTN, the LR1121's extras (2.4 GHz LoRa, S/L-band satellite,
      LR-FHSS on more bands, Sigfox) go unused.
    - SX1262: QFN-24 4 × 4 mm (LR1121 is QFN32 5 × 5), about $2.79 vs $4.22, RX about 4.6 mA
      vs about 5.7 mA, the same +22 dBm TX, mature Zephyr / LoRaMac-node / LoRa Basics Modem
      drivers, and the same die as today's Murata 1SJ, so current range and settings carry over.
    - What we give up: the LR1121's quoted receive sensitivity is a few dB better (−141 vs
      −137 dBm at SF12/BW125; one bench test showed about 1.5 dB). That only helps downlinks
      (join-accept, ADR, acks); uplink range, which sets tracking range, is unchanged.
    - LR2021 (4th-gen LoRa Plus) noted for a later revision: similar sensitivity, 105 mA at
      +22 dBm, but new and sold in 3000-piece reels; check JLC stock before considering it.
- **BLE (nRF54L10, Bluetooth LE 6.0):** provisioning, OTA updates (MCUboot), and close-range
  location. All of the options below work with the single 2.4 GHz chip antenna; none needs an
  antenna array on the collar.
  - **Channel Sounding (BLE 6.0 distance ranging): supported and production-ready.** nRF Connect
    SDK v3.0.1 qualified the host and controller for Channel Sounding and added production Reflector
    and Initiator samples (IFFT ranging).
    - The collar would be the Reflector; the Initiator is a phone with Channel Sounding (Android 16
      class) or a fixed nRF54L receiver around the house or barn. Gives distance, not direction.
    - Needs an encrypted (paired) connection, so it can't run from advertising alone. Use it on
      demand ("find the cat" mode), not continuously, because of the battery.
  - **Direction finding (AoA/AoD, BLE 5.1):** the nRF54L supports only the AoA *transmitter* role
    (the collar sends a Constant Tone Extension). The locator needs an antenna array, and Nordic's
    locator samples don't run on the nRF54L, so a fixed locator would be an nRF52833 + array.
    No AoD and no receiver role on the nRF54L.
  - **RSSI** to fixed receivers still works as a coarse fallback.
  - **Ecosystems:** the nRF Connect SDK also supports Google Find Hub and Apple Find My (Find My
    needs Apple's network accessory program). Worth a look for "near a phone" finding.
  - Firmware-only decisions: none of these change the schematic beyond the existing 2.4 GHz path.
- **915 MHz antenna:** a dipole built into the flex.
  - The antenna arm is one half: top copper, 62 mm from the board edge. This is a first guess.
  - The GND + VBAT power arm is the other half. A bypass cap plus ferrite beads at about 43 mm past
    the board isolate the pod and cell.
  - Feed is at the ANT pad (L6), through one filled, capped via in the pad (free on 6 layers;
    flat, so no wicking when the flex is hand-soldered), with clearance holes in L2–L5 and
    ringed with ground vias. The matching network sits on top, directly above.
  - No coax and no U.FL.
- **Board stack: 6 layers, JLC06161H-3313, 1.6 mm (decided 2026-11-11; replaces 4 layers).**
  The price over 4-layer + paid via-in-pad was marginal, and 6 layers makes via-in-pad free.
  - **Nordic reference stack-up** (from the v0.8 PcbDoc, 4-layer): 35 µm Cu / 0.1 mm prepreg
    (εr 4.3) / 35 µm Cu / 1.2 mm core (εr 4.6) / 35 µm Cu / 0.1 mm prepreg / 35 µm Cu, ≈1.6 mm.
  - **JLC 6-layer 1.6 mm stackups, priced on JLC's quote page (2026-11-11; 17 × 20 mm, 5 pcs,
    1 oz outer / 0.5 oz inner, epoxy-filled & capped vias):** base 6-layer special offer $32.00.
    | Stackup | L1–L2 dielectric | Stackup fee |
    |---|---|---|
    | **JLC06161H-3313** | 3313, 0.0994 mm, εr 4.1 | **$0 (default-priced)** |
    | JLC06161H-7628 | 7628, 0.2104 mm, εr 4.4 | $0 |
    | JLC06161H-1080 | 1080, 0.0764 mm, εr 3.91 | +$33.08 |
    | -2116C, -3313D, -7628B, -7628D | various | +$66.19 |
    | -1080A/B/C, -2116, -2116A/B, -3313A/B/C/E, -7628A | various | +$99.33 |
  - **Chosen: JLC06161H-3313.** Build: Cu 35 µm / 3313 0.0994 / L2 / core 0.55 / L3 /
    2116 0.1088 / L4 / core 0.55 / L5 / 3313 0.0994 / Cu 35 µm (inner Cu 15.2 µm), ≈1.54 mm.
    - L1–L2 is 0.0994 mm at εr 4.1, almost exactly Nordic's 0.1 mm L1–L2, so the 2.4 GHz match
      and RF trace geometry carry over. L1 to L6 is ≈1.44 mm, the same as Nordic's L1-to-bottom,
      so the cut-out region (see 2.4 GHz layout) references the bottom at the same height.
    - 50 Ω microstrip on L1 over L2: ≈0.16 mm without solder mask (Hammerstad-Jensen,
      t = 35 µm); ≈0.17–0.18 mm with mask. Confirm in JLC's impedance calculator for this stack.
    - Rejected: -7628 (free, but 0.21 mm L1–L2 doubles trace widths to ≈0.36 mm and departs from
      Nordic's geometry); -1080 (0.076 mm, ≈0.12 mm lines, +$33, no benefit); the rest cost
      $66–$99 extra.
  - **Layer use (pairs are tightly coupled: L1/L2, L3/L4 and L5/L6 are 0.1 mm apart):**
    - L1: parts, RF, antennas, ground pour.
    - L2: solid ground (reference for all L1 RF and power loops).
    - L3: signal routes (SPI, I2C, IRQs, SWD), ground-poured elsewhere.
    - L4: power pours (3V3_A, 3V3_RF, VBAT), ground-poured elsewhere.
    - L5: solid ground.
    - L6 (bottom): flex pads, dock targets, small parts, ground pour.
    - Stitch all ground layers together densely, especially round the match and board edges.
  - **Via-in-pad (free on 6 layers, epoxy-filled & capped is JLC's 6-layer default):** use it
    where it helps.
    - nRF54L10 centre pad: Nordic's 4 × 4 via array, filled and capped.
    - ANT feed: the via can now go in the ANT pad; a capped via is flat, so it won't wick when
      the flex is hand-soldered.
    - nPM1300: **WLCSP preferred** (see below); check JLC/LCSC stock for nPM1300-CAAA first.
  - **nPM1300 WLCSP note (2026-11-11):** now preferred, since via-in-pad is free on 6 layers. JLC can place it. Standard PCBA goes down to 0.35 mm
    BGA pitch, and the WLCSP's pitch is 0.419 mm (columns) × 0.44 mm (rows), ball Ø
    0.195–0.255 mm (nPM1300 PS Table 38). The limit is routing, not assembly: with JLC
    minimums (0.25 mm BGA pad, 0.15/0.25 mm via, ~0.09 mm space), a diagonal dog-bone via
    clears the ball pads by only ~0.05–0.07 mm, and the 0.17–0.22 mm gap between pads can't
    hold a trace plus two clearances (~0.27 mm). So every interior ball (up to 3 × 5
    of the 5 × 7 array) needs filled, capped via-in-pad, which is free on 6 layers. Saves about
    18 mm² (QFN 25 mm² vs WLCSP about 7.3 mm²).
  - **WLCSP interior balls (B2–D6) checked against PS Table 36 (2026-11-11):**
    - Joined on top copper to their outer twin, no via: B2 VBUS (to B1), C2 VSYS (to C1),
      D2 VBAT (to D1).
    - Unused, left open: B3 CC2, D5 CC1 (Nordic: may float or go to GND); C4 GPIO3, C5 GPIO2,
      D6 GPIO0. Use **GPIO1 (E6, outer row) as the PMIC interrupt to the MCU**; drop the
      PMIC-to-nRESET line (the PMIC watchdog / failed-boot recovery power-cycles the rails,
      which resets the MCU anyway).
    - Unused, to GND: B4 LSIN1 and B5 LSIN2 (Nordic: unused LSIN/LSOUT to GND). Tie them on top to
      A4/A5 (LSOUT, also GND) and take the ground out along row A. No via. This drops the
      optional GNSS load switch; power GNSS from 3V3_A directly.
    - **Need filled, capped via-in-pad:** B6 VOUT1 and C6 VOUT2 (both required). Possibly
      D3 NTC (if it must be grounded or biased with no thermistor), C3 VBUSOUT (a Nordic engineer
      says it needs a 1 µF cap even if unused; reference config 3 lists it as not used), and
      D4 SHPHLD (only if magnet wake is fitted). Confirm NTC and VBUSOUT handling in the PS.
    - So the WLCSP needs 2–5 via-in-pads; Nordic's layout guide recommends capped vias for
      WLCSP via-in-pad.
  - (Superseded 2026-11-11: the earlier "no paid via-in-pad" plan for 4 layers.)
- **2.4 GHz layout (nRF54L10):** copy Nordic's nRF54L15-QFAA reference layout v0.8 (config 1,
  4-layer; applies to L15/L10/L05) around U1 as closely as possible. Circuit is in the topology
  section. From its schematic notes and Gerber-level layer views:
  - Matching network as close to the IC as possible; all 0201.
  - **C6 (1.5 pF, first shunt):** ground connects ONLY to pin 32 (VSS_PA) on the top layer, and
    pin 32 connects ONLY to the centre pad (pin 49) under the package.
  - **C9 (2.0 pF, second shunt):** its ground is a small top-layer island with three vias that
    go straight to the bottom-layer ground.
  - **L2 and L3 are cut out under the whole matching network and the RF output trace** (a
    notch from the ANT pin area out to the board edge), so C9's vias touch no inner plane and the
    match references the bottom layer there. On our 6-layer board, cut out **L2–L5** the same way
    (the match then references L6 at ≈1.44 mm, as on Nordic's board), and **the bottom
    layer under that area must be unbroken ground**: no parts, no traces, and no flex or dock
    copper.
  - The RF output from the match is a wide trace with a rounded end (to a test point) over that
    cutout. From the "RF" node, run to the chip antenna's own match; measure Nordic's trace and
    gap from the PcbDoc before choosing between copying their bottom-referenced line or a short
    50 Ω microstrip over restored L2 ground (about 0.16–0.18 mm on JLC06161H-3313; confirm with
    JLC's impedance calculator).
  - Ground-via stitching all round the match and along the board edges, as in Nordic's layout.
- **32.768 kHz crystal: fit it.** It keeps the BLE sleep clock accurate during connections and
  Channel Sounding. Nordic's BOM: 2012 package, 9 pF load, ±20 ppm. No external caps (internal
  load caps on P1.00 / P1.01).
- **32 MHz crystal:** Nordic's BOM: 2016 package, CL = 8 pF, ±40 ppm total. No external caps.
- **MCU: nRF54L10-QFAA (decided 2026-11-10; replaces the ESP32-H2).**
  - **Package stays QFN48 (checked 2026-11-11).** The nRF54L10 has no CSP; the 2.4 × 2.2 mm
    CSP47 is nRF54L15-only, not pin-compatible, and at 0.3 mm pitch is below JLC's 0.35 mm
    assembly minimum and 0.25 mm BGA-pad minimum. The nRF54LC10A CSP29 (0.35 mm) has only 12
    GPIOs, too few. QFN40 isn't available in practice; only the QFN48 is stocked.
  - **Why Nordic over the H2:**
    - Lower sleep current: nRF54L15 0.7–2.9 µA; nRF52833 2.6 µA with RTC and full RAM.
    - Far lower BLE radio current: nRF54L15 4.8 mA TX at 0 dBm, against 26–112 mA BLE TX on the
      H2 module.
    - The nPM1300 fuel gauge works (Cortex-M).
    - Bluetooth LE 6.0 Channel Sounding (distance ranging) and AoA transmit; see the BLE section.
    - Zephyr has a mature SX126x LoRa driver and LoRaWAN support.
  - **Nordic costs:**
    - No built-in USB-JTAG, so debugging needs SWD and a probe.
    - Firmware moves to the nRF Connect SDK / Zephyr.
    - nRF54L15 has no USB; its CSP is 2.4 × 2.2 mm at 0.3 mm pitch, so check that JLC can place
      it. The QFN48 is 6 × 6 mm.
    - **nRF54L pin planning:** peripherals must normally use pins on their own power domain's port
      (MCU domain → P2, peripheral domain → P1, low-power domain → P0). Clock signals must use
      the dedicated clock pins. P2 has no GPIOTE or Sense, so put interrupt inputs (accelerometer,
      GNSS TX_READY, SX1262 DIO1 IRQ) on P0 or P1. The nRF52 series is fully flexible apart from
      analog, NFC, crystal and SWD pins.
  - **Tools:** the nRF Connect SDK is free (Apache-2.0 / Nordic 5-Clause; the SoftDevice
    Controller is a free binary). J-Link is the smoothest probe; CMSIS-DAP works with pyOCD /
    OpenOCD, but check nRF54L support.
- **Dock contacts: on the PCB, not wired from the case.**
  - Four SMT gold target contacts on the board underside, in the side strips beside the flex,
    two per side, soldered by JLC.
  - Candidate: Mill-Max 1944 SMT flat-face target (3.17 mm face, 3.05 mm tall, gold over nickel),
    via JLC global sourcing unless LCSC has an equivalent.
  - Set the case floor so the faces finish flush with the outside, then pot around them.
  - Use an **asymmetric pattern** (offset one pair along the board) and a keyed dock cradle, so
    the collar can't dock reversed.
  - **Signals:** VBUS, GND, SWDIO, SWCLK. The dock holds the probe (Raspberry Pi Pico
    debugprobe, or a J-Link OB). It gives flashing, debugging, RTT logging and full-erase
    recovery. Field updates go over BLE (MCUboot).
  - **Undocked contacts sit at 0 V, to stop wet-collar corrosion:**
    - Each data contact goes through a TI TMUX1101 (SPST, active-high SEL, 3 pA leakage, 1.8 Ω,
      3 nA supply, SC70-5).
    - SEL is driven from VBUS through about 100 k / 150 k, held low when undocked. Optionally add
      1 MΩ pulldowns on the contact side.
    - Docking (VBUS) also wakes the PMIC from ship mode.
  - **ESD:** a TI TPD1E10B06 (LCSC C1847652, 0402, 5.5 V working, 100 nA max leakage, 12 pF) on
    each contact, on the contact side of the switch.
- **Accelerometer: ST LIS2DW12TR (LCSC C189624), replacing the LIS2DE12 (2026-11-10).**
  Criteria: lowest power, LCSC stock, smallest footprint.
  - LGA-12, 2.0 × 2.0 × 0.7 mm (thinner than the LIS2DE12's 1.0 mm).
  - Datasheet: 0.38 µA at 1.6 Hz and about 1 µA at 12.5 Hz in low-power mode; 50 nA
    power-down. Wake-up, activity/inactivity and free-fall interrupts on chip.
  - LCSC: about 30k in stock, about $0.55 (checked 2026-11-10).
  - Rejected: LIS2DU12 (0.47 µA at 1.6 Hz, same size, but 0 at LCSC); ADXL367 (180 nA
    wake-up mode, the lowest, but 2.2 × 2.3 mm, about $5 and under 100 at LCSC); LIS2DE12
    (higher current, 1 mm tall).
  - Wiring as before: I2C, CS to 3V3_A, SA0 sets the address, INT1 to P0.01, pin 7 (RES) to
    GND, pin 5 NC. Vdd and Vdd_IO both on 3V3_A.
- **Recovery:** a full erase over SWD from the dock; the nPM1300 watchdog / failed-boot reset
  as a field backstop.
- **GNSS interface: I2C (DDC) + TX_READY to the MCU.**
  - The M10 can raise a TX_READY pin when its buffer passes a threshold, so the MCU sleeps until
    data is waiting.
  - A UART left listening for NMEA keeps the MCU's high-speed clock running.
  - I2C can share the bus with the accelerometer and the PMIC.
  - Bring the M10's UART out to test pads for u-center bring-up and debugging.
- **Battery:** LiPo 802025 (8 × 20 × 25 mm, 350 mAh). Its protection PCB stays on the cell, so
  there is **no protector on the board** (XB5353A dropped).
  - Charge current: about 150–175 mA (0.5C or less). Check the cell's own maximum charge and
    discharge ratings.
  - Expected peak load is about 150 mA (LoRa TX + GNSS + nRF54L10), under 1C.
  - Rough budget: about 1.4 days with GNSS on continuously, several days with motion gating.
    Recompute this with datasheet currents.
- **Supply-rail constraints:**
  - nRF54L10 runs from 1.7–3.6 V (check its datasheet); the MIA-M10Q from 1.76–3.6 V.
  - 3.3 V is kept for everything so the SX1262 gets full +22 dBm and no level shifters are needed;
    1.8 V would sit too close to the M10Q minimum.
  - From a 1-cell LiPo: A 3.3 V buck or LDO in 100%-duty /
    dropout keeps working down to a cell voltage of about 3.1–3.2 V, which is very little lost
    capacity. A buck-boost (like today's TPS631000) is probably unnecessary.
  - Check the SX1262's +22 dBm output against its supply voltage in its datasheet (full power
    needs VBAT ≥ about 3.3 V; check the derating curve).
- **Power path: still open.** See the power section below.
- **JLC constraints:**
  - Standard PCBA for double-sided boards and 0201 parts.
  - Flex: 1–2 layers, PI core εr 3.3, 25 µm. No rigid-flex.
  - The flex is soldered to the board.
- **Flex-to-board soldering (by hand):**
  - Plated holes in the flex pads; pre-tin the board pads.
  - Tacky flux, pin the alignment holes, Kapton tape.
  - Preheat the board to 100–120 °C, then an iron at 330–350 °C through each hole.
  - Strain-relieve with epoxy or UV glue before potting.

## Topology: nRF54L10 QFN48 + nPM1300 + MIA-M10Q + SX1262 (draft, 2026-11-10)
Check every pin against the nRF54L QFN48 pin-assignment table before layout, in particular the
clock-capable pins and the port/power-domain rules.

**Power tree (nPM1300)**
- **VBUS:** from the dock pad, through a TPD1E10B06. Docking also wakes the PMIC from ship mode.
- **VBAT:** from BAT+/BAT− on the flex. The cell keeps its own protection board.
- **Rails swapped (2026-11-11), after the datasheet check:** the VSET1 resistor table tops out at
  2.7 V (250–500 kΩ), so BUCK1 cannot start up at 3.3 V without I2C. VSET2 reaches 3.3 V at
  250–500 kΩ. Register range for both bucks is 1.0–3.3 V; VSET resistors ≤5 % tolerance and are
  read only at power-up.
- **BUCK2 = 3V3_A = 3.3 V** (VSET2 = 390 kΩ 1 %, mid of the 250–500 kΩ band, so it comes up
  without I2C). Feeds: nRF54L10 VDD, LIS2DW12, MIA-M10Q, the TMUX1101s, VDDIO and the I2C
  pull-ups.
  - Optional: feed the GNSS main supply through LSW1 so it can be fully powered off, and keep its
    backup supply alive for hot starts. Check the MIA-M10Q pinout for V_BCKP / V_IO.
- **BUCK1 = 3V3_RF** (VSET1 tied to GND, <100 Ω, so BUCK1 starts OFF): SX1262 only. Keeps its
  ~120 mA transmit bursts off the MCU/GNSS rail. Firmware sets BUCK1 to 3.3 V over I2C and enables
  it before using the radio. All I/O is at 3.3 V, so no level shifters.
  - While 3V3_RF is off, drive the SX1262 SPI, NSS and NRESET lines low or leave them hi-Z, so
    they don't back-power the radio through its I/O.
  - Force PWM on BUCK1 during LoRa TX (erratum [30]: on VBAT only, the PWM→hysteretic transition
    can push VOUT outside ±5 %).
  - Headroom: 3.3 V is the buck's maximum and the SX1262's minimum for +22 dBm. At −5 % expect
    roughly −0.5 dB, and more once the cell falls below ~3.4 V (dropout 100 mV at 1 mA). Accepted
    for now; a small buck-boost on 3V3_RF only is the fix if that tail matters.
- **VDDIO = 3.3 V.** NTC: no thermistor in the cell, so bias it as the datasheet says.
- **SHPHLD:** optional reed or Hall switch to GND, for magnet wake from ship mode.
- **GPIO:** one GPIO is the interrupt to the MCU; optionally one drives the nRF nRESET
  (watchdog / failed-boot recovery).

**nRF54L10 pin plan (QFN48)**

| Function | Pin | Notes |
|---|---|---|
| I2C SDA (TWIM30, low-power domain) | P0.02 | GNSS, PMIC, accelerometer; 4.7 k pull-ups to 3.3 V |
| I2C SCL (TWIM30) | P0.03 | Must be a clock-capable pin (P0.03 is) |
| GNSS TX_READY (interrupt) | P0.00 | P0 can wake the system |
| Accelerometer INT1 | P0.01 | Motion wake |
| nPM1300 GPIO interrupt | P0.04 | |
| 32.768 kHz crystal | P1.00 / P1.01 | XL1 / XL2; internal load caps |
| SX1262 SCK (SPIM21, peripheral domain) | P1.04 | Clock-capable pin |
| SX1262 MOSI / MISO / NSS | P1.05 / P1.06 / P1.07 | |
| SX1262 DIO1 IRQ | P1.08 | P1 has GPIOTE (P2 does not) |
| SX1262 BUSY / NRESET | P1.09 / P1.10 | |
| GNSS RESET_N / EXTINT | P1.11 / P1.12 | Optional |
| Spare analog | P1.13 / P1.14 | Optional battery divider (not needed with nPM1300) |
| Spare | P1.02 / P1.03 | NFC pins; set as GPIO in UICR |
| Spare | P2.00–P2.10 | Trace / SPIM00; no GPIOTE, so no interrupts here |
| SWDIO / SWDCLK | pins 25 / 26 | Through the TMUX1101s (SEL from VBUS) to the dock pads |
| ANT | pin 31 | Nordic reference match, then the 2.4 GHz chip antenna |

Used: P0 5/5, P1 13/15, P2 0/11.

**Pin plan checked against Nordic's nRF54L15-QFAA reference schematic v0.8 (2026-11-10).**
QFN48 pin numbers: P1.00–P1.08 = 1–9; VDD = 10, 22, 36, 47, 48; P2.00–P2.10 = 11–21;
P0.00 = 23, P0.01 = 24, P0.02 = 27, P0.03 = 28, P0.04 = 29; SWDIO = 25, SWDCLK = 26;
RESET = 30; ANT = 31; VSS_PA = 32; DECRF = 33; XC1/XC2 = 34/35; P1.09–P1.14 = 37–42;
DECA = 43; VSS = 44; DECD = 45; DCC = 46; centre pad VSS = 49.
- Clock-capable (/CK) pins: P0.03, P0.04; P1.03, P1.04, P1.08, P1.11, P1.12; P2.01, P2.06.
  I2C SCL on P0.03 and SPI SCK on P1.04 are both on /CK pins. OK.
- P1.08 is also EXTREF/CLK16M; using it for the SX1262 IRQ is fine.
- P2.07 is SWO (trace), so leave it spare for debugging.

**nRF54L10 support circuit (Nordic config 1, internal DC/DC)**
| Ref | Value | Connection |
|---|---|---|
| C3 | 10 µF 0402 | VDD pins 47/48 |
| C10 | 100 nF 0201 | VDD pins 47/48 |
| C4, C7, C8 | 100 nF 0201 each | VDD pins 10, 22, 36 |
| L1 | 4.7 µH 0603 | DCC (46) to DECD (45) |
| C1 | 2.2 µF 0201 | DECD (45) |
| FB1 | 120 Ω @ 100 MHz, 200 mA, 0201 | DECD to DECA/DECRF |
| C2 / C12 / C5 | 2.2 µF / 10 nF / 2.2 nF, 0201 | DECA (43) + DECRF (33) |
| X2 | 32 MHz, 2016, CL 8 pF, ±40 ppm total | XC1/XC2; no load caps |
| X1 | 32.768 kHz, 2012, 9 pF, ±20 ppm | P1.00/P1.01; no load caps |
| R1 | 1 k 0201 | Series, RESET (30) to the NRESET net |
| C13 | 3.9 pF 0201 | RESET pin to GND (pin side of R1) |
| L2 | 2.7 nH LQP03HQ2N7B02 | ANT (31), series |
| C6 | 1.5 pF GJM0335C1E1R5WB01 | Shunt, ground to VSS_PA only |
| L3 | 3.5 nH LQP03HQ3N5B02 | Series |
| C9 | 2.0 pF GJM0335C1E2R0WB01 | Shunt, bottom-layer ground only |
| L4 | 3.5 nH LQP03HQ3N5B02 | Series |
| C11 | 0.3 pF | Shunt, at the RF output |

- **Community KiCad block differs slightly:** hlord2000's block has two 10 nF caps where Nordic
  has 10 nF + 2.2 nF on DECA/DECRF, and no 32.768 kHz crystal. Use Nordic's values.
- Nordic's BOM tolerances: C6, C9, C13 ±0.05 pF NP0; C11 ±0.1 pF C0G; L2–L4 ±0.1 nH.
- Check JLC stock for the Murata LQP03HQ / GJM parts; use the exact series if possible, since
  the match was tuned with them.

**SX1262**
- Path: RFO (HP PA) and RFI_P/RFI_N → SPDT RF switch → 915 MHz matching network → ANT pad
  (feed via beside the pad) → flex dipole.
- DIO2 drives the RF switch (SetDio2AsRfSwitchCtrl), so no MCU pin is needed for it. If the
  chosen switch needs complementary controls, add an inverter or use one spare MCU pin.
- Copy the switch part, the TX/RX matching values and the DC-DC parts (DCC_SW inductor, VREG cap)
  from Semtech's SX1262 915 MHz reference design (SX1262MB2CAS class).
- Reference: a 32 MHz crystal on XTA/XTB is fine for US915's SF7–SF10 / 125 kHz uplinks. A TCXO
  powered from DIO3 (SetDio3AsTcxoCtrl) is the safer choice for wide temperature swings; the 1SJ
  uses a TCXO. Decide from the datasheet's frequency-error limits.
- VBAT and VBAT_IO both on 3V3_RF; I/O is 3.3 V, matching the nRF54L.
- DIO3 unused if a crystal is chosen; leave it open or as a test pad.

**Dropped from the H2 version (history):** the Hall sensor on the GPIO9 boot strap, the USB D+/D− routing
and the 32 MHz crystal load caps (the nRF54L has internal ones).

## Proposed floorplan (17 × 20 mm, 6 layers, both sides; may grow slightly if layout needs it)
Widened from 15 mm to fit the dock targets; the extra ground also helps the 2.4 GHz and GNSS
antennas.
- **Left end:** SX1262 (4 × 4 mm, smaller than the LR1121 it replaces) and the 915 MHz switch
  and matching network above the ANT pad.
- **Right end:** charger/PMIC and power parts above the GND/VBAT pads.
- **The two remaining top corners:** GNSS antenna and 2.4 GHz antenna, diagonally apart.
- **Middle:** nRF54L10 + 32 MHz crystal, with a short 2.4 GHz RF trace to the chip antenna.
  Orient U1 so its RF side (pins 31–33) faces the 2.4 GHz antenna corner.
- **Check:** the bottom-layer ground under the 2.4 GHz match must stay unbroken. Under the
  board, the flex carries copper only at the two end pads: the antenna arm leaves from the ANT
  pad (left end, x < 3.6) and the GND/VBAT arm from the right-end pads (x ≥ 15). The middle
  of the strip is bare flex apart from the isolated MECH pad (x 8–10). So keep the nRF match
  and RF trace clear of the board's own L4 pad lands, mainly the MECH pad, and away from the
  ANT end.
- **Underside:** the 8 mm flex strip down the middle, with 4.5 mm strips either side. These hold
  the four dock targets (two per side, pattern offset for keying) plus the switches, ESD diodes
  and other small parts.

## Power path – findings so far
**Ways out of the "off" states.** The device is sealed, so the only ways in are docking (VBUS) or
a magnet.
- **BQ25186** (I2C, 1 A linear, power path, 10-pin DLH package) has two "off" states:
  - **Ship mode:** exits on valid VIN, *or* by holding TS/MR low for tSHIPWAKE. Datasheet:
    3.2 µA in ship mode with button-press wake, 4 µA in battery-only mode.
  - **Shutdown mode:** a TS/MR press does not wake it; only VIN does.
  - The long-press action is configurable: ship, shutdown, hardware reset, or ignore. So configure
    ship mode (not shutdown) if a magnet must be able to wake it.
- **BQ25185** (standalone): TI's E2E answer says factory mode can only be left by asserting VIN.
- **In this collar:**
  - Docking (VBUS) always wakes it.
  - Magnet wake needs a reed switch, or a micropower Hall switch powered from BAT, pulling TS/MR
    low.
  - TS/MR also carries the NTC function. With no thermistor, check how the datasheet wants TS/MR
    biased.

**Candidates.** Check JLC/LCSC stock for each.
1. **Nordic nPM1300: best functional fit; check stock and software.**
   - Linear charger at 32–800 mA, two 200 mA bucks (1.0–3.3 V), and two 50 mA LDOs / 100 mA load
     switches.
   - VSET pins set each buck's enable and voltage at power-on, so the 3.3 V rail comes up without
     I2C.
   - Ship mode 370 nA; it exits via a SHPHLD button to GND or VBUS.
   - Watchdog, hard reset and failed-boot recovery are useful in a sealed device.
   - Measures battery V/I/temperature, and it expects a pack with its own protection, which
     matches.
   - Packages: 3.1 × 2.4 mm WLCSP or 5 × 5 mm QFN32.
   - Ideas: put the MCU + GNSS on one buck and the LoRa radio on the other. A load switch can gate the
     GNSS main supply; keep its backup supply alive for hot starts.
   - **Checked 2026-11-10:**
     - **Fuel gauge:** Nordic's precompiled library supports Cortex-M0/M0+/M3/M4/M33/M55 and
       Xtensa-ESP32 (not RISC-V, which ruled it out on the H2).
     - **On an nRF54L (Cortex-M33) the fuel gauge IS supported**, using the nPM1300's own
       VBAT / current / temperature ADC. Nordic ships default battery models, or you can profile
       the actual 802025 cell with the nPM Fuel Gauge board. With the nPM1300, the existing
       FET + divider battery-sense circuit becomes optional.
     - Nordic's FAQ says the current measurement isn't accurate below 5 mA, so the gauge's
       model, not raw coulomb counting, has to cover sleep current.
     - **Stock:** LCSC lists the 5 × 5 QFN32 as C7501206, with zero or near-zero stock.
       Distributors (Arrow, Future, Avnet) have stock at about $1.4–1.9, so use JLC global sourcing
       or consign parts. The WLCSP (nPM1300-CAAA) saves a lot of area on a 17 × 20 board; check
       whether JLC can source and place it.
2. **TI BQ25120A / BQ2512x family:**
   - Linear charger up to 300 mA, a 300 mA buck, a 100 mA LDO or load switch.
   - Push-button wake and reset with timers; under 50 nA in ship mode; 700 nA with the buck
     enabled. Package 2.5 × 2.5 mm WCSP-25.
   - Ship-mode exit is by adapter or by toggling MR.
   - **Watch out:** the BQ25120A buck defaults to 1.8 V, which would bring the rails up at 1.8 V
     (too low for the M10Q margin and the SX1262 at full power) until I2C reprograms it. Use only a
     variant whose default is 3.3 V, and check the BQ2512x variant table. (Moot with the nPM1300.)
3. **BQ25186 plus a separate nano-Iq 3.3 V buck:**
   - The simplest TI route, with the button/VIN behaviour described above.
   - More parts and a higher ship current (3.2 µA) than the nPM1300.

## Power budget notes
- GPS draws about 180 mAh/day if run continuously, so plan on motion gating via the accelerometer,
  ADR and store-and-forward caching.
- Target 24 h or more on the 350 mAh cell.

## Open items (electrical)
0. ~~Choose the MCU~~ → nRF54L10-QFAA. ~~Choose the power path~~ → nPM1300. Still to decide:
   magnet wake (reed or Hall on SHPHLD) or dock-only wake.
1. **Pick the 2.4 GHz chip antenna; check JLC stock first.** Candidates:
   - Johanson 2450AT42E010B, the above-metal type with no keepout. This is the first pick for a
     17 × 20 board, and the board ground sits between it and the neck. Check its efficiency.
   - Johanson 2450AT18B100E (LCSC C2917717), which needs a ground-free strip about 4 mm deep at the
     board edge.
   - Taoglas WLA.04, with a 4.7 × 3 mm keepout.
   - Antenova SRCW004 (Weii), a wearable part marketed as resistant to detuning.
2. ~~Choose the stackup~~ → JLC06161H-3313. Still to do: confirm the 50 Ω L1 width (≈0.16–0.18 mm) and the 100 Ω stub width in JLC's calculator.
3. **Run a NEC sweep of the curved two-arm layout around a 72 mm neck** to set the antenna copper
   length and the bead position. Then tune with a NanoVNA on a cast test band.
4. A/B test the antenna against the Synzen SZK-C-2L28 FPC on the saline phantom, using TTN
   RSSI/SNR over a few dozen uplinks each.
5. **Ferrite beads:** high impedance at 915 MHz, low DC resistance, rated for charge and GNSS peak
   current. Check the datasheet curves.
6. **GNSS:** confirm the module and antenna (currently MIA-M10Q + ACAG0301 chip antenna; cheaper
   options were wanted) and check performance on the smaller ground plane.
7. Add the plated pad holes and alignment holes to `flex_strip.py` and its DXF.
8. Produce exact KiCad placements and trace widths once the antenna and stackup are fixed.
9. **Range improvements outside the tag:** raise the gateway antenna and use a higher-gain one; a
   second gateway or a ChirpStack Gateway Mesh relay is the other option.
