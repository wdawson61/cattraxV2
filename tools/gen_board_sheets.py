"""Generate the cattraxV2 main-board hierarchical schematic skeleton (KiCad 9 format; KiCad 10
opens and upgrades it). Root sheet + one sub-sheet per block, with hierarchical pins/labels for
the inter-block signals, labels on the root so same-named pins connect, and a parts/notes
text block on each sub-sheet. No symbols yet."""
import uuid, os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
os.makedirs(OUT, exist_ok=True)
PROJECT = "cattraxv2_main"
ROOT_UUID = "1280f897-b7c2-49b2-ad35-96b72642a045"   # keep the existing root uuid
VER = "20250114"
DATE = "2026-11-20"
U = lambda: str(uuid.uuid4())
G = 2.54


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def font(just=None):
    j = f"\n\t\t\t\t(justify {just})" if just else ""
    return f"(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t){j}\n\t\t\t)"


def title_block(title, c1, c2=""):
    return (f"\t(title_block\n\t\t(title {q(title)})\n\t\t(date {q(DATE)})\n\t\t(rev \"A\")\n"
            f"\t\t(comment 1 {q(c1)})\n\t\t(comment 2 {q(c2)})\n\t)\n")


# name: (file, [(pin, type, side)], notes)
SHEETS = {
 "power": ("power.kicad_sch", [
     ("VBUS", "input", "L"), ("VBAT", "passive", "L"),
     ("I2C_SDA", "bidirectional", "R"), ("I2C_SCL", "input", "R"), ("PMIC_INT", "output", "R")],
  "POWER — nPM1300 PMIC (QFN32 5x5)\n"
  "- Charger from VBUS (dock), VBAT from the flex pads (cell has its own protection PCB)\n"
  "- BUCK1 = 1V8 main rail: VSET1 47k (up at power-on, no I2C)\n"
  "- BUCK2 = 3V3_RF for SX1262 VBAT only: VSET2 to GND (off at boot), firmware enables at 3.3 V\n"
  "- Ship mode; wake on VBUS (docking) or SHPHLD (optional magnet switch)\n"
  "- I2C target on the shared bus; GPIO1 -> PMIC_INT; NTC: fixed resistor or disabled (verify)\n"
  "- Buck inductors + VBUS/VSYS/VBAT/VOUT caps per nPM1300 PS\n"
  "Rails leave this sheet as power symbols: +1V8, +3V3_RF, VBAT, VBUS, GND\n"
  "Status: 1V8 rail decision in docs/notes/2026-11-19-dock-to-elec.md (brief not yet updated)"),
 "mcu": ("mcu.kicad_sch", [
     ("I2C_SDA", "bidirectional", "L"), ("I2C_SCL", "output", "L"), ("PMIC_INT", "input", "L"),
     ("UART_TX", "output", "L"), ("UART_RX", "input", "L"),
     ("ACC_INT1", "input", "R"), ("GNSS_TXRDY", "input", "R"), ("GNSS_RESET_N", "output", "R"),
     ("GNSS_EXTINT", "output", "R"), ("LR_SCK", "output", "R"), ("LR_MOSI", "output", "R"),
     ("LR_MISO", "input", "R"), ("LR_NSS", "output", "R"), ("LR_IRQ", "input", "R"),
     ("LR_BUSY", "input", "R"), ("LR_NRESET", "output", "R")],
  "MCU — nRF54L10-QFAA (QFN48 6x6), Nordic reference config 1 (internal DC/DC)\n"
  "- Decoupling: C3 10u + C10 100n (VDD 47/48), C4/C7/C8 100n (VDD 10/22/36)\n"
  "- DC/DC: L1 4.7u 0603 DCC->DECD, C1 2.2u; FB1 120R ferrite -> DECA/DECRF, C2 2.2u, C12 10n, C5 2.2n\n"
  "- X2 32 MHz 2016 CL 8 pF; X1 32.768 kHz 2012 9 pF (no external load caps)\n"
  "- RESET: C13 3.9p to GND, R1 1k series -> test pad\n"
  "- 2.4 GHz: L2 2.7n, C6 1.5p (GND to VSS_PA only), L3 3.5n, C9 2.0p (bottom-layer GND only),\n"
  "  L4 3.5n, C11 0.3p -> chip antenna match + 2.4 GHz chip antenna (part TBD)\n"
  "- Pins: TWIM30 SDA P0.02 / SCL P0.03; GNSS_TXRDY P0.00; ACC_INT1 P0.01; PMIC_INT P0.04\n"
  "  SPIM21 P1.04-P1.07; LR_IRQ P1.08; LR_BUSY P1.09; LR_NRESET P1.10; GNSS RESET/EXTINT P1.11/P1.12\n"
  "  UARTE20 TX P1.13 / RX P1.14 (dock)\n"
  "- SWD (SWDIO pin 25, SWDCLK pin 26, RESET, 1V8, GND) to internal test pads only\n"
  "Power: +1V8, GND"),
 "lora": ("lora.kicad_sch", [
     ("LR_SCK", "input", "L"), ("LR_MOSI", "input", "L"), ("LR_MISO", "output", "L"),
     ("LR_NSS", "input", "L"), ("LR_IRQ", "output", "L"), ("LR_BUSY", "output", "L"),
     ("LR_NRESET", "input", "L"), ("ANT_915", "passive", "R")],
  "LORA — SX1262 (QFN24 4x4), 915 MHz only\n"
  "- VBAT on +3V3_RF (full +22 dBm); VBAT_IO on +1V8 (all digital I/O at 1.8 V, no shifters)\n"
  "- DIO1 -> LR_IRQ; DIO2 drives the RF switch (SetDio2AsRfSwitchCtrl); DIO3 TCXO supply if TCXO\n"
  "- XTA/XTB: 32 MHz crystal or TCXO (decide from datasheet frequency-error limits)\n"
  "- DCC_SW inductor + VREG cap per datasheet\n"
  "- RFO -> TX match; RFI_P/RFI_N -> RX balun; values from Semtech 915 MHz reference design\n"
  "- U: pSemi PE4259 SPDT (VDD +1V8, single-pin control from DIO2)\n"
  "  OPEN: which port CTRL-high selects (wire to TX); DC blocks on RF ports?\n"
  "- Switch common -> 915 MHz match -> ANT_915 (bottom ANT pad, feed via beside the pad)\n"
  "Power: +3V3_RF, +1V8, GND"),
 "gnss": ("gnss.kicad_sch", [
     ("I2C_SDA", "bidirectional", "L"), ("I2C_SCL", "input", "L"), ("GNSS_TXRDY", "output", "L"),
     ("GNSS_RESET_N", "input", "L"), ("GNSS_EXTINT", "input", "L")],
  "GNSS — u-blox MIA-M10Q (LGA 4.5x4.5)\n"
  "- VCC on +1V8 (supported; u-blox 1.8 V reference designs), optional switch via nPM1300 LSOUT1\n"
  "- V_BCKP (if present) to +1V8 for hot start\n"
  "- I2C (DDC) on the shared bus; TX_READY -> GNSS_TXRDY (configure pin via CFG-TXREADY)\n"
  "- RF_IN -> antenna match -> ACAG0301 GNSS chip antenna (clearance per antenna datasheet)\n"
  "- TXD/RXD to test pads for u-center bring-up\n"
  "Power: +1V8, GND"),
 "sensors": ("sensors.kicad_sch", [
     ("I2C_SDA", "bidirectional", "L"), ("I2C_SCL", "input", "L"), ("ACC_INT1", "output", "L")],
  "SENSORS — ST LIS2DW12 (LGA-12 2x2)\n"
  "- I2C mode: CS to +1V8; SA0 sets the address; RES pin to GND; NC pin open\n"
  "- INT1 -> ACC_INT1 (motion wake); INT2 unused or test pad\n"
  "- I2C pull-ups for the shared bus live here (to +1V8; size for 1.8 V rise time)\n"
  "Power: +1V8, GND"),
 "dock": ("dock.kicad_sch", [
     ("VBUS", "output", "R"), ("UART_TX", "input", "R"), ("UART_RX", "output", "R")],
  "DOCK INTERFACE — 4 gold targets on the underside (keyed pattern)\n"
  "- Targets: VBUS, GND, TX (collar out), RX (collar in)\n"
  "- TPD1E10B06 ESD on each target (contact side)\n"
  "- TMUX1101 x2 on TX/RX (VDD +1V8), SEL from VBUS divider 100k/150k (SEL fail-safe to 5.5 V)\n"
  "  so undocked contacts sit at 0 V; optional 1M pulldowns on the contact side\n"
  "- Dock side (CH343P, 1.8 V VIO): see electrical/dock/README.md\n"
  "Power: +1V8, GND"),
 "flex_pads": ("flex_pads.kicad_sch", [
     ("ANT_915", "passive", "R"), ("VBAT", "passive", "R")],
  "FLEX PADS — underside, in the 8 mm centre strip (docs/interface.md)\n"
  "- ANT pad: 915 MHz feed to the flex antenna arm (tented feed via beside the pad)\n"
  "- MECH pad: mechanical anchor only\n"
  "- GND pad: counterpoise arm / battery return\n"
  "- VBAT pad: battery + via the flex (beads on the flex at x~63)\n"
  "- Footprints: custom pads matching electrical/flex/flex_strip.dxf\n"
  "Power: VBAT, GND"),
}

