"""Tests for the Bridge Diagnostics Utility."""
from jester_bridge.diagnostics import get_bridge_diagnostics


def test_bridge_diagnostics():
    data = get_bridge_diagnostics()
    assert data['status'] == 'ONLINE'
    assert data['protocol'] == 'v2.0'
    assert 'openai' in data['providers']
    assert 'google' in data['providers']
    assert data['execution_boundary'] == 'bounded_workspace_runtime'
