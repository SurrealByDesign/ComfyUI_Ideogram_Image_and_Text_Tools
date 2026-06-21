"""Foundation smoke test.

Confirms the package imports cleanly and exposes the node registry
contract that ComfyUI expects, even before any nodes are implemented.
"""

from nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS


def test_node_mappings_are_dicts():
    assert isinstance(NODE_CLASS_MAPPINGS, dict)
    assert isinstance(NODE_DISPLAY_NAME_MAPPINGS, dict)


def test_no_nodes_registered_yet():
    assert NODE_CLASS_MAPPINGS == {}
