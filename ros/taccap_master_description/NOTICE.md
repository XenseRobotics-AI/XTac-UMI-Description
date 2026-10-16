# TacCap G1 master: source and notices

## Source

The left/right master URDFs and STL meshes come from Xense Robotics' TacCap
viewer project (Apache-2.0). Xense Robotics releases these descriptions and
meshes under this repository's MIT license.

## Third-party notices

- `LICENSES/apache-2.0.txt`: Apache License 2.0 of the source project,
  retained for the imported files.

## Changes from the source files

- `<side>_base_link` moved to the shell rear outer surface with +Z along the
  tool axis; links and joints renamed (`<side>_right_link`, `<side>_left_link`,
  `<side>_pico_link`, ...).
- Finger frames aligned with the base axes (hinge +X).
- Added the `<side>_follower_link`, `<side>_eef_link` and wrist camera frames.
- MJCF and USD are generated from the URDFs.
