import pytest

from beat_edl.edl import Marker, markers_from_beats, write_edl


def test_write_edl_header_and_event_count():
    markers = [Marker(time=0.0), Marker(time=1.0), Marker(time=2.0)]
    edl = write_edl(markers, fps=24)
    assert edl.startswith("TITLE: Beat Markers")
    assert "FCM: NON-DROP FRAME" in edl
    # One numbered event per marker.
    assert "001  001" in edl
    assert "003  001" in edl


def test_marker_record_timecode_offset_by_timeline_start():
    edl = write_edl([Marker(time=1.0, name="b")], fps=24)
    # Default timeline start is 01:00:00:00, so 1s lands at 01:00:01:00.
    assert "01:00:01:00" in edl


def test_marker_color_and_note_lines():
    edl = write_edl([Marker(time=0.0, name="Hit", color="Green")], fps=24)
    assert "|C:ResolveColorGreen" in edl
    assert "|M:Hit" in edl
    assert "|D:1" in edl


def test_unknown_color_rejected():
    with pytest.raises(ValueError):
        write_edl([Marker(time=0.0, color="Chartreuse")], fps=24)


def test_markers_from_beats_colors_downbeats():
    beats = [0.0, 0.5, 1.0, 1.5]
    markers = markers_from_beats(beats, downbeats=[0.0, 1.0])
    assert markers[0].color == "Red"
    assert markers[1].color == "Blue"
    assert markers[2].color == "Red"
    assert [m.name for m in markers] == ["Beat 1", "Beat 2", "Beat 3", "Beat 4"]
