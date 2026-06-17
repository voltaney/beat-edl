from beat_edl.timecode import (
    frames_to_timecode,
    seconds_to_frames,
    seconds_to_timecode,
)


def test_seconds_to_frames_rounds_to_nearest():
    assert seconds_to_frames(1.0, 24) == 24
    assert seconds_to_frames(1.02, 24) == 24  # 24.48 -> 24
    assert seconds_to_frames(1.03, 24) == 25  # 24.72 -> 25


def test_frames_to_timecode_basic():
    assert str(frames_to_timecode(0, 24)) == "00:00:00:00"
    assert str(frames_to_timecode(24, 24)) == "00:00:01:00"
    assert str(frames_to_timecode(24 * 60, 24)) == "00:01:00:00"
    assert str(frames_to_timecode(24 * 3600, 24)) == "01:00:00:00"


def test_ntsc_nominal_rate():
    # 29.97 uses a nominal 30-frame label for non-drop timecode.
    assert str(frames_to_timecode(30, 29.97)) == "00:00:01:00"


def test_seconds_to_timecode_with_offset():
    one_hour = 3600 * 24
    assert str(seconds_to_timecode(0.0, 24, offset_frames=one_hour)) == "01:00:00:00"
    assert str(seconds_to_timecode(2.0, 24, offset_frames=one_hour)) == "01:00:02:00"