# root placement: name -> (x, y, w)
PLACE = {
    "power":     (50.8, 45.72, 40.64),
    "dock":      (50.8, 101.6, 40.64),
    "flex_pads": (50.8, 139.7, 40.64),
    "mcu":       (172.72, 45.72, 45.72),
    "gnss":      (299.72, 45.72, 40.64),
    "sensors":   (299.72, 91.44, 40.64),
    "lora":      (299.72, 127.0, 40.64),
}


def sheet_block(name, page, root_items):
    fname, pins, _ = SHEETS[name]
    x, y, w = PLACE[name]
    nl = sum(1 for p in pins if p[2] == "L")
    nr = len(pins) - nl
    h = max(nl, nr) * 2 * G + 2 * G
    out = [f"\t(sheet\n\t\t(at {x} {y})\n\t\t(size {w} {h:.2f})\n\t\t(exclude_from_sim no)\n"
           f"\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(fields_autoplaced yes)\n"
           f"\t\t(stroke\n\t\t\t(width 0.1524)\n\t\t\t(type solid)\n\t\t)\n"
           f"\t\t(fill\n\t\t\t(color 0 0 0 0.0000)\n\t\t)\n\t\t(uuid {q(U())})\n"
           f"\t\t(property \"Sheetname\" {q(name)}\n\t\t\t(at {x} {y - 0.7116:.4f} 0)\n\t\t\t{font('left bottom')}\n\t\t)\n"
           f"\t\t(property \"Sheetfile\" {q(fname)}\n\t\t\t(at {x} {y + h + 0.5846:.4f} 0)\n\t\t\t{font('left top')}\n\t\t)\n"]
    il = ir = 0
    for pin, typ, side in pins:
        if side == "L":
            il += 1
            py, px, ang, just = y + il * 2 * G, x, 180, "left"
            ex, lang, ljust = x - 2 * G, 180, "right bottom"
        else:
            ir += 1
            py, px, ang, just = y + ir * 2 * G, x + w, 0, "right"
            ex, lang, ljust = x + w + 2 * G, 0, "left bottom"
        out.append(f"\t\t(pin {q(pin)} {typ}\n\t\t\t(at {px} {py:.2f} {ang})\n\t\t\t(uuid {q(U())})\n\t\t\t{font(just)}\n\t\t)\n")
        root_items.append(f"\t(wire\n\t\t(pts\n\t\t\t(xy {px} {py:.2f}) (xy {ex:.2f} {py:.2f})\n\t\t)\n"
                          f"\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid {q(U())})\n\t)\n")
        root_items.append(f"\t(label {q(pin)}\n\t\t(at {ex:.2f} {py:.2f} {lang})\n\t\t(fields_autoplaced yes)\n"
                          f"\t\t{font(ljust)}\n\t\t(uuid {q(U())})\n\t)\n")
    out.append(f"\t\t(instances\n\t\t\t(project {q(PROJECT)}\n\t\t\t\t(path \"/{ROOT_UUID}\"\n"
               f"\t\t\t\t\t(page {q(str(page))})\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n")
    return "".join(out)


