"""Generate the cattraxV2 main-board schematic (KiCad 9 format; KiCad 10 opens/upgrades it).

Every connection is made with a short wire stub + label (or power symbol / no-connect) at
each pin end, so connectivity is explicit and easy to check; it is not a pretty drawing.
Pin numbers come from the datasheets in datasheets/ (see PIN SOURCES in each symbol).

Outputs (into OUT dir): cattraxv2_main.kicad_sch + 7 sub-sheets, cattraxv2.kicad_sym,
sym-lib-table, and netlist_check.csv (pin -> net, for review).

NOTE (2026-11-24): the sheets in electrical/board are now hand-arranged and use KiCad's standard
library for passives / crystal / test points / power (Device:R_US, Device:C, power:GND, ...) and the
kicad_lib2 submodule (nickname "symbol", footprints "footprint") for everything else. Do NOT run this into electrical/board. Its job now is the
reference netlist: run it into a scratch dir and copy only netlist_check.csv across. The symbol
definitions below are the source of the kicad_lib2 copies (same pins and geometry).
"""
import os, sys, uuid

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
os.makedirs(OUT, exist_ok=True)
PROJECT = "cattraxv2_main"
ROOT_UUID = "1280f897-b7c2-49b2-ad35-96b72642a045"
VER, GENV, LIB = "20250114", "9.0", "cattraxv2"
DATE = "2026-11-20"
G = 2.54
U = lambda: str(uuid.uuid4())


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def eff(just=None, hide=False):
    j = f" (justify {just})" if just else ""
    h = " (hide yes)" if hide else ""
    return f"(effects (font (size 1.27 1.27)){j}{h})"


def r2(v):
    return round(v / 0.01) * 0.01


# ---------------------------------------------------------------- symbols
SYMS = {}   # name -> dict(pins=[(num,name,x,y,ang)], body=(x0,y0,x1,y1) or None, ref, power)


def ic(name, ref, left, right, top=(), bottom=(), width=20.32, src="", grow=0.0):
    """left/right/top/bottom: lists of (num, name) or None for a gap. Library coords (y up)."""
    n = max(len(left), len(right))
    h = (n + 1) * G
    nt = max(len(top), len(bottom))
    w = max(width, (nt + 1) * G)
    w = round(w / (2 * G)) * 2 * G
    h = round(h / (2 * G) + 0.5) * 2 * G
    x0, x1, y0, y1 = -w / 2, w / 2, h / 2, -h / 2
    pins = []
    for i, p in enumerate(left):
        if p: pins.append((p[0], p[1], x0 - G, y0 - (i + 1) * G, 0))
    for i, p in enumerate(right):
        if p: pins.append((p[0], p[1], x1 + G, y0 - (i + 1) * G, 180))
    for i, p in enumerate(top):
        if p: pins.append((p[0], p[1], x0 + (i + 1) * G, y0 + G, 270))
    for i, p in enumerate(bottom):
        if p: pins.append((p[0], p[1], x0 + (i + 1) * G, y1 - G, 90))
    # grow: widen the body by this much each side while keeping the pin end points (shorter pins)
    SYMS[name] = dict(pins=pins, body=(x0 - grow, y0, x1 + grow, y1), ref=ref, power=False, src=src, kind="ic",
                      pinlen=G - grow)


def two(name, ref, kind):
    # vertical 2-pin: pin 1 top, pin 2 bottom
    SYMS[name] = dict(pins=[("1", "1", 0, 3.81, 270), ("2", "2", 0, -3.81, 90)], body=None,
                      ref=ref, power=False, kind=kind, src="")


def one(name, ref, kind):
    SYMS[name] = dict(pins=[("1", "1", 0, -2.54, 90)], body=None, ref=ref, power=False, kind=kind, src="")


def pwr(name):
    SYMS[name] = dict(pins=[("1", name, 0, 0, 90 if name != "GND" else 270)], body=None, ref="#PWR",
                      power=True, kind="gnd" if name == "GND" else "rail", src="")


# nRF54L10-QFAA, QFN48 (nRF54L15/L10/L05 datasheet v0.8, Table 73)
ic("nRF54L10-QFAA", "U", width=25.4, src="nRF54L DS v0.8 Table 73",
   left=[("1", "P1.00/XL1"), ("2", "P1.01/XL2"), ("3", "P1.02/NFC1"), ("4", "P1.03/NFC2"),
         ("5", "P1.04"), ("6", "P1.05"), ("7", "P1.06"), ("8", "P1.07"), ("9", "P1.08"),
         ("39", "P1.11"), ("40", "P1.12"), ("41", "P1.13"), ("42", "P1.14"), ("37", "P1.09"),
         ("38", "P1.10"), None, ("11", "P2.00"), ("12", "P2.01"), ("13", "P2.02"), ("14", "P2.03"),
         ("15", "P2.04"), ("16", "P2.05"), ("17", "P2.06"), ("18", "P2.07"), ("19", "P2.08"),
         ("20", "P2.09"), ("21", "P2.10")],
   right=[("10", "VDD"), ("22", "VDD"), ("36", "VDD"), ("47", "VDD"), ("48", "VDD"), None,
          ("46", "DCC"), ("45", "DECD"), ("43", "DECA"), ("33", "DECRF"), None,
          ("34", "XC1"), ("35", "XC2"), None, ("31", "ANT"), ("32", "VSS_PA"), None,
          ("23", "P0.00"), ("24", "P0.01"), ("27", "P0.02"), ("28", "P0.03"), ("29", "P0.04"),
          ("30", "nRESET"), ("25", "SWDIO"), ("26", "SWDCLK"), None, ("44", "VSS"), ("49", "EP/VSS")])

# nPM1300-QEAA, QFN32 (nPM1300 PS v1.3, Table 34)
ic("nPM1300-QEAA", "U", width=25.4, src="nPM1300 PS v1.3 Table 34",
   left=[("21", "VBUS"), ("22", "VBUSOUT"), ("23", "CC1"), ("24", "CC2"), None, ("19", "VBAT"),
         ("18", "NTC"), None, ("12", "VDDIO"), ("13", "SDA"), ("14", "SCL"), ("15", "SHPHLD"),
         None, ("7", "GPIO0"), ("8", "GPIO1"), ("9", "GPIO2"), ("10", "GPIO3"), ("11", "GPIO4"),
         None, ("25", "LED0"), ("26", "LED1"), ("27", "LED2")],
   right=[("20", "VSYS"), ("4", "PVDD"), None, ("3", "SW1"), ("1", "VOUT1"), ("2", "PVSS1"),
          ("17", "VSET1"), None, ("5", "SW2"), ("32", "VOUT2"), ("6", "PVSS2"), ("16", "VSET2"),
          None, ("28", "LSIN1/VINLDO1"), ("29", "LSOUT1/VOUTLDO1"), ("30", "LSIN2/VINLDO2"),
          ("31", "LSOUT2/VOUTLDO2"), None, ("33", "EP/AVSS")])

