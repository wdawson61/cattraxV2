# Dock USB-UART bridge – datasheet check (2026-11-19)

Requirement: a USB-UART bridge for the dock whose UART pins run at **1.8 V** (the collar's main
rail is 1.8 V), with no level shifters, small, stocked at JLC/LCSC.

## Sources
- WCH CH343 datasheet, English, **rev 1E** (mirror: https://static.chipdip.ru/lib/163/DOC045163990.pdf;
  original on wch-ic.com as `CH343DS1.PDF`). Latest is the Chinese **rev 1F** (LCSC / wch.cn);
  the VIO / power sections read the same in both.
- Silicon Labs CP2102N datasheet (operating conditions table, product selection guide).
- LCSC product pages: CH343P C2846043, CH343G C2844153.
- To save locally: `datasheets/dock/CH343DS1.pdf` (not committed).

## WCH CH343 (CH343P, TQFN-16 3 × 3, 0.5 mm pitch) — chosen
- Three supply pins (§5.2):
  - **VDD5:** input to the internal regulator.
  - **V3:** regulator output; core and USB transceiver supply. Needs ~0.1 µF.
  - **VIO:** supply for the UART I/O and RST pins, **1.8–5 V**. Should share the supply of the
    MCU it talks to. Not fed from V3/VDD5 internally; no reverse current path.
- Power options:
  - 5 V supply (above about 3.8 V): VDD5 from USB 5 V; V3 decoupling only.
  - 3.3 V supply (below 3.6 V): tie V3 to VDD5 and feed an external 3.3 V.
  - D+/D− and VBUS run from V3, not VIO, so the core side must be ~3.3 V; **VIO alone goes to 1.8 V**.
- WCH power table (rev 1E/1F): UART at 1.8–4 V with VIO from USB 5 V through an external LDO is a
  listed configuration. V3 can supply external 3.3 V up to about 10 mA.
- VIO current in USB suspend: about 2 µA with no I/O load.
- RXD has an internal pull-up to VIO; TXD idles high.
- VBUS pin: USB supply detect. If VIO falls below about 1.4 V with the VBUS pull-down off, the
  chip sinks about 300 µA on VBUS until VIO returns (rev 1E/1F §5.2).
- Packages: CH343P QFN16 3 × 3 (C2846043); CH343G / CH343C SOP-16 (CH343G C2844153).
- **Not yet checked:** I/O state when VIO = 0 V with V3 powered (matters for the dock's delayed-VIO
  plan; see `electrical/dock/README.md`).

## Silicon Labs CP2102N — fallback
- VDD 3.0–3.6 V (core). **VIO 1.71 V – VDD**, but only on the **QFN28** package; on QFN24 and
  QFN20, VIO is tied to VDD inside. So the CP2102N-A02-GQFN28 works for 1.8 V UART; the smaller
  packages don't.
- Larger (5 × 5 QFN28) and dearer than the CH343P.

## Rejected
- WCH CH340 family: UART I/O at the supply voltage only (3.3 / 5 V); would need level shifting.

## Collar-side consequences (for the board brief)
- TMUX1101 on the TX/RX contacts now runs at VDD = 1.8 V. SEL stays driven from the VBUS divider:
  per `checks/2026-11-10-power-and-io.md` §4, SEL is fail-safe up to 5.5 V regardless of VDD, so the
  existing 100k/150k divider is still fine.
- Back-powering on docking (S/D pins abs max VDD + 0.5 V while 1V8 is still coming up): handled on
  the dock with 1 kΩ series resistors and delayed VIO.
