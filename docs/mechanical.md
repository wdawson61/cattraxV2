# Handoff brief – cat collar tracker: band, enclosure, casting (mechanical)

Context for a new session. Attach `collar_mockup.zip` (all scripts, STEP/STL, README) and
`handoff_shared_interface.md`. The fixed dimensions both sessions share are in the shared
interface; this brief adds the mechanical decisions and open work.

## Project
- A LoRa + GPS cat tracker for a 26-acre property. The gateway is a RAK7289V2 on TTN.
- This is a respin of the KiCad board "cattrax.6", fabbed and assembled at JLCPCB.
- Goals: an antenna built into the collar, a sealed potted enclosure with a pogo dock, range no
  worse than today, minimum board size, lower cost, and the battery in a pod on the band.
- Preference: always check the relevant datasheets and design docs, and ask for help finding them
  if needed.
- Tools: CadQuery (Python) scripts. The user opens the STEP files in Fusion or FreeCAD.

## Redesign decisions (2026-11-11): sleeker collar
These supersede the older items further down where they conflict. First version modelled
2026-11-11: see "v2 CAD" below.
- **Full silicone overmould.** The case and pod are covered by a 0.6–0.8 mm silicone skin as well as
  the band, so the printed parts become an inner frame (layer lines, glue lines and edges hidden).
  This needs a closed two-part mould (base + shaped lid, pour hole and vents) instead of the
  open-top tray in `full_collar_mould.py` v1.
- **Tracker case: a pebble, printed as two glued halves.** A tray (neck side: dock-target windows,
  flex slots) plus a domed cover, each printed open side down. In plan view about 19.5 mm wide at
  the board, tapering smoothly into the 12 mm band over about 10 mm at each end; the top is a
  flattened dome.