# SX1262IMLTRT, QFN24 (SX1261/2 DS rev 1.2, Table 2-1)
ic("SX1262IMLTRT", "U", width=20.32, src="SX1261/2 DS rev 1.2 Table 2-1",
   left=[("1", "VDD_IN"), ("10", "VBAT"), ("11", "VBAT_IO"), None, ("7", "VREG"), ("9", "DCC_SW"),
         None, ("3", "XTA"), ("4", "XTB"), None, ("19", "NSS"), ("18", "SCK"), ("17", "MOSI"),
         ("16", "MISO"), ("15", "NRESET"), ("14", "BUSY"), ("13", "DIO1"), ("12", "DIO2"),
         ("6", "DIO3")],
   right=[("24", "VR_PA"), ("23", "RFO"), None, ("22", "RFI_N"), ("21", "RFI_P"), None, None,
          ("2", "GND"), ("5", "GND"), ("8", "GND"), ("20", "GND"), ("25", "EP/GND")])

# SKY13323-378LF, MLPD-6 1x1 (Skyworks 201080F, Table 1); EP = ground
ic("SKY13323-378LF", "U", width=15.24, src="Skyworks 201080F Table 1",
   left=[("1", "OUTPUT1"), ("3", "OUTPUT2"), None, ("6", "VCTL1"), ("4", "VCTL2")],
   right=[("5", "INPUT"), None, ("2", "GND"), ("7", "EP/GND")])

# u-blox MIA-M10Q LGA (Integration manual R05, Table 1)
_mia_gnd = ["A1", "A2", "A3", "A8", "A9", "B2", "B8", "C3", "C9", "E3", "E4", "E9", "F1", "F3", "F4",
            "G3", "G4", "G5", "G6", "H8", "J8", "J9"]
ic("MIA-M10Q", "U", width=27.94, src="MIA-M10Q IM R05 Table 1",
   left=[("B1", "VCC"), ("J4", "V_IO"), ("J5", "V_BCKP"), ("J6", "VIO_SEL"), ("C6", "VCC_RF"), None,
         ("D1", "SDA/PIO2"), ("E1", "SCL/PIO3"), ("G1", "TX/PIO1"), ("H1", "RX/PIO0"),
         ("A6", "EXTINT/PIO5"), ("A7", "TIMEPULSE/PIO4"), ("F7", "PIO6"), ("C4", "RESET_N"),
         ("C7", "SAFEBOOT_N"), ("H9", "LNA_EN"), None, ("A4", "RTC_I"), ("A5", "RTC_O"), None,
         ("D2", "RSVD_D2"), ("E2", "RSVD_E2"), ("F9", "RSVD_F9"), ("G7", "RSVD_G7")],
   right=[("B9", "RF_IN"), None, ("C1", "RSVD"), ("C5", "RSVD"), ("D9", "RSVD"), ("E7", "RSVD"),
          ("G9", "RSVD"), ("J1", "RSVD"), ("J2", "RSVD"), ("J3", "RSVD"), ("J7", "RSVD"), None]
         + [(b, "GND") for b in _mia_gnd])

# ST LIS2DW12, LGA-12 (DS11811 rev 9, Table 1)
ic("LIS2DW12", "U", width=17.78, src="LIS2DW12 DS11811 rev 9 Table 1",
   left=[("9", "VDD"), ("10", "VDD_IO"), None, ("1", "SCL/SPC"), ("4", "SDA/SDI/SDO"),
         ("3", "SDO/SA0"), ("2", "CS")],
   right=[("12", "INT1"), ("11", "INT2"), None, ("5", "NC"), ("7", "RES"), ("6", "GND"), ("8", "GND")])

# TI TMUX1101, SC70-5 DCK (SCDS431, Table 5-1)
ic("TMUX1101", "U", width=12.7, src="TMUX1101 Table 5-1",
   left=[("1", "D"), ("4", "SEL")], right=[("2", "S"), ("5", "VDD"), ("3", "GND")])

# TI TPS62840 YBG (WCSP-6, 0.4 mm): SLVSEC6D pinout A1 GND, A2 VOS, B1 VIN, B2 SW, C1 EN, C2 VSET
ic("TPS62840YBG", "U", width=12.7, grow=1.27, src="TPS62840 DS SLVSEC6D, YBG pin functions",
   left=[("B1", "VIN"), ("C1", "EN"), ("C2", "VSET")], right=[("B2", "SW"), ("A2", "VOS"), ("A1", "GND")])

# pSemi PE4259, SC-70-6 (DOC-03694-5 Table 2: 1 RF1, 2 GND, 3 RF2, 4 CTRL, 5 RFC, 6 CTRL/VDD)
ic("PE4259", "U", width=15.24, src="pSemi PE4259 DS DOC-03694-5 Table 2; single-pin mode: CTRL high = RFC-RF1",
   left=[("1", "RF1"), ("3", "RF2"), None, ("4", "CTRL"), ("6", "VDD")],
   right=[("5", "RFC"), None, ("2", "GND")])

# TI TPD1E10B06 (pin 1 IO, pin 2 GND)
two("TPD1E10B06", "D", "esd")
two("R", "R", "r")
two("C", "C", "c")
two("L", "L", "l")
two("FerriteBead", "FB", "fb")
two("Crystal", "Y", "xtal")
# 4-pin crystal: 1 & 3 = crystal, 2 & 4 = case/GND
SYMS["Crystal_GND24"] = dict(pins=[("1", "1", 0, 3.81, 270), ("3", "3", 0, -3.81, 90),
                                   ("2", "2", -3.81, 0, 0), ("4", "4", 3.81, 0, 180)],
                             body=None, ref="Y", power=False, kind="xtal4", src="")
one("Antenna", "AE", "ant")
one("TestPad", "TP", "tp")
one("Pad", "J", "tp")
for p in ("GND", "+1V8", "+3V3_RF", "VBAT", "VBUS", "VSYS"):
    pwr(p)


