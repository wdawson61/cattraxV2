# Dock

Charging and service dock for the collar. Started 2026-11-19; nothing is drawn yet.

Related:
- Collar side of the dock interface: `docs/electrical.md` (dock contacts) and `docs/interface.md`
  (target positions, keying).
- Dock-face mechanics (bare PETG neck face, target height, locating dimples):
  `docs/integration.md` §1.
- USB-UART datasheet check: `docs/checks/2026-11-19-dock-usb-uart.md`.
- Board-brief changes that go with this dock: `docs/notes/2026-11-19-dock-to-elec.md`.

## What the dock does

1. **Charges** the collar: passes USB 5 V to the collar's VBUS target. The collar's nPM1300 does
   all of the charging and sets the current; the dock is only a protected 5 V source.
2. **Wakes** the collar: VBUS on the collar wakes the nPM1300 from ship mode.
3. **Talks UART** to the collar at 1.8 V, through a USB-UART bridge, for:
   - firmware updates with MCUboot serial recovery (mcumgr / SMP), which works even when the
     application is broken;
   - logs and the application's own SMP / shell when it is running.

The dock carries **no debug probe**. SWD is only on internal test pads on the collar board,
reached by a pogo fixture before potting (factory flashing; prototypes). Field updates go over
BLE OTA.

## Contacts (collar ⇄ dock)

| Contact | Direction | Level | Notes |
|---|---|---|---|
| VBUS | dock → collar | 5 V | From USB through a current-limited switch (see below) |
| GND | — | 0 V | |
| TX | collar → dock | 1.8 V | nRF54L10 UARTE20 TXD (P1.13) → CH343P RXD |
| RX | dock → collar | 1.8 V | CH343P TXD → nRF54L10 UARTE20 RXD (P1.14) |

- Four gold targets on the collar's neck face, asymmetric pattern so it can't dock reversed.
- On the collar, TX/RX go through TMUX1101 switches (SEL from VBUS), so undocked contacts sit at
  0 V; each contact has a TPD1E10B06.
- Default UART: 115200 8N1, no flow control (MCUboot serial recovery default). Faster is possible
  later (CH343 goes to 6 Mbaud); check MCUboot/SMP buffer sizes before raising it.

## Block diagram

```
USB-C ──┬── VBUS 5 V ── current-limited switch ── pogo VBUS ──► collar
        │                (≈500 mA, part TBD)
        ├── VDD5 ┐
        │        CH343P ── V3: 0.1 µF only (internal 3.3 V regulator)
        ├── D+/D−┘   │
        │            VIO ◄── 1.8 V LDO (EN delayed, see "Power-up order")
        │            TXD ── 1 kΩ ── pogo RX ──► collar
        │            RXD ◄─ 1 kΩ ── pogo TX ◄── collar
        └── USB ESD (D+/D−/VBUS)              pogo GND
```

## USB-UART bridge: WCH CH343P

- **Part:** WCH CH343P, TQFN-16 3 × 3 mm, LCSC C2846043. Same die in SOP-16: CH343G (C2844153).
- **Why:** its UART I/O runs from a separate **VIO pin, 1.8–5 V**, independent of the core
  supply, and VIO does not back-feed V3/VDD5. So the dock talks 1.8 V to the collar with no
  level shifters.
- **Core / USB side must stay at about 3.3 V.** Two ways to power it (datasheet §5.2):
  - **From USB 5 V (planned):** VDD5 = USB VBUS, V3 = 0.1 µF decoupling only; the internal
    regulator makes 3.3 V for the core and USB transceiver.
  - **From an external 3.3 V rail:** tie VDD5 and V3 together to the 3.3 V rail (< 3.6 V). Use
    this if the dock ends up needing its own 3.3 V rail for something larger.
  - Never feed 1.8 V into VDD5 or V3; D+/D− and VBUS run from V3.
- **VIO = 1.8 V** from a small LDO off USB 5 V (or off 3.3 V if the dock gets a 3.3 V rail).
  WCH's power table lists this exact arrangement (VIO from USB 5 V through an external LDO).
- **Small 3.3 V needs:** V3 can supply about 10 mA to external loads (WCH power table), enough
  for an LED or a pull-up. Anything bigger gets its own 3.3 V LDO and the "external 3.3 V" option.
- **VBUS pin:** to USB VBUS (it detects the USB supply). Check the datasheet's VBUS divider /
  current note for the chosen supply option.
