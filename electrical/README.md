# electrical

Brief: `docs/electrical.md`. Shared numbers: `docs/interface.md`.

| Folder | What |
|---|---|
| `board/` | Main board KiCad project (6-layer, 17 × 20 mm, JLC06161H-3313), not started yet. `connections_nrf54l10.csv` is the draft pin/net table. Release outputs go in `board/fab/<rev>/` (Gerber, BOM, CPL). |
| `flex/` | `flex_strip.py` → `flex_strip.dxf`/`.png` (layers EDGE, TOP_CU, BOT_CU, HOLES, BOARD, PARTS; 1 unit = 1 mm). Jointly owned with mechanical. **Not yet updated** for the 2026-11-12 interface changes (223 mm strip, pod section, Hall sensor, tail holes). |
| `dock/` | Pogo dock: VBUS, GND, SWDIO, SWCLK; series resistors in SWD and probe VTref wait (`docs/checks/2026-11-10-power-and-io.md` §4). |
| `kicad_libs/` | Submodule `wdawson61/kicad_libs`. Run `git submodule update --init` after cloning. |
