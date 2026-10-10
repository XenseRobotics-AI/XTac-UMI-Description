"""Record generated-asset parameters and hashes in the component config JSON.

The USD conversion settings live in the generators, so a consumer reading only
the shipped assets cannot tell which parameters produced them. These helpers
mirror those settings, plus a hash of every shipped layer, into the existing
provenance files. Generators call them with ``check=True`` under ``--check`` so
stale metadata fails the same regression as stale models.
"""

import hashlib
import json
from pathlib import Path


def hash_tree(root, subdirectory):
    """Map each file under ``root / subdirectory`` to its sha256, sorted by path."""
    base = root / subdirectory
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(base.rglob("*"))
        if path.is_file()
    }


def update_config(path, key, payload, check):
    """Set ``key`` in the JSON at ``path``; compare instead of writing under check.

    Returns the path so callers can report it alongside the generated files.
    """
    document = json.loads(path.read_text())
    if document.get(key) != payload:
        if check:
            raise SystemExit(f"Regenerate stale {key} metadata: {path}")
        document[key] = payload
        path.write_text(json.dumps(document, indent=2) + "\n")
    return path
