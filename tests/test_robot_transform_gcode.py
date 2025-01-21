import pytest
from robot.transform_gcode_to_ROBOTROOT import transform_gcode_points


def test_identity_transformation():
    """Test with no rotation or translation."""
    points = [{"X": 1, "Y": 1, "Z": 1, "Move": "G0", "Layer": 0, "Type": "TRAVEL"}]
    tool_orientation = {"A": 0, "B": 0, "C": 0}
    tool_offset = {"X": 0, "Y": 0, "Z": 0}
    robot_base = {"X": 0, "Y": 0, "Z": 0, "A": 0, "B": 0, "C": 0}
    expected = [{"X": 1.0, "Y": 1.0, "Z": 1.0}]

    result = transform_gcode_points(points, tool_orientation, tool_offset, robot_base)
    assert result == pytest.approx(expected, abs=1e-3)


def test_tool_offset_translation():
    """Test with tool offset along all axis."""
    points = [{"X": 1, "Y": 1, "Z": 0, "Move": "G0", "Layer": 0, "Type": "TRAVEL"}]
    tool_orientation = {"A": 0, "B": 0, "C": 0}
    tool_offset = {"X": 1, "Y": 1, "Z": 100}
    robot_base = {"X": 0, "Y": 0, "Z": 0, "A": 0, "B": 0, "C": 0}
    expected = [{"X": 0.0, "Y": 0.0, "Z": -100.0}]

    result = transform_gcode_points(points, tool_orientation, tool_offset, robot_base)
    assert result == pytest.approx(expected, abs=1e-3)


def test_tool_orientation_rotation():
    """Test with tool rotation along all axis."""
    points = [{"X": 1, "Y": 1, "Z": 0, "Move": "G0", "Layer": 0, "Type": "TRAVEL"}]
    tool_orientation = {"A": 180, "B": 180, "C": 180}
    tool_offset = {"X": 0, "Y": 0, "Z": 0}
    robot_base = {"X": 0, "Y": 0, "Z": 0, "A": 0, "B": 0, "C": 0}
    expected = [{"X": 1, "Y": 1, "Z": 0}]

    result = transform_gcode_points(points, tool_orientation, tool_offset, robot_base)
    assert result == pytest.approx(expected, abs=1e-3)


def test_robotroot_translation():
    """Test with robot root offset along all axis."""
    points = [{"X": 0, "Y": 0, "Z": 0, "Move": "G0", "Layer": 0, "Type": "TRAVEL"}]
    tool_orientation = {"A": 0, "B": 0, "C": 0}
    tool_offset = {"X": 0, "Y": 0, "Z": 0}
    robot_base = {"X": 10, "Y": 10, "Z": 10, "A": 0, "B": 0, "C": 0}
    expected = [{"X": -10, "Y": -10, "Z": -10}]

    result = transform_gcode_points(points, tool_orientation, tool_offset, robot_base)
    assert result == pytest.approx(expected, abs=1e-3)


def test_robotroot_rotation():
    """Test with 180-degree rotation around all axis."""
    points = [{"X": 1, "Y": 1, "Z": 0, "Move": "G0", "Layer": 0, "Type": "TRAVEL"}]
    tool_orientation = {"A": 0, "B": 0, "C": 180}
    tool_offset = {"X": 0, "Y": 0, "Z": 0}
    robot_base = {"X": 0, "Y": 0, "Z": 0, "A": 180, "B": -90, "C": 180}
    expected = [{"X": 0.0, "Y": 1.0, "Z": -1.0}]

    result = transform_gcode_points(points, tool_orientation, tool_offset, robot_base)
    assert result == pytest.approx(expected, abs=1e-3)


def test_complete():
    """Test with 180-degree rotation around Y-axis and X-Axis with a tool_offset of 10 from $NULLFRAME."""
    points = [{"X": 0, "Y": 0, "Z": 0, "Move": "G0", "Layer": 0, "Type": "TRAVEL"}]
    tool_orientation = {"A": 0, "B": 180, "C": 180}
    tool_offset = {"X": 0, "Y": 0, "Z": 10}
    robot_base = {"X": 0, "Y": 0, "Z": 0, "A": 0, "B": 0, "C": 0}
    expected = [{"X": 0, "Y": 0, "Z": -10.0}]

    result = transform_gcode_points(points, tool_orientation, tool_offset, robot_base)
    assert result == pytest.approx(expected, abs=1e-3)
