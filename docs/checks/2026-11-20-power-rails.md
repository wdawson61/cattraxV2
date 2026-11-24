# 2026-11-20 — Power rails: PMIC, GNSS supply, SX1262 I/O supply

Datasheets used (all in `datasheets/`): nPM1300 PS v1.3, MIA-M10Q data sheet UBX-22015849 R08 and
integration manual UBX-21028173 R05, SX1261/2 DS rev 1.2, nRF54L DS v0.8, TI TPS62840 (SLVSEC6D),
TI SN74LV1T34/04.

## 1. PMIC: keep the nPM1300
- Buck accuracy is specified ±5% (PS 6.3.6, VOUT[n]ACC). The typical curves (PS Fig 18–19) show the
  1.8 V output within about −0.35 % … +0.9 % over −40…125 °C, 1–200 mA, VBAT 3.8/4.35 V.
- nRF54L10 runs 1.7–3.6 V, so even worst case (1.71 V) is in range. The shortfall is only against
  third-party parts specified with no margin at 1.8 V (SX1262 VBAT_IO min 1.8 V, MIA-M10Q ±2 %).
- Alternatives looked at and not taken:
  - nPM1304: same bucks, same QFN32 pinout, better for small cells, but 0 stock at LCSC.
  - TI BQ25190: ±1.5 % rails and a sequencer, but 0.4 mm DSBGA, buck-boost defaults to 4.8 V
    (above SX1262 3.9 V abs max), no Nordic fuel gauge, no LCSC stock.
  - ADI MAX77654: ±3 %, WLP, no gain over the above.

## 2. GNSS supply: TPS62840 1.8 V buck from VSYS (replaces TPS7A20 LDO off 3V3_RF)
- MIA-M10Q DS Table 13: VCC 1.76–3.6 V; V_IO (VIO_SEL = GND) 1.76 V … VCC, abs max 1.98 V.
  IM Table 40 asks for 1.8 V ±2 % in 1.8 V designs.
- The LDO path (BUCK2 at 3.3 V → LDO to 1.8 V) is ~50 % efficient while the GNSS runs.
- Running VCC at 3.3 V was checked and rejected: DS Tables 16/17 give ~46 mW at 3.0 V vs ~37 mW at
  1.8 V (default constellations, acquisition), and VCC would need a ≤ 0.2 Ω switch.
- Estimated battery power during a fix: LDO ~76 mW, VCC on 3V3_RF ~54 mW, TPS62840 ~42 mW
  (assumed 90 % BUCK2, 88 % TPS62840 — read the TI curves to confirm).
- TPS62840: ±1.5 % (PWM, full temp) → 1.773 V worst-case low, 13 mV above the 1.76 V floor for
  ripple. 25 nA off, 60 nA IQ. tSS 120 µs ≈ 67 µs/V, inside the MIA V_IO ramp limit 25…35000 µs/V
  (DS Table 12). Part: TPS62840YBGR (WCSP-6, 0.4 mm), LCSC C2071139. SON-8 (DLC) was out of stock.
- EN = GNSS_EN (P2.00) with a 1 MΩ pull-down (TPS62840 internal EN pull-down not confirmed).
- Open: read the PFM ripple at 1.8 V off TI Fig 45; if too high, the DLC part's MODE pin can
  force PWM while the GNSS runs (~3 mA extra).

## 3. SX1262 VBAT_IO through nPM1300 LOADSW1
- SX1262 DS §5.2: "At any time, VBAT_IO must be lower than or equal to VBAT." VBAT_IO = 1.8 V rail,
  VBAT = 3V3_RF (BUCK2). The nPM1300 documents no BUCK1/BUCK2 start order.
- Fix: LSIN1 = +1V8, LSOUT1 = LR_VIO → SX1262 VBAT_IO, 1 µF on LSOUT1 (PS Config 2).
  Load switches are off at power-on (PS 6.4), so VBAT_IO cannot lead VBAT. LOADSW2 unused (GND).