def lib_symbol(name, prefixed=True):
    s = SYMS[name]
    full = f"{LIB}:{name}" if prefixed else name
    lines = [f"(symbol {q(full)}"]
    if s["power"]:
        lines.append("(power) (pin_numbers (hide yes)) (pin_names (offset 0) (hide yes))")
    else:
        lines.append("(pin_names (offset 1.016))" if s["kind"] == "ic" else "(pin_numbers (hide yes)) (pin_names (offset 0) (hide yes))")
    lines.append("(exclude_from_sim no) (in_bom yes) (on_board yes)")
    ref = s["ref"]
    if s["power"]:
        vy = -3.81 if s["kind"] == "gnd" else 3.81
        lines.append(f"(property \"Reference\" \"#PWR\" (at 0 {vy - 2.54} 0) {eff(hide=True)})")
        lines.append(f"(property \"Value\" {q(name)} (at 0 {vy} 0) {eff()})")
    else:
        top = s["body"][1] + 3.81 if s["body"] else 5.08
        lines.append(f"(property \"Reference\" {q(ref)} (at 0 {top} 0) {eff()})")
        lines.append(f"(property \"Value\" {q(name)} (at 0 {top - 1.778} 0) {eff()})")
    lines.append(f"(property \"Footprint\" \"\" (at 0 0 0) {eff(hide=True)})")
    lines.append(f"(property \"Datasheet\" \"\" (at 0 0 0) {eff(hide=True)})")
    lines.append(f"(property \"Description\" {q(s['src'])} (at 0 0 0) {eff(hide=True)})")
    g = []
    k = s["kind"]
    st = "(stroke (width 0.254) (type default))"
    if s["body"]:
        x0, y0, x1, y1 = s["body"]
        g.append(f"(rectangle (start {x0} {y0}) (end {x1} {y1}) {st} (fill (type background)))")
    elif k == "gnd":
        g.append(f"(polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)) {st} (fill (type none)))")
    elif k == "rail":
        g.append(f"(polyline (pts (xy -0.762 1.27) (xy 0 2.54) (xy 0.762 1.27)) {st} (fill (type none)))")
        g.append(f"(polyline (pts (xy 0 0) (xy 0 2.54)) {st} (fill (type none)))")
    elif k == "r":       # US-style zigzag
        g.append(f"(polyline (pts (xy 0 2.54) (xy 1.016 2.117) (xy -1.016 1.27) (xy 1.016 0.423) (xy -1.016 -0.423) "
                 f"(xy 1.016 -1.27) (xy -1.016 -2.117) (xy 0 -2.54)) {st} (fill (type none)))")
    elif k == "fb":
        g.append(f"(rectangle (start -1.016 2.54) (end 1.016 -2.54) {st} (fill (type outline)))")
    elif k == "c":
        g.append(f"(polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) {st} (fill (type none)))")
        g.append(f"(polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) {st} (fill (type none)))")
    elif k == "l":
        for yy in (1.905, 0.635, -0.635, -1.905):
            g.append(f"(arc (start 0 {yy + 0.635}) (mid 0.635 {yy}) (end 0 {yy - 0.635}) {st} (fill (type none)))")
    elif k == "esd":
        g.append(f"(polyline (pts (xy -1.27 1.27) (xy 1.27 1.27) (xy 0 -1.27) (xy -1.27 1.27)) {st} (fill (type none)))")
        g.append(f"(polyline (pts (xy -1.27 -1.27) (xy 1.27 -1.27)) {st} (fill (type none)))")
    elif k in ("xtal", "xtal4"):
        g.append(f"(rectangle (start -1.143 0.508) (end 1.143 -0.508) {st} (fill (type none)))")
        g.append(f"(polyline (pts (xy -1.778 1.27) (xy 1.778 1.27)) {st} (fill (type none)))")
        g.append(f"(polyline (pts (xy -1.778 -1.27) (xy 1.778 -1.27)) {st} (fill (type none)))")
    elif k == "ant":
        g.append(f"(polyline (pts (xy 0 -2.54) (xy 0 1.27) (xy -1.27 2.54) (xy 1.27 2.54) (xy 0 1.27)) {st} (fill (type none)))")
    elif k == "tp":
        g.append(f"(circle (center 0 0) (radius 0.762) {st} (fill (type none)))")
    lines.append(f"(symbol {q(name + '_0_1')} " + " ".join(g) + ")")
    pl = []
    for num, pname, x, y, ang in s["pins"]:
        ptype = "power_in" if s["power"] else "passive"
        if s["power"]:
            length = 0
        elif s["kind"] == "ic":
            length = s.get("pinlen", 2.54)
        elif s["kind"] == "tp":
            length = 1.778
        else:
            length = 1.27 if abs(x) + abs(y) > 3 else 0
            if s["kind"] in ("r", "c", "l", "fb", "esd", "xtal", "xtal4"):
                length = 1.27
            if s["kind"] == "c":
                length = 3.048          # run the leads up to the plates at +-0.762
            if s["kind"] == "ant":
                length = 0
        hide = " (hide yes)" if s["power"] else ""
        pl.append(f"(pin {ptype} line (at {x} {y} {ang}) (length {length}){hide} "
                  f"(name {q(pname)} {eff()}) (number {q(num)} {eff()}))")
    lines.append(f"(symbol {q(name + '_1_1')} " + " ".join(pl) + ")")
    lines.append("(embedded_fonts no))")
    return " ".join(lines)


# ---------------------------------------------------------------- sheets
POWER_NETS = {"GND", "+1V8", "+3V3_RF", "VBAT", "VBUS", "VSYS"}
# inter-sheet signals (hierarchical); everything else is a local label
SHEET_PINS = {
    "power": [("I2C_SDA", "bidirectional", "R"), ("I2C_SCL", "input", "R"), ("PMIC_INT", "output", "R"),
              ("LR_VIO", "output", "R")],
    "mcu": [("I2C_SDA", "bidirectional", "L"), ("I2C_SCL", "output", "L"), ("PMIC_INT", "input", "L"),
            ("UART_TX", "output", "L"), ("UART_RX", "input", "L"),
            ("ACC_INT1", "input", "R"), ("GNSS_TXRDY", "input", "R"), ("GNSS_RESET_N", "output", "R"),
            ("GNSS_EXTINT", "output", "R"), ("GNSS_EN", "output", "R"), ("LR_SCK", "output", "R"),
            ("LR_MOSI", "output", "R"), ("LR_MISO", "input", "R"), ("LR_NSS", "output", "R"),
            ("LR_IRQ", "input", "R"), ("LR_BUSY", "input", "R"), ("LR_NRESET", "output", "R")],
    "lora": [("LR_SCK", "input", "L"), ("LR_MOSI", "input", "L"), ("LR_MISO", "output", "L"),
             ("LR_NSS", "input", "L"), ("LR_IRQ", "output", "L"), ("LR_BUSY", "output", "L"),
             ("LR_NRESET", "input", "L"), ("LR_VIO", "input", "L"), ("ANT_915", "passive", "R")],
    "gnss": [("I2C_SDA", "bidirectional", "L"), ("I2C_SCL", "input", "L"), ("GNSS_TXRDY", "output", "L"),
             ("GNSS_RESET_N", "input", "L"), ("GNSS_EXTINT", "input", "L"), ("GNSS_EN", "input", "L")],
    "sensors": [("I2C_SDA", "bidirectional", "L"), ("I2C_SCL", "input", "L"), ("ACC_INT1", "output", "L")],
    "dock": [("UART_TX", "input", "R"), ("UART_RX", "output", "R")],
    "flex_pads": [("ANT_915", "passive", "R")],
}
SHEET_FILES = {k: k + ".kicad_sch" for k in SHEET_PINS}
SHEET_UUID = {k: U() for k in SHEET_PINS}
PAGE = {k: i + 2 for i, k in enumerate(SHEET_PINS)}

# Component lists: (ref, symbol, value, footprint, {pin: net}, note)   NC = no-connect
FP = dict(c0201="Capacitor_SMD:C_0201_0603Metric", c0402="Capacitor_SMD:C_0402_1005Metric",
          c0603="Capacitor_SMD:C_0603_1608Metric", r0201="Resistor_SMD:R_0201_0603Metric",
          r0402="Resistor_SMD:R_0402_1005Metric", l0201="Inductor_SMD:L_0201_0603Metric",
          l0402="Inductor_SMD:L_0402_1005Metric", l0603="Inductor_SMD:L_0603_1608Metric")
