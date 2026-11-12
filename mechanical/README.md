# mechanical

CadQuery (Python) scripts. STEP opens in Fusion/FreeCAD as solids; STL is for printing on the
Prusa MK3. Brief: `docs/mechanical.md`. Shared numbers: `docs/interface.md`.

| Folder | What |
|---|---|
| `cad/` | Current (v3) scripts. `collar_parts.py` holds the ring frame and the v2 tracker case that everything imports. |
| `out/` | Generated STEP/STL. Not committed; regenerate, and attach to a GitHub Release at milestones. |
| `sheets/` | Section and preview PNGs (committed). |
| `tests/` | Clasp and other test pieces, plus pull-test results. |
| `casting/` | Silicone process notes and the cast log. |
| `phantom/` | `collar_mockup.py`: the 72 mm saline-bottle neck phantom (still has the cattrax.6 tray). |

## Regenerating

Scripts write to the current directory and import their siblings from the script's own folder,
so run them from `out/`:

```sh
cd mechanical/out
python3 ../cad/pod_v3.py          # v3_*  pod silicone, cell, clasp insert, band stub
python3 ../cad/cap_screw.py       # v3s_* cap shell/base, M1.6 hardware
python3 ../cad/sensor_h.py        # Hall sensor tongue/stiffener geometry
python3 ../cad/collar_mould_v3.py # v3m_* mould halves, band cast, assembly
python3 ../cad/sections_h.py      # v3h_* + section data (scratch in /tmp)
```

`collar_mould.py` is the v2 mould; `collar_mould_v3.py` imports it for the case envelope.
