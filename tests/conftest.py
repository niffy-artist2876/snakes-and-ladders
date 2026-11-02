"""Shared pytest setup."""

import pytest


@pytest.fixture(autouse=True)
def instant_moves(request, monkeypatch):
    """Make token moves finish at once, so UI tests that check game flow can press
    Roll and look at the result on the next frame. Tests of the animation itself opt
    out with `pytestmark = pytest.mark.real_animation`."""
    if request.node.get_closest_marker("real_animation"):
        return
    try:
        from snakes_ladders.ui import animation
    except ImportError:  # Pygame is not installed: the engine tests do not need it.
        return
    monkeypatch.setattr(animation, "DURATION", 0)