NC = "NC"


def cap(ref, val, a, b="GND", fp="c0402", note=""):
    return (ref, "C", val, FP.get(fp, fp), {"1": a, "2": b}, note)


def res(ref, val, a, b, fp="r0201", note=""):
    return (ref, "R", val, FP.get(fp, fp), {"1": a, "2": b}, note)


def ind(ref, val, a, b, fp="l0201", note=""):
    return (ref, "L", val, FP.get(fp, fp), {"1": a, "2": b}, note)


S = {}
S["power"] = [
    ("U2", "nPM1300-QEAA", "nPM1300-QEAA", "", {
        "21": "VBUS", "22": "VBUSOUT", "23": NC, "24": NC, "19": "VBAT", "18": "GND",
        "12": "+1V8", "13": "I2C_SDA", "14": "I2C_SCL", "15": "SHPHLD",
        "7": NC, "8": "PMIC_INT", "9": NC, "10": NC, "11": NC, "25": NC, "26": NC, "27": NC,
        "20": "VSYS", "4": "VSYS", "3": "SW1", "1": "+1V8", "2": "GND", "17": "VSET1",
        "5": "SW2", "32": "+3V3_RF", "6": "GND", "16": "VSET2",
        "28": "+1V8", "29": "LR_VIO", "30": "GND", "31": "GND", "33": "GND"},
     "PS v1.3 Table 34. LSIN/LSOUT unused -> GND as in Fig 63. NTC -> GND: disable NTC in BCHGDISABLESET."),
    ind("L101", "2.2uH 0806 DCR<400m", "SW1", "+1V8", fp="", note="PS Table 39"),
    ind("L102", "2.2uH 0806 DCR<400m", "SW2", "+3V3_RF", fp=""),
    cap("C101", "10uF", "+1V8", fp="c0603"), cap("C102", "10uF", "+3V3_RF", fp="c0603"),
    cap("C103", "10uF", "VSYS", fp="c0603"), cap("C104", "10uF", "VSYS", fp="c0603"),
    cap("C105", "1uF", "VBUS", fp="c0603"), cap("C106", "2.2uF X7R", "VBAT", fp="c0603"),
    cap("C107", "1uF", "VBUSOUT", fp="c0603"), cap("C108", "100nF", "+1V8", fp="c0201"),
    res("R101", "47k 1%", "VSET1", "GND", note="BUCK1 1.8 V at power-on (PS Table 17)"),
    res("R102", "390k 1%", "VSET2", "GND", note="BUCK2 3.3 V at power-on (250-500k, PS Table 18). SEQUENCING: SX1262 needs VBAT_IO(1V8) <= VBAT(3V3_RF) at all times; both bucks start together (tSTRT 1.2 ms) - scope-verify on first boards; FW must never disable BUCK2 while BUCK1 is on"),
    cap("C120", "1uF", "LR_VIO", fp="c0402", note="LOADSW1 output (PS Config 2 uses 1.0 uF). LOADSW1 = SX1262 VBAT_IO, off at power-on (PS 6.4); FW enables after both bucks are up"),
    ("TP101", "TestPad", "SHPHLD", "", {"1": "SHPHLD"}, "ship-mode exit / optional magnet switch"),
]
S["mcu"] = [
    ("U1", "nRF54L10-QFAA", "nRF54L10-QFAA", "", {
        "1": "XL1", "2": "XL2", "3": NC, "4": NC, "5": "LR_SCK", "6": "LR_MOSI", "7": "LR_MISO",
        "8": "LR_NSS", "9": "LR_IRQ", "39": "GNSS_RESET_N", "40": "GNSS_EXTINT", "41": "UART_TX",
        "42": "UART_RX", "37": "LR_BUSY", "38": "LR_NRESET", "11": "GNSS_EN",
        "12": NC, "13": NC, "14": NC, "15": NC, "16": NC, "17": NC, "18": "SWO", "19": NC, "20": NC, "21": NC,
        "10": "+1V8", "22": "+1V8", "36": "+1V8", "47": "+1V8", "48": "+1V8",
        "46": "DCC", "45": "DECD", "43": "DECA", "33": "DECA", "34": "XC1", "35": "XC2",
        "31": "RF24_0", "32": "GND", "23": "GNSS_TXRDY", "24": "ACC_INT1", "27": "I2C_SDA",
        "28": "I2C_SCL", "29": "PMIC_INT", "30": "NRST_PIN", "25": "SWDIO", "26": "SWDCLK",
        "44": "GND", "49": "GND"},
     "Nordic ref layout v0.8 config 1. VSS_PA (32): layout -> centre pad only."),
    cap("C201", "10uF", "+1V8", fp="c0402", note="VDD 47/48"), cap("C202", "100nF", "+1V8", fp="c0201"),
    cap("C203", "100nF", "+1V8", fp="c0201", note="VDD 10"), cap("C204", "100nF", "+1V8", fp="c0201", note="VDD 22"),
    cap("C205", "100nF", "+1V8", fp="c0201", note="VDD 36"),
    ind("L201", "4.7uH", "DCC", "DECD", fp="l0603"), cap("C206", "2.2uF", "DECD", fp="c0201"),
    ("FB201", "FerriteBead", "120R@100MHz 200mA", "Inductor_SMD:L_0201_0603Metric", {"1": "DECD", "2": "DECA"}, ""),
    cap("C207", "2.2uF", "DECA", fp="c0201"), cap("C208", "10nF", "DECA", fp="c0201"),
    cap("C209", "2.2nF", "DECA", fp="c0201"),
    ("Y201", "Crystal_GND24", "32MHz CL8pF +-40ppm 2016", "", {"1": "XC1", "3": "XC2", "2": "GND", "4": "GND"}, "no load caps"),
    ("Y202", "Crystal", "32.768kHz 9pF +-20ppm 2012", "", {"1": "XL1", "2": "XL2"}, "no load caps"),
    res("R201", "1k", "NRST_PIN", "NRESET"), cap("C210", "3.9pF", "NRST_PIN", fp="c0201"),
    ind("L202", "2.7nH LQP03HQ2N7B02", "RF24_0", "RF24_1", fp="l0201"),
    cap("C211", "1.5pF GJM0335C1E1R5WB01", "RF24_1", fp="c0201", note="GND to VSS_PA pin 32 only"),
    ind("L203", "3.5nH LQP03HQ3N5B02", "RF24_1", "RF24_2", fp="l0201"),
    cap("C212", "2.0pF GJM0335C1E2R0WB01", "RF24_2", fp="c0201", note="GND via to bottom layer only"),
    ind("L204", "3.5nH LQP03HQ3N5B02", "RF24_2", "RF24_3", fp="l0201"),
    cap("C213", "0.3pF", "RF24_3", fp="c0201"),
    cap("C214", "DNP", "RF24_3", fp="c0201", note="antenna match, shunt (tune)"),
    ind("L205", "0R", "RF24_3", "RF24_ANT", fp="l0201", note="antenna match, series (tune)"),
    cap("C215", "DNP", "RF24_ANT", fp="c0201", note="antenna match, shunt (tune)"),
    ("AE201", "Antenna", "2.4GHz chip antenna (TBD)", "", {"1": "RF24_ANT"}, ""),
    ("TP201", "TestPad", "SWDIO", "", {"1": "SWDIO"}, ""), ("TP202", "TestPad", "SWDCLK", "", {"1": "SWDCLK"}, ""),
    ("TP203", "TestPad", "nRESET", "", {"1": "NRESET"}, ""), ("TP204", "TestPad", "1V8", "", {"1": "+1V8"}, ""),
    ("TP205", "TestPad", "GND", "", {"1": "GND"}, ""), ("TP206", "TestPad", "SWO", "", {"1": "SWO"}, ""),
]
S["lora"] = [
    ("U7", "SX1262IMLTRT", "SX1262IMLTRT", "", {
        "1": "+3V3_RF", "10": "+3V3_RF", "11": "LR_VIO", "7": "VREG", "9": "DCC_SW", "3": "XTA", "4": "XTB",
        "19": "LR_NSS", "18": "LR_SCK", "17": "LR_MOSI", "16": "LR_MISO", "15": "LR_NRESET",
        "14": "LR_BUSY", "13": "LR_IRQ", "12": "LR_DIO2", "6": NC,
        "24": "VR_PA", "23": "RFO", "22": "RFI_N", "21": "RFI_P",
        "2": "GND", "5": "GND", "8": "GND", "20": "GND", "25": "GND"},
     "DS 5.2: VBAT_IO must be <= VBAT at all times -> 3V3_RF stays on whenever 1V8 is on."),
    cap("C301", "1uF", "+3V3_RF", note="ref C16"), cap("C302", "100nF", "+3V3_RF", fp="c0201", note="ref C18"),
    cap("C303", "100nF", "LR_VIO", fp="c0201", note="VBAT_IO, gated by nPM1300 LOADSW1"),
    ind("L301", "15uH", "DCC_SW", "VREG", fp="l0603", note="ref L7"), cap("C304", "470nF", "VREG", note="ref C17"),
    ("Y301", "Crystal_GND24", "32MHz 2016 (or TCXO on DIO3)", "", {"1": "XTA", "3": "XTB", "2": "GND", "4": "GND"}, "ref Q1"),
    # TX path, topology from Semtech E428V03A (AN1200.40 Fig 5); values = ref design BOM (915 MHz)
    cap("C305", "TBD", "VR_PA", fp="c0402", note="ref C1"), cap("C306", "TBD", "VR_PA", fp="c0402", note="ref C2"),
    ind("L302", "TBD", "VR_PA", "TXA", fp="l0402", note="ref L1 (PA bias)"),
    ind("L303", "TBD", "RFO", "TXA", fp="l0402", note="ref L2"),
    cap("C307", "TBD", "TXA", fp="c0402", note="ref C3"),
    ind("L304", "TBD", "TXA", "TXB", fp="l0402", note="ref L3"),
    cap("C308", "TBD", "TXA", "TXB", fp="c0402", note="ref C4 (across L3)"),
    cap("C309", "TBD", "TXB", fp="c0402", note="ref C5"),
    cap("C310", "TBD", "TXB", "TXC", fp="c0402", note="ref C6 (series, DC block)"),
    ind("L305", "TBD", "TXC", "TX_SW", fp="l0402", note="ref L4"),
    cap("C311", "TBD", "TX_SW", fp="c0402", note="ref C7"),
    # RX balun
    cap("C312", "TBD", "RFI_N", "RX_SW", fp="c0402", note="ref C11 (series, DC block)"),
    ind("L306", "TBD", "RFI_N", "RFI_P", fp="l0402", note="ref L6"),
    cap("C313", "TBD", "RFI_P", fp="c0402", note="ref C12"),
    cap("C314", "TBD", "RX_SW", fp="c0402", note="ref C13"),
    # switch: PE4259 single-pin mode, DIO2 (1.8 V) drives CTRL directly; SX1262 drives DIO2 high in TX
    ("U8", "PE4259", "PE4259-63", "Package_TO_SOT_SMD:SOT-363_SC-70-6",
     {"1": "TX_SW", "3": "RX_SW", "4": "LR_CTRL", "6": "LR_VIO", "5": "SW_COM", "2": "GND"},
     "LCSC C470892. Single-pin mode, VDD = LR_VIO (same rail as DIO2). CTRL high (>= 0.7 VDD) = RFC-RF1 = TX. "
     "P1dB 29.5 dBm min @ 1 GHz, VDD 1.8-2.3 V. All RF ports DC blocked (DS Table 7). C322 = RFC tuning cap (DS Table 3 note 2)."),
    cap("C315", "100nF", "LR_VIO", fp="c0201", note="PE4259 VDD bypass"),
    res("R301", "1k", "LR_DIO2", "LR_CTRL", note="series R on CTRL, as PE4259 eval board R1/R2"),
    # antenna side
    cap("C322", "DNP", "SW_COM", fp="c0402", note="PE4259 DS 5.01 Table 3 note 2: RFC tuning shunt, eval board 0.25 pF (2 x 0.5 pF series) at the pin"),
    cap("C319", "TBD", "SW_COM", "ANTA", fp="c0402", note="ref C8 (series, DC block)"),
    cap("C320", "TBD", "ANTA", fp="c0402", note="ref C9"),
    ind("L307", "TBD", "ANTA", "ANT_915", fp="l0402", note="ref L5"),
    cap("C321", "TBD", "ANT_915", fp="c0402", note="ref C10"),
]
S["gnss"] = [
    ("U3", "MIA-M10Q", "MIA-M10Q", "", dict(
        **{b: "GND" for b in _mia_gnd},
        **{"B1": "GNSS_1V8", "J4": "GNSS_1V8", "J5": NC, "J6": "GND", "C6": NC,
           "D1": "I2C_SDA", "E1": "I2C_SCL", "G1": "GNSS_TXD", "H1": "GNSS_RXD", "A6": "GNSS_EXTINT",
           "A7": NC, "F7": "GNSS_TXRDY", "C4": "GNSS_RESET_N", "C7": "GNSS_SAFEBOOT", "H9": NC,
           "A4": NC, "A5": "GND", "D2": "RSVD_D2E2", "E2": "RSVD_D2E2", "F9": "RSVD_F9", "G7": "RSVD_G7",
           "B9": "GNSS_RF", "C1": NC, "C5": NC, "D9": NC, "E7": NC, "G9": NC, "J1": NC, "J2": NC,
           "J3": NC, "J7": NC}),
     "IM R05: 1.8 V design (VIO_SEL to GND), supply 1.8 V +-2% (DS: V_IO 1.76 V min, 1.98 V abs max) -> TPS62840 (+-1.5%). TX_READY on PIO6."),
    ("U11", "TPS62840YBG", "TPS62840YBGR", "", {"B1": "VSYS", "C1": "GNSS_EN", "C2": "GND", "B2": "GNSS_SW",
                                                "A2": "GNSS_1V8", "A1": "GND"},
     "GNSS-only 1.8 V buck from VSYS. VSET=GND -> 1.8 V, +-1.5% (PWM, full temp). 60 nA IQ, 25 nA off. "
     "LCSC C2071139. tSS 120 us -> ~67 us/V, inside MIA V_IO ramp limit 25..35000 us/V (DS Table 12)."),
    ind("L401", "2.2uH", "GNSS_SW", "GNSS_1V8", fp="l0603", note="TPS62840 L eff 1.51-2.9 uH; Isat >= 300 mA (MIA inrush 100 mA)"),
    cap("C401", "4.7uF", "VSYS", fp="c0402", note="TPS62840 input cap, close to VIN/GND"),
    cap("C402", "10uF", "GNSS_1V8", fp="c0402", note="TPS62840 COUT eff 3-40 uF after DC bias"),
    cap("C403", "100nF", "GNSS_1V8", fp="c0201", note="at MIA VCC/V_IO"),
    res("R403", "1M", "GNSS_EN", "GND", note="hold GNSS off while MCU is in reset/boot"),
    res("R401", "0R", "RSVD_F9", "GND", note="IM: future dual-band compatibility"),
    res("R402", "0R", "RSVD_G7", "GND", note="IM: crystal-variant compatibility"),
    cap("C404", "DNP", "GNSS_RF", fp="c0201", note="antenna match (tune)"),
    ind("L402", "0R", "GNSS_RF", "GNSS_ANT", fp="l0201", note="antenna match (tune)"),
    cap("C405", "DNP", "GNSS_ANT", fp="c0201", note="antenna match (tune)"),
    ("AE401", "Antenna", "ACAG0301-1575 (TBC)", "", {"1": "GNSS_ANT"}, ""),
    ("TP401", "TestPad", "GNSS_TXD", "", {"1": "GNSS_TXD"}, ""), ("TP402", "TestPad", "GNSS_RXD", "", {"1": "GNSS_RXD"}, ""),
    ("TP403", "TestPad", "SAFEBOOT_N", "", {"1": "GNSS_SAFEBOOT"}, ""),
]
S["sensors"] = [
    ("U6", "LIS2DW12", "LIS2DW12TR", "", {"9": "+1V8", "10": "+1V8", "1": "I2C_SCL", "4": "I2C_SDA",
                                         "3": "GND", "2": "+1V8", "12": "ACC_INT1", "11": NC,
                                         "5": "GND", "7": "GND", "6": "GND", "8": "GND"},
     "I2C mode (CS high), SA0 low -> address 0x18"),
    cap("C501", "100nF", "+1V8", fp="c0201"), cap("C502", "10uF", "+1V8", fp="c0402"),
    res("R501", "4.7k", "I2C_SDA", "+1V8", note="shared bus pull-up (check rise time at 1.8 V)"),
    res("R502", "4.7k", "I2C_SCL", "+1V8"),
]
S["dock"] = [
    ("J601", "Pad", "DOCK_VBUS", "", {"1": "VBUS"}, "dock target"),
    ("J602", "Pad", "DOCK_GND", "", {"1": "GND"}, "dock target"),
    ("J603", "Pad", "DOCK_TX", "", {"1": "DOCK_TX"}, "dock target (collar out)"),
    ("J604", "Pad", "DOCK_RX", "", {"1": "DOCK_RX"}, "dock target (collar in)"),
    ("D601", "TPD1E10B06", "TPD1E10B06", "", {"1": "VBUS", "2": "GND"}, ""),
    ("D602", "TPD1E10B06", "TPD1E10B06", "", {"1": "DOCK_TX", "2": "GND"}, ""),
    ("D603", "TPD1E10B06", "TPD1E10B06", "", {"1": "DOCK_RX", "2": "GND"}, ""),
    ("U4", "TMUX1101", "TMUX1101DCK", "", {"1": "UART_TX", "2": "DOCK_TX", "4": "DOCK_SEL", "5": "+1V8", "3": "GND"}, ""),
    ("U5", "TMUX1101", "TMUX1101DCK", "", {"1": "UART_RX", "2": "DOCK_RX", "4": "DOCK_SEL", "5": "+1V8", "3": "GND"}, ""),
    cap("C601", "100nF", "+1V8", fp="c0201"), cap("C602", "100nF", "+1V8", fp="c0201"),
    res("R601", "100k", "VBUS", "DOCK_SEL"), res("R602", "150k", "DOCK_SEL", "GND"),
    res("R603", "1M DNP", "DOCK_TX", "GND"), res("R604", "1M DNP", "DOCK_RX", "GND"),
]
S["flex_pads"] = [
    ("J701", "Pad", "FLEX_ANT", "", {"1": "ANT_915"}, "915 MHz feed (via beside pad)"),
    ("J702", "Pad", "FLEX_MECH", "", {"1": NC}, "mechanical anchor only"),
    ("J703", "Pad", "FLEX_GND", "", {"1": "GND"}, "counterpoise / battery return"),
    ("J704", "Pad", "FLEX_VBAT", "", {"1": "VBAT"}, "battery +"),
]