def text(s, x, y):
    return (f"\t(text {q(s)}\n\t\t(exclude_from_sim no)\n\t\t(at {x} {y} 0)\n\t\t{font('left top')}\n"
            f"\t\t(uuid {q(U())})\n\t)\n")


# root
root_items, sheets = [], []
for page, name in enumerate(PLACE, start=2):
    sheets.append(sheet_block(name, page, root_items))
root = ("(kicad_sch\n" f"\t(version {VER})\n\t(generator \"eeschema\")\n\t(generator_version \"9.0\")\n"
        f"\t(uuid {q(ROOT_UUID)})\n\t(paper \"A3\")\n"
        + title_block("cattraxV2 main board — top level",
                      "Draft hierarchy: sheets + inter-sheet signals only; no symbols yet",
                      "Signals connect by label name; power uses global power symbols (+1V8, +3V3_RF, VBAT, VBUS, GND)")
        + "\t(lib_symbols)\n"
        + text("Block map: power (nPM1300) | mcu (nRF54L10 + 2.4 GHz) | lora (SX1262 + PE4259 + 915 match)\n"
               "gnss (MIA-M10Q) | sensors (LIS2DW12 + I2C pull-ups) | dock (targets, ESD, TMUX) | flex_pads (ANT, MECH, GND, VBAT)\n"
               "Sources: docs/electrical.md, electrical/board/connections_nrf54l10.csv, docs/notes/2026-11-19-dock-to-elec.md",
               50.8, 17.78)
        + "".join(root_items) + "".join(sheets)
        + "\t(sheet_instances\n\t\t(path \"/\"\n\t\t\t(page \"1\")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)\n")
