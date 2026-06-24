"""Lightweight regression checks for workflows/*.json -- the polished,
full-UI-format templates meant for a human to load into ComfyUI directly
(see workflows/README.md for how these differ from examples/).

These were built programmatically against live ComfyUI schemas and verified
by actually queuing them, so this suite only guards against the file getting
corrupted afterward (e.g. a bad manual edit) -- it does not re-validate the
graph logic itself.
"""

import json
from pathlib import Path

import pytest

WORKFLOWS_DIR = Path(__file__).resolve().parent.parent / "workflows"


def _workflow_files():
    return sorted(WORKFLOWS_DIR.glob("*.json"))


def _load_no_duplicate_keys(path):
    def reject_duplicates(pairs):
        seen = {}
        for key, value in pairs:
            if key in seen:
                raise ValueError(f"duplicate key {key!r} in {path.name}")
            seen[key] = value
        return seen

    with open(path, encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=reject_duplicates)


def test_at_least_one_workflow_template_present():
    assert len(_workflow_files()) >= 1


@pytest.mark.parametrize("path", _workflow_files(), ids=lambda p: p.name)
def test_workflow_is_valid_ui_format(path):
    data = _load_no_duplicate_keys(path)
    assert isinstance(data, dict)
    for key in ("nodes", "links", "groups", "config", "extra", "version"):
        assert key in data, f"{path.name} missing top-level key {key!r}"
    assert isinstance(data["nodes"], list) and len(data["nodes"]) > 0


@pytest.mark.parametrize("path", _workflow_files(), ids=lambda p: p.name)
def test_workflow_has_a_readme_note(path):
    data = _load_no_duplicate_keys(path)
    notes = [n for n in data["nodes"] if n.get("type") == "Note"]
    assert notes, f"{path.name} has no Note node explaining the workflow"
    assert notes[0]["widgets_values"][0].strip(), f"{path.name}'s Note has no text"


@pytest.mark.parametrize("path", _workflow_files(), ids=lambda p: p.name)
def test_workflow_node_ids_are_unique(path):
    data = _load_no_duplicate_keys(path)
    ids = [n["id"] for n in data["nodes"]]
    assert len(ids) == len(set(ids)), f"{path.name} has duplicate node ids"


@pytest.mark.parametrize("path", _workflow_files(), ids=lambda p: p.name)
def test_workflow_links_reference_existing_nodes(path):
    data = _load_no_duplicate_keys(path)
    node_ids = {n["id"] for n in data["nodes"]}
    for link in data["links"]:
        _link_id, origin_id, _origin_slot, target_id, _target_slot, _type = link
        assert origin_id in node_ids, f"{path.name} link {link} has unknown origin {origin_id}"
        assert target_id in node_ids, f"{path.name} link {link} has unknown target {target_id}"