NOTES = {
    "power": "nPM1300 (QFN32). BUCK1 = +1V8 main rail (VSET1 47k). BUCK2 = +3V3_RF (VSET2 390k, on at power-up and\n"
             "kept on: SX1262 needs VBAT >= VBAT_IO at all times). SX1262 VBAT_IO = LR_VIO via LOADSW1 (LSIN1 = +1V8), off at\n"
             "power-on; FW: enable LOADSW1 only after boot, disable it before ship mode / BUCK2 off. LOADSW2 unused (to GND).\n"
             "Charger from VBUS (dock). NTC tied to GND -> disable NTC in BCHGDISABLESET. Buck accuracy is +-5% (PS 6.3.6).",
    "mcu": "nRF54L10-QFAA, Nordic reference config 1 (internal DC/DC). 2.4 GHz match per Nordic ref v0.8;\n"
           "C211 ground to VSS_PA only; C212 ground to bottom layer only; inner planes cut out under the match.\n"
           "UART_TX/RX = UARTE20 on P1.13/P1.14. GNSS_EN on P2.00. SWD + SWO + nRESET to internal test pads.",
    "lora": "SX1262 + PE4259 switch (as Semtech's own reference designs). Topology from Semtech E428V03A (AN1200.40 Fig 5);\n"
            "TBD values = that design's 915 MHz BOM. PE4259 single-pin mode: VDD = LR_VIO, CTRL = DIO2 via 1k;\n"
            "CTRL high = RFC-RF1 = TX (RF1 pin 1), low = RFC-RF2 = RX (RF2 pin 3). P1dB 29.5 dBm min at VDD 1.8 V.\n"
            "VBAT_IO = LR_VIO (nPM1300 LOADSW1). FW: hold LR_NRESET low and SPI/NSS low or hi-Z until LR_VIO is on, then reset.",
    "gnss": "MIA-M10Q, 1.8 V design (VCC = V_IO, VIO_SEL to GND). u-blox requires 1.8 V +-2%: nPM1300 buck is +-5%,\n"
            "so GNSS_1V8 comes from a TPS62840 buck (+-1.5%) off VSYS, EN = GNSS_EN with 1M pull-down (also powers GNSS down).\n"
            "TX_READY on PIO6 (F7), configure via CFG-TXREADY. No RTC crystal: RTC_O to GND, RTC_I open. D2-E2 tied.",
    "sensors": "LIS2DW12 in I2C mode (CS high, SA0 low = 0x18). INT1 = motion wake. Shared I2C pull-ups live here.",
    "dock": "Dock targets on the underside. TMUX1101 (SEL high = on) closed only when VBUS present, so undocked\n"
            "TX/RX contacts sit at 0 V. SEL divider 100k/150k from VBUS (SEL fail-safe to 5.5 V).",
    "flex_pads": "Flex pads in the underside centre strip (docs/interface.md). Footprints: custom, from electrical/flex/flex_strip.dxf.",
}

