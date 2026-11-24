# Appearance

[中文](APPEARANCE-zh.md)

Colours follow the physical gripper (hardware photo, 2026-11-24) and the
xensim-bench TacCap asset (`Looks/TacCap/*`).

| Material | sRGB `rgba` | metallic | roughness | Used on |
| --- | --- | --- | --- | --- |
| `taccap_silver` | `0.82 0.81 0.79 1` | 0.00 | 0.45 | Moulded shell, hinge blocks, adapter |
| `taccap_cover` | `0.65 0.70 0.71 1` | 0.00 | 0.60 | Finger covers, side plates |
| `taccap_black` | `0.018 0.020 0.022 1` | 0.05 | 0.70 | Frame, slave motor, screws, lens barrel, fingertip inner rubber |
| `taccap_yellow` | `0.95 0.72 0.07 1` | 0.00 | 0.48 | Fingertip caps, camera collar, master buttons |
| `taccap_gel` | `0.055 0.055 0.055 1` | 0.00 | 0.85 | Slave tactile pad |
| `taccap_lens` | `0.05 0.055 0.06 0.62` | 0.85 | 0.06 | Fisheye cover glass (dark mirror) |
| `taccap_light` | `0.92 0.94 0.96 0.85` | 0.00 | 0.55 | Slave status-LED window (frosted) |

## How it is shipped

URDF, MJCF and USD each give a visual one material, so a CAD mesh is shipped as
one part per material: `<stem>__<material>.STL` (for example
`grip_left__yellow.STL`). All three formats reference the same parts and show
the same colours. Collision keeps the complete mesh.

The face-to-material table is `ros/taccap_slave_description/config/appearance.json`.
`scripts/extract_appearance_partition.py` builds it; `scripts/generate_appearance_parts.py`
writes the parts from it.

## Rules

- **Fingertip.** The yellow cap ends on the plane `x = 106.4 mm` (finger mesh
  frame). Only the fingertip solid is cut, so screws and plates that cross the
  plane keep their colour, and the seam is a straight line. The slave's gel pad
  stays dark; the master has black rubber instead.
- **Camera window** (same on slave and master). Two CAD solids: the lens module
  (glass dome, then a black stepped barrel) and the yellow collar around it.
- **Slave right finger.** Labelled from the mirrored left finger, solid by solid,
  so both hands match.
- **Master body and fingers.** The time-sync button and the side buttons are
  yellow; the plates they sit in are white.
- **Slave internals.** Parts hidden inside the shell carry no yellow.

`tests/test_appearance.py` reads the shipped parts and checks these rules per
CAD solid: every screw head black, the sync button yellow, the camera lens
module only glass and black, the collar only yellow, the LED window only
`taccap_light`.
