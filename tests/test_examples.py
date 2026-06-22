"""Example workflows are hand-authored ComfyUI API-format JSON, not
exported from a live ComfyUI session. This test catches drift: every
custom node class_type referenced in an example must still exist in
the node registry.
"""

import json
from pathlib import Path

import pytest

from nodes import NODE_CLASS_MAPPINGS

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


def _example_files():
    return sorted(EXAMPLES_DIR.glob("*.json"))


def _load_no_duplicate_keys(path):
    """Plain json.load silently keeps the last value on a duplicate key,
    which previously let a node-id collision slip through unnoticed."""

    def reject_duplicates(pairs):
        seen = {}
        for key, value in pairs:
            if key in seen:
                raise ValueError(f"duplicate node id {key!r} in {path.name}")
            seen[key] = value
        return seen

    with open(path, encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=reject_duplicates)


@pytest.mark.parametrize("path", _example_files(), ids=lambda p: p.name)
def test_example_is_valid_json_object_of_nodes(path):
    workflow = _load_no_duplicate_keys(path)
    assert isinstance(workflow, dict)
    assert len(workflow) > 0
    for node_id, node in workflow.items():
        assert "class_type" in node, f"{path.name} node {node_id} missing class_type"
        assert "inputs" in node, f"{path.name} node {node_id} missing inputs"


@pytest.mark.parametrize("path", _example_files(), ids=lambda p: p.name)
def test_example_custom_node_types_are_registered(path):
    workflow = _load_no_duplicate_keys(path)
    for node_id, node in workflow.items():
        class_type = node["class_type"]
        if class_type in _CORE_NODE_TYPES:
            continue
        assert (
            class_type in NODE_CLASS_MAPPINGS
        ), f"{path.name} node {node_id} references unknown class_type {class_type!r}"


_CORE_NODE_TYPES = {
    "LoadImage",
    "SaveImage",
    "PreviewImage",
    "ImageBatch",
    "MaskToImage",
    "ImageToMask",
    "JoinImageWithAlpha",
    "InvertMask",
}


def test_at_least_one_example_per_implemented_node_family():
    referenced = set()
    for path in _example_files():
        workflow = _load_no_duplicate_keys(path)
        referenced.update(node["class_type"] for node in workflow.values())
    for name in NODE_CLASS_MAPPINGS:
        assert name in referenced, f"No example workflow references {name}"
