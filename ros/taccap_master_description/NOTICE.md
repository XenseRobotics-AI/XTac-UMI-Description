# TacCap G1 master: source and notices

## Source

The left/right master URDFs and STL meshes come from Xense Robotics' TacCap
viewer project (Apache-2.0). The original URDFs are kept byte-for-byte in
`provenance/urdf/`; source checksums are recorded in `config/master.json`.
Xense Robotics releases these descriptions and meshes under this repository's
MIT license.

## Third-party notices

- `LICENSES/apache-2.0.txt`: Apache License 2.0 of the source project,
  retained for the imported files.

## Changes from the source files

- `<side>_base_link` moved to the shell rear outer surface with +Z along the
  tool axis; the original `base_link` merged into it (shell meshes placed via
  origins). Links and joints renamed (`<side>_right_link`, `<side>_left_link`,
  `<side>_pico_link`, ...).
- Finger frames aligned with the base axes (hinge +X, the original -Z);
  zero position, limits and signs unchanged.
- Added massless `<side>_follower_link` (matches the slave
  `taccap_base_link`), `<side>_eef_link` (closed fingertip face centre) and
  wrist camera frames.
- MJCF and USD are regenerated from the current URDFs.

No mass, inertia or collision data is supplied. Frames are mesh/CAD-derived
and not calibrated.
