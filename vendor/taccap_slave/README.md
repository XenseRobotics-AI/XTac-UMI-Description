# TacCap slave upstream snapshot

`source/` is an unmodified subset (`urdf/`, `meshes/`, `LICENSES/`, `NOTICE.md`) of
`XenseRobotics-AI/xense-description:assets/grippers/xense/taccap/slave-v2026.10.23`.
`upstream.json` records the verified upstream commit and the hash of every file.

Do not apply downstream patches here. Run `python scripts/import_slave.py` to
adapt the snapshot, and `--check` to verify it. See
[the update workflow](../../docs/UPSTREAM_SLAVE.md), including how to verify and
pin a new upstream commit.

The upstream source notice and license texts are retained unchanged inside
`source/`; they describe the separate CAD and measurement sources.
