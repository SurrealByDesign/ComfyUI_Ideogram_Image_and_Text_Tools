"""Foundation smoke test.

Confirms the package imports cleanly and exposes the node registry
contract that ComfyUI expects.
"""

from nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS


def test_node_mappings_are_dicts():
    assert isinstance(NODE_CLASS_MAPPINGS, dict)
    assert isinstance(NODE_DISPLAY_NAME_MAPPINGS, dict)


def test_every_registered_node_has_a_display_name():
    assert set(NODE_CLASS_MAPPINGS) == set(NODE_DISPLAY_NAME_MAPPINGS)