- **Pins used:** TXD, RXD. RTS/DTR unused for now (no reset contact on the collar).
- **Datasheet:** English rev 1E; latest is the Chinese rev 1F (see the check). Driver: built
  into macOS and Linux (CDC); WCH's driver adds features on Windows.
- **Alternative:** Silicon Labs CP2102N, **QFN28 only** (separate VIO, 1.71 V–VDD); the
  QFN24/QFN20 versions tie VIO to VDD. CH340 family: no (3.3/5 V I/O only).

## Power-up order and back-powering (open)

When a collar in ship mode is docked, its TMUX1101 SEL goes high from VBUS at once, but its 1V8
rail takes a few milliseconds to come up. The TMUX1101 S/D pins are rated to VDD + 0.5 V, so
the CH343P's TXD idling high at 1.8 V would drive current into an unpowered 1V8 rail through the
switch's protection diodes. Same issue as the earlier SWD probe note
(`docs/checks/2026-11-10-power-and-io.md` §4).

Planned mitigations on the dock side (cheap; use both):
- **1 kΩ series resistors** in TX and RX at the pogo pins: limits any back-feed to < 2 mA.
- **Delay VIO**: an LDO with an enable pin, EN from 5 V through an RC (about 50–100 ms), so the
  CH343P's UART is unpowered until the collar's rails are up. With VIO at 0 V, CH343P I/O doesn't
  drive (check that its outputs float or go low with VIO off).

## Charging path

- USB 5 V → current-limited load switch / eFuse (≈500 mA, part TBD) → pogo VBUS. Protects the
  USB host if the pogo contacts are wet or shorted.
- ESD on the pogo VBUS line at the dock.
- Charge current is set by the collar (nPM1300, ≤ ~88 mA for the Grepow cells per
  `docs/integration.md` §3), so the dock needs no charger of its own.
- Charge status: read from the collar over the UART (nPM1300 charger status) and shown by the host
  tool. A dock LED is optional (power-on only, from V3 or 5 V).

## Firmware flows (dock side is just a serial port)

- **Recover / update:** dock the collar → it boots → MCUboot's serial-recovery window
  (CONFIG_BOOT_SERIAL_WAIT_FOR_DFU, a few hundred ms) → host sends an SMP command within the window
  → `mcumgr image upload` + reset. Host must be ready before docking (or the collar is reset by
  undock/re-dock).
- **Normal:** app exposes SMP + logs on UARTE20 while docked; it can detect docking from the
  nPM1300 VBUS status and enable the UART only then (saves power undocked).

## Mechanics (to agree with the mechanical session)

- Spring pogo pins on the dock (part TBD; spring force × 4 must not lift the collar out of the
  cradle) landing on the collar's flush gold targets.
- Keyed cradle that follows the band curve; locating pins into the two dimples proposed in
  `docs/integration.md` §1.
- Hold-down: the collar's weight is not enough to compress four pogos reliably; consider a small
  magnet in the cradle under the tracker (watch the GNSS antenna and the clasp's breakaway sensor)
  or a light clip.
- Wet collars: dock contacts face up, so add a drain path in the cradle.

## Draft BOM

| Ref | Part | Status |
|---|---|---|
| U1 | WCH CH343P USB-UART (LCSC C2846043) | chosen; datasheet check done |
| U2 | 1.8 V LDO with enable, ≥ 50 mA | TBD |
| U3 | 5 V current-limited load switch / eFuse, ≈ 500 mA | TBD |
| D1 | USB ESD array (D+/D−/VBUS) | TBD |
| D2–D4 | ESD on pogo VBUS / TX / RX | TBD (TPD1E10B06 like the collar, or an array) |
| R1, R2 | 1 kΩ series, pogo TX / RX | — |
| R3, C1 | RC delay on U2 EN | values TBD from U2's EN threshold |
| J1 | USB-C receptacle (5.1 kΩ CC pull-downs ×2) | TBD |
| J2 | 4 × spring pogo pins | TBD |

## Open items

1. Choose U2 (1.8 V LDO with EN), U3 (current limit), D1, J1, J2.
2. Confirm CH343P output behaviour with VIO = 0 (floating vs low).
3. Pogo pin force and travel vs target height (1.5 mm proposed, `docs/integration.md` §1).
4. Cradle shape, keying and hold-down, with the mechanical session.
5. Host tool: a small script around `mcumgr` for update / logs / charge status.