# ---------------------------------------------------------------- placement inside a sheet
used_syms = set()
pwr_count = [0]
netcheck = []


def place_component(comp, X, Y, sheet, out):
    ref, sym, val, fp, pinmap, note = comp
    s = SYMS[sym]
    spec = ""
    if not s["body"] and " " in val and not val.startswith("DNP"):
        val, spec = val.split(" ", 1)
        if "DNP" in spec:
            val, spec = val + " DNP", spec.replace("DNP", "").strip()
    used_syms.add(sym)
    sp = f"/{ROOT_UUID}/{SHEET_UUID[sheet]}"
    body_top = Y - (s["body"][1] + 3.81 if s["body"] else 5.08)
    out.append(
        f"(symbol (lib_id {q(LIB + ':' + sym)}) (at {r2(X)} {r2(Y)} 0) (unit 1) (exclude_from_sim no) (in_bom yes) "
        f"(on_board yes) (dnp {'yes' if 'DNP' in val else 'no'}) (uuid {q(U())})\n"
        f"  (property \"Reference\" {q(ref)} (at {r2(X + (0 if s['body'] else 2.54))} {r2(body_top if s['body'] else Y - 1.27)} 0) {eff(None if s['body'] else 'left')})\n"
        f"  (property \"Value\" {q(val)} (at {r2(X + (0 if s['body'] else 2.54))} {r2(body_top + 1.778 if s['body'] else Y + 1.27)} 0) {eff(None if s['body'] else 'left')})\n"
        f"  (property \"Footprint\" {q(fp)} (at {r2(X)} {r2(Y)} 0) {eff(hide=True)})\n"
        f"  (property \"Datasheet\" \"\" (at {r2(X)} {r2(Y)} 0) {eff(hide=True)})\n"
        f"  (property \"Description\" {q(note)} (at {r2(X)} {r2(Y)} 0) {eff(hide=True)})\n"
        f"  (property \"Spec\" {q(spec)} (at {r2(X)} {r2(Y)} 0) {eff(hide=True)})\n"
        + "".join(f"  (pin {q(p[0])} (uuid {q(U())}))\n" for p in s["pins"])
        + f"  (instances (project {q(PROJECT)} (path {q(sp)} (reference {q(ref)}) (unit 1))))\n)\n")
    hier = {p[0] for p in SHEET_PINS[sheet]}
    for num, pname, px, py, ang in s["pins"]:
        net = pinmap.get(num)
        assert net is not None, f"{ref} pin {num} unassigned"
        ex, ey = X + px, Y - py               # library y-up -> sheet y-down
        netcheck.append((sheet, ref, val, num, pname, net))
        if net == NC:
            out.append(f"(no_connect (at {r2(ex)} {r2(ey)}) (uuid {q(U())}))\n")
            continue
        # stub direction: away from body
        dx, dy = {0: (-1, 0), 180: (1, 0), 270: (0, -1), 90: (0, 1)}[ang]
        L = 2.54
        sx, sy = ex + dx * L, ey + dy * L
        out.append(f"(wire (pts (xy {r2(ex)} {r2(ey)}) (xy {r2(sx)} {r2(sy)})) (stroke (width 0) (type default)) (uuid {q(U())}))\n")
        if net in POWER_NETS:
            pwr_count[0] += 1
            pref = f"#PWR{pwr_count[0]:03d}"
            used_syms.add(net)
            out.append(f"(symbol (lib_id {q(LIB + ':' + net)}) (at {r2(sx)} {r2(sy)} 0) (unit 1) (exclude_from_sim no) "
                       f"(in_bom yes) (on_board yes) (dnp no) (uuid {q(U())})\n"
                       f"  (property \"Reference\" {q(pref)} (at {r2(sx)} {r2(sy)} 0) {eff(hide=True)})\n"
                       f"  (property \"Value\" {q(net)} (at {r2(sx)} {r2(sy + (3.81 if net == 'GND' else -3.81))} 0) {eff()})\n"
                       f"  (property \"Footprint\" \"\" (at {r2(sx)} {r2(sy)} 0) {eff(hide=True)})\n"
                       f"  (property \"Datasheet\" \"\" (at {r2(sx)} {r2(sy)} 0) {eff(hide=True)})\n"
                       f"  (property \"Description\" \"\" (at {r2(sx)} {r2(sy)} 0) {eff(hide=True)})\n"
                       f"  (pin \"1\" (uuid {q(U())}))\n"
                       f"  (instances (project {q(PROJECT)} (path {q(sp)} (reference {q(pref)}) (unit 1))))\n)\n")
            continue
        lang, just = {(-1, 0): (180, "right bottom"), (1, 0): (0, "left bottom"),
                      (0, -1): (90, "left bottom"), (0, 1): (270, "right bottom")}[(dx, dy)]
        if net in hier:
            shape = [p[1] for p in SHEET_PINS[sheet] if p[0] == net][0]
            hj = {180: "right", 0: "left", 90: "left", 270: "right"}[lang]
            out.append(f"(hierarchical_label {q(net)} (shape {shape}) (at {r2(sx)} {r2(sy)} {lang}) "
                       f"(fields_autoplaced yes) {eff(hj)} (uuid {q(U())}))\n")
        else:
            out.append(f"(label {q(net)} (at {r2(sx)} {r2(sy)} {lang}) (fields_autoplaced yes) {eff(just)} (uuid {q(U())}))\n")


