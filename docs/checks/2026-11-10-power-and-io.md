# Cat tracker respin – datasheet checks (2026-11-10)

**Status 2026-11-11:** the rail swap (item 1) and the BUCK1 notes (items 2–3) are merged into
`hardware/respin/handoff_electrical.md` and `connections_draft_nrf54l10.csv`. Item 4 (dock-side
SWD series resistors and probe VTref wait) is a dock/probe note and is not in the board brief.

## 1. nPM1300 VSET — BUCK1 cannot start at 3.3 V (change needed)
- PS Table 18 (VOUT1 by resistor): <100 Ω off; 4.7k 1.0 V; 10k 1.2; 22k 1.5; 47k 1.8; 68k 2.0;
  100k 2.2; 150k 2.5; **250–500k 2.7 V (max)**.
- VOUT2 by resistor goes up to **3.3 V at 250–500 kΩ** (nPM1300 EK user guide VSET table).
- Register range for both bucks is 1.0–3.3 V in 100 mV steps; resistors max 5 % tolerance;
  VSET pins read only at power-up.
- **Change:** swap the rails.
  - **BUCK2 → 3V3_A** (nRF54L10, GNSS, LIS2DW12, TMUX1101s, pull-ups, VDDIO). VSET2 = 390 kΩ 1 %
    (mid of 250–500 k) → 3.3 V with no I2C.
  - **BUCK1 → 3V3_RF** (SX1262 only). VSET1 grounded (<100 Ω) so BUCK1 starts OFF; firmware sets
    BUCK1 to 3.3 V over I2C and enables it before using the radio. Keep the SX1262 SPI/NRESET
    pins driven low or hi-Z while 3V3_RF is off to avoid back-powering through its I/O.

## 2. nPM1300 buck near a flat cell
- Spec: VSYSMIN 2.7 V to enable BUCK; VDROP_OUT 100 mV at 1 mA load; IOUT 200 mA; VOUT accuracy
  ±5 %. Output tracks VSYS minus dropout once VSYS falls below about VOUT + dropout.
- So 3.3 V holds down to a cell of roughly 3.4 V, then sags with the cell (more drop at higher
  load). All 3V3_A loads are fine well below 3.3 V. Little LiPo capacity is left below ~3.4 V.
- Errata [30]: on VBAT only, the PWM→hysteretic transition can push VOUT outside ±5 %. Force PWM
  on BUCK1 (3V3_RF) during LoRa TX.

## 3. SX1262 +22 dBm vs supply
- Semtech datasheet: the SX1262 HP PA is fed straight from VBAT; maximum output is limited by
  supply, and **VBAT = 3.3 V minimum to reach +22 dBm**. Operating supply 1.8–3.7 V, so VBAT
  can't come straight from the cell (4.2 V).
- 3.3 V is the highest the nPM1300 buck can give, so +22 dBm sits right at the limit:
  - Buck at −5 % (3.135 V): roughly −0.4 to −0.5 dB (estimate; check the PA-vs-VBAT curve).
  - Cell below ~3.4 V: the rail sags and TX power drops further. Today's TPS631000 buck-boost
    holds its rail regulated to a lower cell voltage, so the respin is slightly worse only in that
    last few % of capacity.
- If that tail matters: a small buck-boost just for 3V3_RF. Otherwise accept it.
- TCXO on DIO3 needs VBAT ≥ TCXO voltage + 200 mV; a 1.8 V TCXO is fine.

## 4. TMUX1101 SEL from VBUS divider — OK
- SEL has 1.8 V-compatible thresholds and fail-safe logic: SEL can be up to 5.5 V regardless of
  VDD, including VDD = 0. SEL abs max 6 V. The 100k/150k divider gives 3.0 V (3.3 V at 5.5 V
  VBUS): a solid logic 1.
- **Watch:** S/D pins abs max is VDD + 0.5 V. Docking from ship mode, SEL goes high at once while
  3V3_A is still coming up. A probe driving SWD at 3.3 V into S then forward-biases the ESD
  diodes into an unpowered 3V3_A. Fix on the dock side: 100 Ω–1 kΩ series resistors in SWDIO/SWCLK,
  and the probe only starts driving after it sees target power (J-Link VTref sense; set the same
  on the Pico debugprobe).

## Not done
- Datasheet PDFs not downloaded: the cloud workspace's network blocks vendor sites, and the
  computer link was down. Download into `hardware/datasheets/` from the desktop: nPM1300 PS,
  nRF54L10 PS, SX1261/2 datasheet + Semtech 915 MHz reference design, MIA-M10Q integration
  manual, TMUX1101, TPD1E10B06, LIS2DW12.
