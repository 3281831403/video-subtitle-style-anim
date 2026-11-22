import pytest

from subsfx.animate import (
    anim_batch,
    char_times,
    ease_out_back,
    layout_chars,
    opacity_at,
    scale_at,
    stroke_width_at,
    validate_style,
)

EPS = 1e-9

BASE_STYLE = {
    "font_size": 40.0,
    "letter_spacing": 2.0,
    "per_char_ms": 80.0,
    "char_dur_ms": 300.0,
    "fade_ms": 120.0,
    "overshoot": 1.2,
}


def test_char_times_staggers_each_character():
    times = char_times("字幕弹出", 1000.0, 120.0)
    assert times == pytest.approx([1000.0, 1120.0, 1240.0, 1360.0], abs=EPS)
    assert len(set(times)) == 4


def test_ease_out_back_hits_exact_endpoints():
    assert ease_out_back(0.0, 1.6) == pytest.approx(0.0, abs=EPS)
    assert ease_out_back(1.0, 1.6) == pytest.approx(1.0, abs=EPS)

    samples = [ease_out_back(i / 100.0, 1.6) for i in range(101)]
    assert max(samples) > 1.0 + 1e-3
    assert min(samples) >= -EPS


def test_scale_at_uses_back_easing_not_linear():
    char_time = 2000.0
    dur_ms = 400.0
    middle = scale_at(char_time, char_time + dur_ms * 0.5, dur_ms, 1.2)

    assert middle > 1.0
    assert middle < 2.0


def test_opacity_uses_fade_not_character_duration():
    char_time = 3000.0

    assert opacity_at(char_time, char_time, 120.0) == pytest.approx(0.0, abs=EPS)
    assert opacity_at(char_time, char_time + 60.0, 120.0) == pytest.approx(
        0.5, abs=EPS
    )
    assert opacity_at(char_time, char_time + 120.0, 120.0) == pytest.approx(
        1.0, abs=EPS
    )

    # The fade is complete here while an 800 ms pop is still in progress.
    assert scale_at(char_time, char_time + 120.0, 800.0, 1.2) < 1.0


def test_layout_chars_does_not_assume_monospace():
    items = layout_chars("A字A", {"font_size": 40.0, "letter_spacing": 5.0})

    assert [item["char"] for item in items] == ["A", "字", "A"]
    assert [item["width"] for item in items] == pytest.approx(
        [20.0, 40.0, 20.0], abs=EPS
    )
    assert [item["x"] for item in items] == pytest.approx(
        [0.0, 25.0, 70.0], abs=EPS
    )


def test_stroke_width_does_not_scale_with_glyph():
    assert stroke_width_at(0.25, 4.0) == pytest.approx(4.0, abs=EPS)
    assert stroke_width_at(2.0, 4.0) == pytest.approx(4.0, abs=EPS)


def test_validate_style_rejects_fade_longer_than_duration():
    assert validate_style(dict(BASE_STYLE)) == []

    bad = dict(BASE_STYLE)
    bad["fade_ms"] = 301.0
    assert validate_style(bad) == ["fade_ms must be <= char_dur_ms"]


def test_anim_batch_restarts_timeline_for_each_clip():
    clips = [
        {"id": "a", "text": "AB", "start_ms": 1000.0},
        {"id": "b", "text": "字幕", "start_ms": 5000.0},
    ]

    result = anim_batch(clips, BASE_STYLE)

    assert [c["time_ms"] for c in result["a"]["chars"]] == pytest.approx(
        [1000.0, 1080.0], abs=EPS
    )
    assert [c["time_ms"] for c in result["b"]["chars"]] == pytest.approx(
        [5000.0, 5080.0], abs=EPS
    )
    assert result["b"]["start_ms"] == pytest.approx(5000.0, abs=EPS)


def test_char_times_last_char_stays_inside_timeline():
    text = "字幕弹出"
    start_ms = 200.0
    per_char_ms = 90.0

    times = char_times(text, start_ms, per_char_ms)

    assert times[-1] == pytest.approx(
        start_ms + per_char_ms * (len(text) - 1), abs=EPS
    )
    assert times[-1] < start_ms + per_char_ms * len(text)


def test_ease_out_back_clamps_excessive_overshoot():
    for t in (0.25, 0.5, 0.75, 0.95):
        huge = ease_out_back(t, 1e9)
        capped = ease_out_back(t, 2.0)
        assert huge == pytest.approx(capped, abs=EPS)
        assert 0.0 <= huge <= 2.0

    assert ease_out_back(0.5, -1e9) == pytest.approx(
        ease_out_back(0.5, 0.0), abs=EPS
    )
    assert scale_at(0.0, 150.0, 300.0, 1e9) >= 0.0


def test_scale_endpoints_are_exact():
    char_time = 750.0
    dur_ms = 250.0

    assert scale_at(char_time, char_time, dur_ms, 1.2) == pytest.approx(
        0.0, abs=EPS
    )
    assert scale_at(char_time, char_time + dur_ms, dur_ms, 1.2) == pytest.approx(
        1.0, abs=EPS
    )
    assert scale_at(char_time, char_time - 1.0, dur_ms, 1.2) == pytest.approx(
        0.0, abs=EPS
    )
    assert scale_at(
        char_time, char_time + dur_ms + 1.0, dur_ms, 1.2
    ) == pytest.approx(1.0, abs=EPS)


def test_adjacent_char_gap_equals_per_char():
    times = char_times("ABCDE", 10.0, 37.5)
    gaps = [later - earlier for earlier, later in zip(times, times[1:])]

    assert gaps == pytest.approx([37.5, 37.5, 37.5, 37.5], abs=EPS)


def test_layout_cjk_uses_full_width():
    items = layout_chars("字幕", {"font_size": 64.0})

    assert [item["width"] for item in items] == pytest.approx(
        [64.0, 64.0], abs=EPS
    )
    assert [item["x"] for item in items] == pytest.approx(
        [0.0, 64.0], abs=EPS
    )


def test_stroke_width_independent_of_scale_at_tolerance():
    base_width = 3.75
    for scale in (0.0, 0.01, 0.5, 1.0, 1.2, 10.0):
        assert stroke_width_at(scale, base_width) == pytest.approx(
            base_width, abs=EPS
        )


def test_anim_batch_matches_individual_clips():
    clip_a = {"id": "a", "text": "A字", "start_ms": 100.0}
    clip_b = {"id": "b", "text": "字幕", "start_ms": 900.0}

    batched = anim_batch([clip_a, clip_b], BASE_STYLE)
    solo_a = anim_batch([clip_a], BASE_STYLE)["a"]
    solo_b = anim_batch([clip_b], BASE_STYLE)["b"]

    assert batched["a"] == solo_a
    assert batched["b"] == solo_b