- Firmware rules: hold LR_NRESET low and SPI/NSS low or hi-Z until LR_VIO is on, then reset the
  radio. Turn LOADSW1 off before ship mode or before BUCK2 is turned off.
- Still worth scoping on the first boards: 1V8 / 3V3_RF / LR_VIO at power-up, ship-mode entry and
  battery pull.

## 4. Main rail voltage: 1.8 V nominal
- SX1262 VBAT_IO min is 1.8 V (DS Table 3-3); BUCK1 worst case is 1.71 V, typical ≈ 1.80 V.
  Accepted. If a board measures low, BUCK1 can be set to 1.9 V over I2C after boot (VSET1 only
  offers 1.8 or 2.0 V at power-on). At 1.9 V typical, the MIA signal pins (abs max 1.98 V) are fine;
  only the +5 % paper worst case (1.995 V) exceeds it.

## 5. RF switch drivers
- SKY13323-378LF needs VCTL at ≥ 2.7 V for P1dB +27 dBm (+19 dBm at 1.8 V).
- SN74LV1T34 (buffer → VCTL1, TX) and SN74LV1T04 (inverter → VCTL2, RX) on 3V3_RF, input SX1262 DIO2.
  VIH 1.36 V min at VCC 3.3 V. DCK pinout 1 NC, 2 A, 3 GND, 4 Y, 5 VCC. LV1T34: LCSC C78541.

### §5 update, 2026-11-23: PE4259, no logic gates
- The SKY13323 needs complementary controls at ≥ 2.7 V; DIO2 is 1.8 V, so it took a level-shifting
  buffer and inverter (2 × SC70-5, 2 decoupling caps, 2 RC filters). Replaced by the switch Semtech's
  own SX126x reference designs use (AN1200.40 §2.1.1).
- pSemi PE4259 (DOC-03694-5.01, 07/2026, `datasheets/radio/pe4259ds.pdf`), LCSC C470892 (PE4259-63, SC-70-6), ~12.7k in stock 2026-11-23.
  - Single-pin mode: pin 6 = VDD, pin 4 = CTRL. CTRL high → RFC–RF1, low → RFC–RF2 (Table 5).
  - VDD 1.8–3.3 V; control high ≥ 0.7 × VDD (≈ 1.26 V at 1.8 V), so DIO2 drives CTRL directly.
    The text calls for a "nominal 3 V" supply in single-pin mode, but Table 3 allows 1.8 V.
  - Input P1dB at 1 GHz: 29.5 dBm min with VDD 1.8–2.3 V (31.5 at 2.3–3.3 V); ~7 dB over +22 dBm.
  - IL 0.35 dB typ, isolation 30 dB typ at 1 GHz (VDD 3 V). RF pins 1, 3, 5 DC blocked (Table 7 note):
    C310, C312, C319.
  - DC inputs ≤ VDD + 0.3 V (Table 1): CTRL and VDD share LR_VIO, so this holds through power-up.
  - Table 3 note 2: a tuning cap is required for IL / return loss. The eval board (Fig. 13) shunts
    2 × 0.5 pF in series (0.25 pF) on RFC at the pin. Added C322 (0402, DNP) on SW_COM at pin 5;
    fit and tune with the antenna match.
- Wiring: VDD = LR_VIO (same rail as DIO2, so CTRL never drives an unpowered switch), 100 nF (C315);
  CTRL from LR_DIO2 through R301 1 kΩ (as the PE4259 eval board's control resistors).
  RF1 (pin 1) = TX_SW, RF2 (pin 3) = RX_SW, RFC (pin 5) = SW_COM.
- Removed: U9 SN74LV1T34, U10 SN74LV1T04, C316, C317, C318, R302. Added C322.
- Open: confirm P1dB / harmonics on the first boards at +22 dBm with VDD at 1.8 V.