def sym_extent(sym):
    s = SYMS[sym]
    if s["body"]:
        x0, y0, x1, y1 = s["body"]
        return (x1 - x0) + 2 * G + 28, (y0 - y1) + 2 * G + 10
    return 15.24, 20.32


def build_sheet(name):
    out = []
    comps = S[name]
    ics = [c for c in comps if SYMS[c[1]]["body"]]
    small = [c for c in comps if not SYMS[c[1]]["body"]]
    paper_w, paper_h = (420, 297)
    # ICs in a row from the left, passives in a grid below/right
    x, ymax = 35.56, 0
    y_top = 50.8
    for c in ics:
        w, h = sym_extent(c[1])
        X = r2(round((x + w / 2) / G) * G)
        Y = r2(round((y_top + h / 2) / G) * G)
        place_component(c, X, Y, name, out)
        x += w + 10
        ymax = max(ymax, y_top + h)
    cols_x0 = 35.56
    gx, gy = cols_x0, max(ymax + 12.7, 140) if ics else 60.96
    if x > 300 or gy > 200:
        gy = min(gy, 200)
    pitch_x, pitch_y = 25.4, 25.4
    for c in small:
        X = r2(round(gx / G) * G)
        Y = r2(round(gy / G) * G)
        place_component(c, X, Y, name, out)
        # value/ref note text beside small parts is in properties
        gx += pitch_x
        if gx > paper_w - 30:
            gx = cols_x0
            gy += pitch_y
    out.append(f"(text {q(NOTES[name])} (exclude_from_sim no) (at 35.56 25.4 0) {eff('left top')} (uuid {q(U())}))\n")
    return out, gy


