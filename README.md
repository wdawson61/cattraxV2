# cattraxV2

LoRa + GNSS cat collar tracker for a 26-acre property (gateway: RAK7289V2 on TTN).

V2 is a clean start: nRF54L10 + SX1262 + MIA-M10Q + nPM1300 on a 17 × 20 mm six-layer board,
a dipole and power arm on a single flex strip cast into a silicone band, and a curved
LiPo cast into a pod on the band. The previous design (STM32/Murata 1SJ, board "cattrax.6")
is archived in [wdawson61/cattrax](https://github.com/wdawson61/cattrax).

## Layout

| Path | What | Owner |
|---|---|---|
| `docs/interface.md` | Shared mech ⇄ elec interface: the fixed numbers both sides design to | both |
| `docs/electrical.md`, `docs/mechanical.md` | Design briefs, one per domain | elec / mech |
| `docs/integration.md` | Open cross-domain items | integration |
| `docs/notes/` | Dated handoff notes between domains | — |
| `docs/checks/` | Datasheet checks behind design decisions | — |
| `docs/decisions/` | Decision log | — |
| `datasheets/` | Local PDFs by subsystem (not committed) + `index.md` (committed) | — |
| `electrical/board/` | Main board KiCad project, pin/connection table, fab outputs | elec |
| `electrical/flex/` | Flex strip generator (`flex_strip.py` → DXF/PNG) | both |
| `electrical/dock/` | Pogo charging/SWD dock | elec |
| `electrical/kicad_libs/` | Shared KiCad libraries (submodule) | elec |
| `mechanical/cad/` | CadQuery scripts for case, pod, cap, clasp, mould | mech |
| `mechanical/sheets/` | Section and preview sheets | mech |
| `mechanical/tests/`, `mechanical/casting/` | Test pieces, pull tests, casting log | mech |
| `mechanical/phantom/` | 72 mm saline-bottle neck phantom | mech |
| `rf/` | Antenna models, VNA sweeps, tuning log | elec |
| `firmware/` | Zephyr (nRF Connect SDK) application and board definition | fw |
| `tools/` | Calibration, power budget, TTN payload formatter | — |

## Getting started

```sh
git clone --recurse-submodules https://github.com/wdawson61/cattraxV2.git
```

- **Mechanical:** see `mechanical/README.md` (CadQuery; generated STEP/STL are not committed).
- **Firmware:** see `firmware/README.md` (nRF Connect SDK, freestanding application).
- **Datasheets:** see `datasheets/index.md`; PDFs are kept locally, not in git.
