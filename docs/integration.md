# Note to the integration session (from the mechanical session, 2026-11-11, updated 2026-11-12)

The mechanical redesign (see "Redesign decisions" in `hardware/respin/handoff_mechanical.md`)
touches the shared interface in these places. Nothing in `handoff_shared_interface.md` has been
changed for them yet; please decide and update it.

## 1. Dock face and target height
- The tracker case gets a flat, bare PETG neck face, flush with the band's neck face; the rest of
  the case is covered in silicone. The four dock targets finish flush in that face.
- Target height is now a mechanical parameter, 1.5 mm for now (shared interface says ~3 mm tall,
  Ø3.2). The user is looking for the shortest Mill-Max target; that choice fixes the case height.
- Proposed: two small locating dimples in the bare neck face for pins on the dock, so the pogos
  land on the targets. Dimple size and position need to be agreed with the dock design.

## 2. Breakaway detection (idea, needs electrical input)
- The user would like the tracker to report when the magnetic breakaway opens.
- Suggested: a micropower Hall switch on the flex at the pod end (about x = 60–66, near the pod-lid
  flange), sensing the cap's clasp magnet. This needs a third trace on the flex (currently GND and
  VBAT only) back to an nRF54L10 GPIO.
- Zero-hardware fallback: infer it from the accelerometer (long stillness, tracker no longer on top).
- Not recommended: electrical contacts across the clasp (wet, exposed, add friction).

## 3. Battery (updated 2026-11-12, corrected from the datasheets)
- Interim: 602030, 6 × 20 × 30 mm, 300 mAh (was 802025, 350 mAh).
- Likely next: a Grepow curved cell. Samples requested (5 each, bare cells, no PCM). Full datasheet
  check: `claude/cell_datasheet_checks_2026-11-12.md`.
  - **GRP751538**: 440 mAh, 15 × 38.1 mm arc × 6.94 mm (7.50 swollen), **4.40 V max charge**,
    2C charge/discharge (≤0.2C and 4.35 V below 10 °C). Pre-curved along its length at inner
    **R52.4 mm**. First choice.
  - **GRP402425**: 225 mAh, 24.2 × 25.09 mm arc × 4.05 mm, **4.35 V max charge**, 200 mA max
    charge, **100 mA max continuous discharge** (500 mA for 3 s), no charging below 10 °C.
    Radius not stated.
  - Ask Grepow: the 225's radius, and whether the 440 can be made at R ≈ 37–38 mm.
  - Proposed: nPM1300 VTERM 4.35 V for either cell (verify the step exists in the PS); charge
    current ≤88 mA; NTC needed for the cold-charge limits. Check the 24 h power budget.

## 4. Cell protection at the battery, on the flex (new, 2026-11-12)
- With bare cells there is no protection PCB. The user wants, at minimum, a protection IC at the
  battery end of the flex. Reason: the cell is in the pod, 60+ mm of flex from the board, so a
  short on the leads, BAT pads or flex traces is upstream of anything on the main board. The
  nPM1300's charger is the primary control; the cell-end protector is the independent backup.
- Suggested placement: between the BAT+/BAT− pads (x = 67.5–70.5) and the bypass cap / ferrite
  beads (x ≈ 60–64), within the 8 mm flex width. A one-chip protector with integrated FETs keeps
  it to one or two parts.
- Height: under about 2 mm of silicone above the flex, so parts ≤ ~1.2 mm tall.
- Thresholds: with VTERM 4.35 V on both cells, an overcharge detect around 4.425–4.45 V suits
  both; overdischarge ~2.8–3.0 V (both cells cut off at 3.0 V). 4.2 V-class protectors would cut
  off early. If the 440 is charged to 4.40 V it needs a ~4.45–4.475 V part instead.
- This adds parts and pads to the flex (jointly owned): update `flex_strip.py` and the shared
  interface.

## 5. Flex tail and cap
- Fit-and-trim cap: the tail is cut just past the pin key after fitting, so the flex tail end
  (bare, beyond x ≈ −62) gets trimmed. No change to the copper.
- Clasp magnets (two Ø8 × 4.8 mm N52 discs) at the pod tip and in the cap nose. At the smallest
  setting the antenna copper end is still about 31 mm away, but tune the antenna on the cast band
  with the magnets in place.

## 6. No interface change, for information
- Pod-lid anchor flange lowered to 0.6–1.6 mm so the flex (1.6 mm) lies on top of it.