def title(t, c1, c2=""):
    return (f"(title_block (title {q(t)}) (date {q(DATE)}) (rev \"A\") (comment 1 {q(c1)}) (comment 2 {q(c2)}))\n")


sheet_bodies = {}
for name in SHEET_PINS:
    body, _ = build_sheet(name)
    sheet_bodies[name] = body

# ---------------------------------------------------------------- write sub-sheets
libsyms_txt = None


def lib_symbols_block():
    return "(lib_symbols\n" + "\n".join(lib_symbol(n) for n in sorted(used_syms)) + "\n)\n"


for name in SHEET_PINS:
    txt = (f"(kicad_sch (version {VER}) (generator \"eeschema\") (generator_version \"{GENV}\")\n"
           f"(uuid {q(U())})\n(paper \"A3\")\n"
           + title(f"cattraxV2 main board — {name}", "Generated from datasheets by tools/gen_board_schematic.py",
                   "Connections by labels at pin stubs; tidy into a readable drawing as you go")
           + lib_symbols_block() + "".join(sheet_bodies[name]) + "(embedded_fonts no)\n)\n")
    open(os.path.join(OUT, SHEET_FILES[name]), "w").write(txt)

# ---------------------------------------------------------------- root
PLACE = {"power": (50.8, 45.72), "dock": (50.8, 101.6), "flex_pads": (50.8, 139.7),
         "mcu": (172.72, 45.72), "gnss": (299.72, 45.72), "sensors": (299.72, 99.06), "lora": (299.72, 134.62)}
root_items = []
for name, pins in SHEET_PINS.items():
    x, y = PLACE[name]
    w = 45.72 if name == "mcu" else 40.64
    nl = sum(1 for p in pins if p[2] == "L"); nr = len(pins) - nl
    h = max(nl, nr, 2) * 2 * G + 2 * G
    s = [f"(sheet (at {x} {y}) (size {w} {r2(h)}) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) "
         f"(fields_autoplaced yes) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000)) (uuid {q(SHEET_UUID[name])})\n"
         f"  (property \"Sheetname\" {q(name)} (at {x} {r2(y - 0.7116)} 0) {eff('left bottom')})\n"
         f"  (property \"Sheetfile\" {q(SHEET_FILES[name])} (at {x} {r2(y + h + 0.5846)} 0) {eff('left top')})\n"]
    il = ir = 0
    for pin, typ, side in pins:
        if side == "L":
            il += 1; py = y + il * 2 * G; px = x; ang = 180; just = "left"; ex = x - 2 * G; la, lj = 180, "right bottom"
        else:
            ir += 1; py = y + ir * 2 * G; px = x + w; ang = 0; just = "right"; ex = x + w + 2 * G; la, lj = 0, "left bottom"
        s.append(f"  (pin {q(pin)} {typ} (at {r2(px)} {r2(py)} {ang}) (uuid {q(U())}) {eff(just)})\n")
        root_items.append(f"(wire (pts (xy {r2(px)} {r2(py)}) (xy {r2(ex)} {r2(py)})) (stroke (width 0) (type default)) (uuid {q(U())}))\n")
        root_items.append(f"(label {q(pin)} (at {r2(ex)} {r2(py)} {la}) (fields_autoplaced yes) {eff(lj)} (uuid {q(U())}))\n")
    s.append(f"  (instances (project {q(PROJECT)} (path \"/{ROOT_UUID}\" (page {q(str(PAGE[name]))}))))\n)\n")
    root_items.append("".join(s))
root = (f"(kicad_sch (version {VER}) (generator \"eeschema\") (generator_version \"{GENV}\")\n"
        f"(uuid {q(ROOT_UUID)})\n(paper \"A3\")\n"
        + title("cattraxV2 main board — top level", "Generated from datasheets by tools/gen_board_schematic.py",
                "Power rails are global power symbols: +1V8, +3V3_RF, VBAT, VBUS, GND")
        + "(lib_symbols)\n"
        + f"(text {q('Blocks: power (nPM1300) | mcu (nRF54L10 + 2.4 GHz) | lora (SX1262 + PE4259 + 915 match) | gnss (MIA-M10Q + TPS62840)' + chr(10) + 'sensors (LIS2DW12 + I2C pull-ups) | dock (targets, ESD, TMUX1101) | flex_pads (ANT, MECH, GND, VBAT)' + chr(10) + 'Pin->net table for review: electrical/board/netlist_check.csv')} (exclude_from_sim no) (at 50.8 20.32 0) {eff('left top')} (uuid {q(U())}))\n"
        + "".join(root_items)
        + "(sheet_instances (path \"/\" (page \"1\")))\n(embedded_fonts no)\n)\n")
open(os.path.join(OUT, PROJECT + ".kicad_sch"), "w").write(root)

# ---------------------------------------------------------------- library + table + check csv
libtxt = (f"(kicad_symbol_lib (version 20241209) (generator \"kicad_symbol_editor\") (generator_version \"{GENV}\")\n"
          + "\n".join(lib_symbol(n, prefixed=False) for n in sorted(SYMS)) + "\n)\n")
open(os.path.join(OUT, f"{LIB}.kicad_sym"), "w").write(libtxt)
open(os.path.join(OUT, "sym-lib-table"), "w").write(
    '(sym_lib_table\n  (version 7)\n  (lib (name "cattraxv2")(type "KiCad")(uri "${KIPRJMOD}/cattraxv2.kicad_sym")(options "")(descr "Project symbols, pin tables from datasheets"))\n)\n')
with open(os.path.join(OUT, "netlist_check.csv"), "w") as f:
    f.write("sheet,ref,value,pin,pin_name,net\n")
    for r in netcheck:
        f.write(",".join('"' + str(x).replace('"', "'") + '"' for x in r) + "\n")


# sanity: balanced parens
def balanced(path):
    d, ins, esc = 0, False, False
    for ch in open(path, encoding="utf-8").read():
        if ins:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': ins = False
        elif ch == '"': ins = True
        elif ch == "(": d += 1
        elif ch == ")":
            d -= 1
            assert d >= 0, path
    assert d == 0 and not ins, path


for fn in os.listdir(OUT):
    if fn.endswith((".kicad_sch", ".kicad_sym")) or fn == "sym-lib-table":
        balanced(os.path.join(OUT, fn))
print("ok:", sorted(os.listdir(OUT)), "components:", sum(len(v) for v in S.values()), "pins:", len(netcheck))
