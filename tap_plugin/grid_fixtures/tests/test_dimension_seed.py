"""The grid_fixtures dimension seed declares every dimension key the plugin writes.

Core's dimension-map reshape (tap#708, #711) refers to dimensions by their node's id and never
mints a node, so a key a running grid writes must have a seeded Dimension node. grid_fixtures
writes one key, ``tap.playground``: the pg_* models' DEFAULT_DIMENSIONS, the PG_* edges'
``default_dimensions`` and the canary collector's stamp.
"""

from __future__ import annotations

import ast
import json
import tomllib
from pathlib import Path
from typing import Any

PLUGIN = Path(__file__).resolve().parent.parent
SEED = PLUGIN / "grift" / "dimension.grift.json"
# Core's test vocabulary uses this id for tap.playground; the seed must agree with it.
PLAYGROUND_ID = "01a1d150-0000-7000-8000-000000000001"


def _nodes() -> list[dict[str, Any]]:
    document = json.loads(SEED.read_text(encoding="utf-8"))
    return [node for batch in document["batches"] for node in batch["nodes"]]


def _written_keys() -> set[str]:
    """Every dimension key the plugin's source writes: model DEFAULT_DIMENSIONS and collector
    ``*_DIMENSIONS`` dict literals (by AST), plus edge files' ``default_dimensions``."""
    keys: set[str] = set()
    for path in [*(PLUGIN / "models").glob("*.py"), *(PLUGIN / "collectors").rglob("*.py")]:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            target = None
            if isinstance(node, ast.AnnAssign):
                target, value = node.target, node.value
            elif isinstance(node, ast.Assign) and len(node.targets) == 1:
                target, value = node.targets[0], node.value
            if isinstance(target, ast.Name) and target.id.upper().endswith("DIMENSIONS") and isinstance(value, ast.Dict):
                keys |= {k.value for k in value.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)}
    for path in (PLUGIN / "edges").glob("*.edge.json"):
        keys |= set(json.loads(path.read_text(encoding="utf-8")).get("default_dimensions", {}))
    return keys


def test_the_seed_declares_every_key_the_plugin_writes() -> None:
    nodes = _nodes()
    assert {n["entity"]["entity_type"] for n in nodes} == {"dimension"}
    declared = {n["node"]["name"] for n in nodes}
    written = _written_keys()
    assert written, "the source scan found no dimension keys; it has stopped seeing the stamps"
    assert written == declared, f"written {sorted(written)} vs declared {sorted(declared)}"
    assert all(n["entity"]["name"] == n["node"]["name"] for n in nodes)
    assert all(n["node"]["description"].strip() for n in nodes)


def test_tap_playground_has_cores_id() -> None:
    by_name = {n["node"]["name"]: n for n in _nodes()}
    assert by_name["tap.playground"]["entity"]["entity_id"] == PLAYGROUND_ID


def test_the_manifest_declares_the_seed() -> None:
    manifest = tomllib.loads((PLUGIN / "tap-plugin.toml").read_text(encoding="utf-8"))
    assert manifest["grift"]["dimension"] == "grift/dimension.grift.json"
