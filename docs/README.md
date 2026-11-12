# docs

Work is split into three sessions/domains — electrical, mechanical and integration — and each
only edits its own documents. Cross-domain changes go through a dated note in `notes/`, and
anything both sides rely on lives in `interface.md`.

| File | Role |
|---|---|
| `interface.md` | The contract. Change only by agreement; note the change in both briefs. |
| `electrical.md` | Electrical/layout brief: power tree, parts, pinout, layout rules, open items. |
| `mechanical.md` | Mechanical brief: band, case, pod, clasp, cap, mould, casting, open items. |
| `integration.md` | Cross-domain items waiting for a decision. |
| `notes/YYYY-MM-DD-<from>-to-<to>.md` | Handoff notes. |
| `checks/YYYY-MM-DD-<topic>.md` | Datasheet checks, with the source document and revision. |
| `decisions/` | Decision log. |

## Old paths in these documents

These files were written in the cattrax.6 repo and still use its paths. Mapping:

| Written as | Now |
|---|---|
| `hardware/respin/handoff_shared_interface.md` | `docs/interface.md` |
| `hardware/respin/handoff_electrical.md` | `docs/electrical.md` |
| `hardware/respin/handoff_mechanical.md` | `docs/mechanical.md` |
| `claude/note_to_integration_2026-11-11.md` | `docs/integration.md` |
| `claude/note_to_electrical_2026-11-1x.md` | `docs/notes/2026-11-1x-mech-to-elec.md` |
| `claude/electrical_datasheet_checks_2026-11-10.md` | `docs/checks/2026-11-10-power-and-io.md` |
| `claude/cell_datasheet_checks_2026-11-12.md` | `docs/checks/2026-11-12-cells.md` |
| `claude/hall_sensor_datasheet_checks_2026-11-12.md` | `docs/checks/2026-11-12-hall-sensor.md` |
| `hardware/respin/connections_draft_nrf54l10.csv` | `electrical/board/connections_nrf54l10.csv` |
| `hardware/respin/cad_v3_pod/*.py` | `mechanical/cad/` |
| `hardware/respin/cad_v3_pod/*.png` | `mechanical/sheets/` |
| `collar_mockup.zip` → `flex_strip.py` | `electrical/flex/` |
| `collar_mockup.zip` → `collar_mockup.py` | `mechanical/phantom/` |
| `hardware/datasheets/`, `docs/*.pdf` | `datasheets/<subsystem>/` |
| `hardware/respin/cad/`, `cad_v2/` (superseded) | not carried over; in the cattrax repo |
