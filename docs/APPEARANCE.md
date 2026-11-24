# Appearance

[中文](APPEARANCE-zh.md)

The models are coloured like the physical gripper. URDF, MJCF and USD show the
same colours.

| Material | sRGB `rgba` | metallic | roughness | Used on |
| --- | --- | --- | --- | --- |
| `taccap_silver` | `0.82 0.81 0.79 1` | 0.00 | 0.45 | Shell, hinge blocks, adapter |
| `taccap_cover` | `0.65 0.70 0.71 1` | 0.00 | 0.60 | Finger covers, side plates |
| `taccap_black` | `0.018 0.020 0.022 1` | 0.05 | 0.70 | Frame and connector, slave motor, screws, lens barrel, master fingertip rubber, fingertip nub, silkscreen |
| `taccap_yellow` | `0.95 0.72 0.07 1` | 0.00 | 0.48 | Fingertip caps, camera collar, master buttons |
| `taccap_gel` | `0.055 0.055 0.055 1` | 0.00 | 0.85 | Slave tactile pad |
| `taccap_lens` | `0.05 0.055 0.06 0.62` | 0.85 | 0.06 | Fisheye cover glass |
| `taccap_light` | `0.92 0.94 0.96 0.85` | 0.00 | 0.55 | Slave status-LED window |

URDF `<color>` has no metallic or roughness; those two apply to USD.

## Mesh parts

A visual carries one material, so each CAD mesh ships as one part per material,
`<stem>__<material>.STL` (for example `grip_left__yellow.STL`). Collision uses
the complete mesh.

Each fingertip cap also carries the XENSE silkscreen as its own visual,
`<stem>_silkscreen.STL`, a thin black print just off the cap's outer face. It
is geometry, not a texture, so it renders in every format.

The parts are generated from two data files in
`ros/taccap_slave_description/config/`: `appearance.json` (the material of
every mesh face) and `silkscreen.json` (the wordmark outline). Regenerate with
`python scripts/generate_appearance_parts.py`.