- **Dock face: option 1, bare PETG.** The case's flat neck face is left bare and finishes flush with
  the band's neck face. As modelled, the case sits in a 0.3 mm pocket in a flat land on the mould
  core (both parts are hard PETG, so a crush rib wouldn't crush); the face ends 0.3 mm proud of the
  band. Any silicone film peels off PETG. Add two small locating dimples for the dock's pins.
  Rejected: skinned face with wells at each target, proud targets through the skin, masking.
- **Dock target height is a parameter, 1.5 mm for now** (was 3 mm). The user is checking the
  shortest Mill-Max targets; this mostly sets the case height (about 7 → 5.5 mm).
- **Cell (2026-11-12): Grepow GRP751538 curved, 440 mAh** (15 wide × 38.1 arc × 6.94 mm, 7.50 mm
  max swollen, inner radius R52.39 ±1, 6.8 g, 4.40 V max). Samples ordered (5 each of GRP751538 and
  GRP402425, bare cells). Datasheet summary: `claude/cell_datasheet_checks_2026-11-12.md` (project).
  Interim before that was the flat 602030 (kept as `cad_v2/collar_parts_602030.py`). Ask Grepow
  whether the 440 can be made at R ≈ 37–38 mm, which would remove the remaining ~1.6 mm end lift.
  Cell protection is now a protector IC at the battery end of the flex (integration note §4).
  Handling: fix by the large face, no movement, don't bend the sealed edge, tabs ≤ 3 bends.
- **Pod shape:** curved along the neck, longer tapers (~18 mm), 0.8 mm walls under the skin.
  (Modelled with a rounded-rectangle section, 2.2 mm top corners; see v2 CAD.)
- **Clasp: option B, nose in a shallow cone** (replaces the flat magnet face and the
  sideways-slide lip). The pod's end holds a cone socket with a magnet behind it; the cap carries
  the matching nose and a second magnet. Release force is about the same for straight pull,
  sideways pull and twist. As modelled: 35° cone, and the cap continues the pod's outline rather
  than ending in a small nose (the Ø10.3 cone mouth needs the pod's full end section).
  - Magnets: two facing N52 discs, start with Ø8 × 4.8 mm (K&J 5/16 × 3/16) and tune down with
    skin thickness or Ø8 × 3.2 mm discs. A magnet on a steel disc is too weak through ~0.6 mm of
    skin (estimate ~2 lb).
  - The cone and nose surfaces stay bare against the mould wall; the rest of the pod is skinned.
  - Print release test pieces before casting (straight, sideways, twist, peel).
  - Rejected: flat face + 30° rim (A, needs a blunt pod end), tongue under the pod (C, jams
    sideways), overlapping magnet tongues (D, weak in shear, peels), magnet detents through a loop
    (E, ratchets loose, silicone friction makes release unpredictable), elastic/stretch section
    (International Cat Care advises against elastic collars: legs and jaws get caught), cast-in
    silicone breakaway (the flex crosses every point except the clasp, and it's one-shot).
- **Cap: fit and trim.** A short closed sleeve on the tail with the pin key; fit at the right hole,
  then cut the tail off just past the pins (bare flex there). No window, fold-back or keeper.
  Can be taken in later but not let out.
- **Breakaway target unchanged** (about 2 kg in this brief). Published commercial release forces
  range from about 2 to 6 lb.
- **Printer: Prusa MK3 (250 × 210 bed).** The 255 mm one-piece mould only fits diagonally, so use
  the two-piece version or split the new mould.

## v2 CAD (`hardware/respin/cad_v2/`, 2026-11-11)
Scripts: `collar_parts.py` (printed parts), `collar_mould.py` (envelope + mould; imports the parts),
`clasp_test_pieces.py`. STEP + STL for each part, `v2_collar_assembly.step`, `collar_v2_preview.png`.
Parts are exported in the ring frame (Z = ring axis); reorient for printing.
- **Cast in the worn shape:** a ring at the 72 mm phantom (R0 = 35.97 mm), so the pod's neck face
  follows the neck and the band comes out curved. The adjustment tail (x = −70 to −122.5) is cast
  straight along a tangent so it clears the pod; it bends into the cap when fitted.
- **Mould:** two halves split on the band's mid-width plane, about 112 × 131 mm, each 14.6 mm thick
  (fits the MK3). Ø5 sprue at x = −40 (funnel or syringe), Ø1.6 vents at the tracker, pod, tapers
  and tail end; 3 × Ø3 dowels; 6 × M3 clamp holes. Core features: flat land + 0.3 mm pocket under the
  tracker, cone boss filling the pod socket, Ø1 stilts holding the flex at 1.6 mm, stepped cores
  (Ø3 to 1.6 mm, Ø2 above) at the 7 tail holes. Seal the printed mould with clear acrylic.
- **Silicone outline:** lofted from radial sections through the parts + 0.8 mm skin, constant crown
  over the case (the pod outline follows the cell), tapers into the 12 × 3.6 band over 10 mm (case) and 18 mm (pod). About 15 cm³
  (~16 g) of Dragon Skin 20 per collar. Thin skins in a closed mould: degas, then pour/inject slowly.
- **Tracker case:** tray + cover, 22.6 × 19.6 mm, 5.3 mm tall (targets 1.5 mm, top parts ≤ 1.2 mm);
  ~7 mm over the neck with skin. Target windows Ø3.4 at placeholder positions (−6.5, 6.25),
  (5.5, 6.25), (−5.5, −6.25), (6.5, −6.25): match the KiCad layout. Dimples Ø1.6 × 0.8 at
  x = ±9.6 on the centreline. Flex slots in both end walls at 1.35–1.75 mm. 0.8 mm skin nubs.
- **Pod (GRP751538, 2026-11-12):** shaped tightly round the cell, no crown fill. Cavity is an
  annular sector concentric with the cell (R52.09–60.19, 15.5 wide), the cell resting on its concave
  face with 0.8 mm under it at the middle (2.1–2.5 mm at the ends, where the cell is flatter than the
  neck). 0.8 mm walls; top follows the cell's convex face. Band x 78 → 122.6 (44.6 mm), 17.1 wide;
  radial height above the pod's neck face 9.7 mm mid, ~11.7 at the ends (+1.6 mm for skin and the
  skin under the pod over the neck). 2.5 mm lead allowance at the lid end; Ø2.5 lead hole in the lid.
  Magnet goes in through the cell cavity first. (602030 version: 22.1 wide, ~13.9 over the neck.)
- **Clasp:** radial face at band x 122.6. Cone 35°, **0.6 mm deep** (was 0.8, to fit the lower pod),
  floor Ø8.6, mouth Ø10.3, axis 5.5 mm above the pod's neck face along the band tangent there; the
  pod section blends up over 5 mm to clear the mouth. Magnets Ø8 × 4.8 mm, 0.3 mm skins, about
  0.8 mm apart when seated (cap shoulder 0.2 mm off the pod face). Test pieces updated to 0.6 mm.
- **Cap:** 21 mm long, continues the pod outline and tapers to 14.4 × 5.7 mm; two glued halves
  (split at mid-width) with the magnet trapped between them; slot 12.4 × 3.9 for the tail; two
  radial Ø2.1 holes for Ø2 × 6 mm steel dowel pins (fix with silicone adhesive), 5 mm apart.
  The cap now ends at band x 143.7 (pins at 135 / 140, i.e. −91 / −86 wrapped), so with the longer
  pod the tail holes used at the 226 mm design size shift to around −84.5 / −89.5.
- **Test pieces:** socket + nose pairs at 25°, 35°, 45°, Ø16 bodies with a scale loop; magnets go in
  from the back. Test straight, 45°, 90°, twist and peel, 5 pulls each.

## v3 (`hardware/respin/cad_v3_pod/`, 2026-11-12): current direction
Supersedes the v2 pod, clasp, cap and mould. The tracker case is still v2.
- **Pod:** no PETG shell. The GRP751538 is Kapton-wrapped and cast straight into the silicone
  (`pod_v3.py`), 0.8 mm skin (≥0.5 at the cell's sharp corners, corner radius 1.2 over the cell).
  Height over the neck 8.7 mid, 10.7 at the clasp face (x 124.3); 17.1 wide.
- **Clasp:** one K&J B842-N52 block (12.7 × 6.35 × 3.18) each side. Pod side: a printed PETG insert
  (4.75 × 15.5 × 9.1) with a 0.4 mm bevelled recess in its face; cap side: a matching boss. ~0.8 mm
  magnet gap. Release force still to be measured.
- **Cap:** `cap_screw.py`. PETG shell + 1.5 mm base plate, two M1.6 × 8 countersunk screws from the
  neck side into flush M1.6 nuts, through the tail holes (Ø1.8, 5 mm pitch). No glue; re-size by
  moving the screws; replaceable. 8.0 mm over the neck at the screws.
- **Breakaway sensor:** TMAG3001A2 on the end of the flex under the cell (`sensor_h.py`), ~7 mm
  behind the pod magnet. Flex details are in the shared interface (flex section, 2026-11-12).
- **Mould:** `collar_mould_v3.py` (imports `collar_mould.py`/`collar_parts.py` for the case
  envelope). Two halves split at mid-width, 106 × 118 × 15 mm each (MK3), 3 dowels, 6 × M3.
  - Locating: case in the 0.3 mm land pocket; insert on a boss filling its recess; cell on Ø1.2
    pins (top, both sides, underside at the cell edges) at x 86 and 113; flex on stilts (1.6 mm in
    the band, 0.35 mm in the pod) and Ø1.7 cores through the 7 tail holes.
  - Cast **standing on edge, tail down**: the pod is then at the bottom with its neck side up.
    Fill G2 (tail tip) first, then G1 (pod crown, lowest point) bottom-up by syringe; parting-plane
    vents at the ring top, case crown (3), pod face, tail root and pod taper; radial Ø1 core vents
    under the cell into the open centre. DS20 NV or DS10 NV, degassed in the cup only.
  - Pins leave Ø1.2 holes to the Kapton: dab-fill with the same silicone after demoulding.
  - Tail: 40 mm, straight along the tangent at x −70 (to −110), 6.3 mm clear of the pod envelope.
  - About 13 cm³ (~14 g) of silicone.
- Sheets: `clasp_sizing_sections.png`, `cap_screw_sections.png`, `hall_sensor_sections.png`,
  `mould_v3_sheet.png`.

## Decisions made (earlier)
- **Construction:** the band is cast silicone. The tracker case, the battery pod and the cap are
  rigid PETG prints. One continuous flex strip runs from tracker to pod and cap. The whole inner
  assembly is cast into the band.
- **Moulding approach (first version modelled 2026-11-11; see "Single-pour mould" below):**
  - An open-top flat mould whose floor forms the neck face, with shaped pockets that locate the
    tracker case and the pod. The cap is not cast in.
  - The flex runs taut at mid-band height between them, so it can be a single pour.
  - Faces that must stay bare (magnet faces, dock contacts) go against the mould wall or are taped.
  - The cases and pod must be sealed before casting. Silicone doesn't bond to PETG; it only locks
    through anchor holes and flanges.
- **Silicone:**
  - Platinum cure, Dragon Skin 20 class.
  - Avoid cure inhibitors: sulfur clay (use sulfur-free), latex, tin-cure silicone, and fresh
    epoxy or urethane. Seal printed moulds with clear acrylic.
  - Test-cast a patch with the flex's adhesive or coverlay first.
  - No heat-accelerated cure once a cell is inside.
- **Pod:**
  - The section tapers smoothly into the band so nothing can snag, and the neck face is flat.
  - Lead tunnel through the lid taper. Two magnets behind a 0.3 mm skin.
  - A lip on the neck side supports the cap. The cap slides off sideways for removal.
    (Superseded 2026-11-11 by the option B cone clasp.)
- **Breakaway:**
  - The magnetic joint is the breakaway. Typical cat collars release at about 2 kg (2–5 lb).
  - Measure the pull with a luggage scale before casting, and tune it with the `skin` thickness or
    the magnet grade.
- **Adjustable cap (watch-strap style):**
  - The band tail threads into the cap, is pinned through 2 of its 7 holes by a pin key, exits
    through a top window, and folds back under a TPU keeper.
    (Superseded 2026-11-11: fit-and-trim closed sleeve, no window or keeper.)
  - The pins bear on the polyimide flex holes, not just the silicone.

## Files (in collar_mockup.zip)
- `collar_mockup.py`: the phantom ring for a 72 mm saline bottle. It has the Synzen FPC groove,
  coax channel, tray, lid and pod seat. The tray still fits the old 27.5 × 21.4 board, so it's
  useful for RF A/B tests but needs updating.
- `band_mould.py`: a flat two-stage mould for one arm (base + frame). It now has the 7 adjustment
  hole cores and a rounded tail end. It still carries the old Synzen FPC notches and the
  tracker-end tongue. It is not yet the single-pour full-collar mould.
- `pod_clasp.py`: pod, pod lid with taper and lead tunnel, adjustable cap, pin key and keeper.
  Cell set to the 802025 nominal (8 × 20 × 25) on 2026-11-11 and re-run: the STEP/STL in
  `hardware/respin/cad/` are current; `pod_clasp_preview.png` in the zip still shows the 902030 pod.
- `flex_strip.py`: flex outline and copper, exported as DXF and PNG. It is owned jointly with the
  electrical session.
- `full_collar_mould.py` (2026-11-11): the single-pour full-collar mould. Imports `pod_clasp.py`.
  Generated STEP/STL and a preview sheet are in `hardware/respin/cad/` (see below).

## Generated CAD (`hardware/respin/cad/`, 2026-11-11, CadQuery 2.8)
- STEP files open in Fusion as solid bodies (no history). Change parameters in the scripts and
  re-run, or edit the STEP directly. Port to a Fusion API script with User Parameters once the
  layout settles.
- `full_collar_mould` (one piece, 255.2 × 30.9 × 5.6 mm) and `_left` / `_right` (split at x = 40:
  165.5 + 89.7 mm, two Ø3 × 6 mm dowels each side, for beds under ~260 mm).
- `full_collar_band_cast`: the band as it comes out (200.5 mm, tail x = −122.5 to the lid tip at
  x = 78); about 7.4 cm³ / 8 g of silicone.
- `full_collar_mould_assembly`: mould + case placeholder + pod + lid + flex + band.
- `tracker_case_placeholder`: 23 × 20 × 7 mm rounded box (board + 1.2 mm walls + 0.3 mm clearance),
  only there to cut the pocket.
- `clasp_*` and `pod_clasp_assembly`: regenerated with the 802025 cell.

## Single-pour mould (as modelled)
- Open top; the floor is the neck face; pour to the rim (band_t = 3.6) and strike off.
- Pockets are cut with the real pod + lid envelope and the case placeholder, up to rim height;
  the case and pod stand up out of the pour. Seal their neck faces to the floor (thin sulfur-free
  clay or tape) so silicone can't creep under the dock contacts or the pod.
- Pod placed so its lid anchor holes are at x = 74 (flex anchor holes); magnet face at
  x = 122.28; the end wall clears the lip.
- Flex height: 7 stepped adjustment cores (Ø3 shoulder to 1.6 mm, Ø2 pin through the Ø2.1 flex
  holes) plus Ø1 stilts at y = ±2.5 (x = −14, −32, −50, −66, 30, 48). The flex is denser than
  the silicone, so it stays down on them. Stilts leave Ø1 mm dimples in the neck face.
- The cap is not cast in; the tail threads into it afterwards.
- **Pod-lid anchor flange lowered** (`pod_clasp.py`: `flex_z = 1.6`, `flange_t = 1.0`): it was
  centred in the band (1.2–2.4 mm), which put it through the flex plane. It now spans 0.6–1.6 mm,
  so the flex lies on top of it and the anchor pins pass through both.

## Open items (mechanical)
0. **Next (v3, 2026-11-12):**
   - Print the clasp insert + cap shell/base with two B842 magnets and pull-test (straight, 45°,
     90°, twist, peel); tune with the insert's skin/recess.
   - Print the v3 mould halves; trial cast with a dummy cell (Kapton-wrapped aluminium block) and a
     dummy flex: check the standing bottom-up fill, the core vents, the 0.34 mm silicone over the
     flex, and that the cell pins hold position.
   - Check the GRP751538 tab length with Grepow (sets the tab pads at x 76.5–79.5).
   - Bench-check the Hall field step with a real magnet pair before committing the flex.
   **Earlier (2026-11-11 redesign, v2 modelled):**
   - Print and pull-test the clasp test pieces; pick the cone angle and magnet thickness.
   - Print the mould halves and a trial cast with dummy parts (check fill of the 0.8 mm skins,
     vents, the land pocket seal, flex staying on the stilts).
   - Match the target windows and dimples to the KiCad layout once it exists.
   - Ask Grepow about a curved cell (bend radius ~37 mm, MOQ, price).
   - v1 open-top mould and `pod_clasp.py` are superseded by cad_v2.
1. **Rigid pod on a curved neck.** With the 802025 cell the pod body is about 32 mm long (44 mm
   with the 12 mm taper), down from about 37 mm (49 mm) for the 902030. A flat, rigid neck face
   on the 72 mm phantom (radius 36) stands off at its ends by √(36² + (L/2)²) − 36:
   - body only (32 mm): about 3.5 mm (was about 4.7 mm);
   - body + taper, if the taper's neck face is flat and rigid too (44 mm): about 6.3 mm (was
     about 7.6 mm).
   Options:
   - curve the neck face of the body and tapers (the main fix);
   - a shorter, thicker cell;
   - turn the cell crosswise. About 23 mm along the band gives about 1.8 mm standoff, but the pod
     becomes 30+ mm wide.
   Test-fit a print on the bottle first.
2. Measure the real cell with calipers, including the folded protection-circuit end, and update
   `cell_t/w/l` and `lead_allow`.
3. Design the new tracker case for the 17 × 20 board (possibly slightly larger if layout needs it): flex pass-through, dock contact face, potting
   volume, and the anchor flanges into the band.
   - The flex is at 1.6 mm in the band but under the board it's at about 3 mm (the 3 mm dock
     targets finish flush with the case floor), so it needs a ~1.4 mm jog at each case end wall.
   - Case anchor flanges: same rule as the pod lid, top at 1.6 mm with the flex on top.
   - Then replace the placeholder in `full_collar_mould.py` (`case_body()`).
4. Single-pour full-collar mould: first version modelled (2026-11-11). Still to do: real case
   pocket, test print, check the pocket fit and that silicone doesn't creep under the parts.
5. Print and pull-test the clasp. Check the cap clip and keeper under about 2 kg.
6. Weigh the tracker housing against the pod to confirm the counterweight keeps the tracker on top.
7. Re-cast for the actual cat's neck: set the lengths in `flex_strip.py` and `band_mould.py`
   together.
