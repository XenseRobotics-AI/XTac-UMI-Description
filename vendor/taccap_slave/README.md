# TacCap slave upstream snapshot

`source/` is an unmodified snapshot of
`XenseRobotics-AI/xense-description:assets/grippers/xense/taccap/slave-v2026.10.23`.
`upstream.json` records all file hashes and whether an upstream commit has been verified.
The original capture is an uncommitted worktree snapshot; its context HEAD is not its revision.

Do not apply downstream patches here. Run `python scripts/import_slave.py` to
adapt the snapshot, and `--check` to verify it. See
[the update workflow](../../docs/UPSTREAM_SLAVE.md), including how to verify and
pin the upstream commit after it is published.

The upstream source notices and license texts are retained unchanged inside
`source/`; they describe the separate CAD and measurement sources.