open(os.path.join(OUT, PROJECT + ".kicad_sch"), "w").write(root)

# sub-sheets
for name, (fname, pins, notes) in SHEETS.items():
    items = []
    for i, (pin, typ, side) in enumerate(pins):
        items.append(f"\t(hierarchical_label {q(pin)}\n\t\t(shape {typ})\n\t\t(at 63.5 {38.1 + i * 2 * G:.2f} 180)\n"
                     f"\t\t(fields_autoplaced yes)\n\t\t{font('right')}\n\t\t(uuid {q(U())})\n\t)\n")
    items.append(text(notes, 101.6, 38.1))
    s = ("(kicad_sch\n" f"\t(version {VER})\n\t(generator \"eeschema\")\n\t(generator_version \"9.0\")\n"
         f"\t(uuid {q(U())})\n\t(paper \"A4\")\n"
         + title_block(f"cattraxV2 main board — {name}", "Draft: hierarchical labels + notes only; add symbols here")
         + "\t(lib_symbols)\n" + "".join(items) + "\t(embedded_fonts no)\n)\n")
    open(os.path.join(OUT, fname), "w").write(s)


def balanced(path):
    d, instr, esc = 0, False, False
    for ch in open(path).read():
        if instr:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': instr = False
        elif ch == '"': instr = True
        elif ch == "(": d += 1
        elif ch == ")":
            d -= 1
            assert d >= 0, path
    assert d == 0 and not instr, path

for f in os.listdir(OUT):
    balanced(os.path.join(OUT, f))
print("ok", sorted(os.listdir(OUT)))
