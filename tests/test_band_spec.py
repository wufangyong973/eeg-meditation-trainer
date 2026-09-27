"""Tests for the band_spec module (#45) and the band_rows range field."""
from __future__ import annotations

from app.eeg.band_spec import (
    BAND_NAMES_BY_KEY,
    BAND_RANGES,
    GROUPED_RANGES,
    format_range,
)
from app.ui.widgets.band_totals import band_rows


# ---------------------------------------------------------------------------
# Protocol values (NeuroSky ThinkGear ASIC_EEG_POWER 0x83)
# ---------------------------------------------------------------------------
def test_detailed_ranges_match_protocol():
    assert BAND_RANGES["delta"] == ("Delta", 0.5, 2.75)
    assert BAND_RANGES["theta"] == ("Theta", 3.5, 6.75)
    assert BAND_RANGES["alpha1"] == ("Alpha 1", 7.5, 9.25)
    assert BAND_RANGES["alpha2"] == ("Alpha 2", 10.0, 11.75)
    assert BAND_RANGES["beta1"] == ("Beta 1", 13.0, 16.75)
    assert BAND_RANGES["beta2"] == ("Beta 2", 18.0, 29.75)
    assert BAND_RANGES["gamma1"] == ("Gamma 1", 31.0, 39.75)
    assert BAND_RANGES["gamma2"] == ("Gamma 2", 41.0, 49.75)


def test_detailed_band_keys_are_in_protocol_frequency_order():
    keys = list(BAND_RANGES)
    assert keys == [
        "delta", "theta", "alpha1", "alpha2",
        "beta1", "beta2", "gamma1", "gamma2",
    ]
    # frequency order: each band's low edge is >= the previous band's high edge
    for prev, nxt in zip(keys, keys[1:]):
        assert BAND_RANGES[prev][2] <= BAND_RANGES[nxt][1]


def test_band_display_names_unchanged():
    assert BAND_NAMES_BY_KEY == {
        "delta": "Delta", "theta": "Theta",
        "alpha1": "Alpha 1", "alpha2": "Alpha 2",
        "beta1": "Beta 1", "beta2": "Beta 2",
        "gamma1": "Gamma 1", "gamma2": "Gamma 2",
    }


# ---------------------------------------------------------------------------
# Grouped ranges = min/max span of their sub-bands
# ---------------------------------------------------------------------------
def test_grouped_range_is_span_of_subbands():
    assert GROUPED_RANGES["delta"] == ("Delta", 0.5, 2.75)
    assert GROUPED_RANGES["theta"] == ("Theta", 3.5, 6.75)
    assert GROUPED_RANGES["alpha"] == ("Alpha", 7.5, 11.75)
    assert GROUPED_RANGES["beta"] == ("Beta", 13.0, 29.75)
    assert GROUPED_RANGES["gamma"] == ("Gamma", 31.0, 49.75)


def test_grouped_range_matches_minmax_formula():
    # recompute from the sub-bands to prove the module isn't hard-coded
    # inconsistently with itself.
    subs = {
        "alpha": ("alpha1", "alpha2"),
        "beta": ("beta1", "beta2"),
        "gamma": ("gamma1", "gamma2"),
    }
    for g, ks in subs.items():
        lo = min(BAND_RANGES[k][1] for k in ks)
        hi = max(BAND_RANGES[k][2] for k in ks)
        assert GROUPED_RANGES[g][1] == lo
        assert GROUPED_RANGES[g][2] == hi


def test_grouped_names_match_band_totals_meta():
    # the names shown by the Grouped table must equal band_spec grouped names
    from app.ui.widgets import band_totals as bt
    names_from_meta = {k: n for k, n, _g in bt._GROUP_META}
    assert names_from_meta == {k: v[0] for k, v in GROUPED_RANGES.items()}


# ---------------------------------------------------------------------------
# format_range helpers
# ---------------------------------------------------------------------------
def test_format_range_detailed():
    assert format_range("delta") == "0.5–2.75 Hz"
    assert format_range("alpha1") == "7.5–9.25 Hz"
    assert format_range("alpha2") == "10–11.75 Hz"
    assert format_range("gamma2") == "41–49.75 Hz"


def test_format_range_grouped():
    assert format_range("alpha", grouped=True) == "7.5–11.75 Hz"
    assert format_range("beta", grouped=True) == "13–29.75 Hz"
    assert format_range("gamma", grouped=True) == "31–49.75 Hz"


def test_format_range_unknown_key_raises():
    try:
        format_range("not-a-band")
    except (KeyError, LookupError):
        return
    raise AssertionError("format_range should raise for an unknown key")


# ---------------------------------------------------------------------------
# band_rows now carries a range field
# ---------------------------------------------------------------------------
def test_band_rows_detailed_includes_range():
    rows = band_rows({"delta": 1.0, "theta": 2.0, "alpha1": 0.0, "alpha2": 0.0,
                      "beta1": 0.0, "beta2": 0.0, "gamma1": 0.0, "gamma2": 0.0},
                     mode="detailed")
    assert [r["range"] for r in rows] == [
        "0.5–2.75 Hz", "3.5–6.75 Hz", "7.5–9.25 Hz", "10–11.75 Hz",
        "13–16.75 Hz", "18–29.75 Hz", "31–39.75 Hz", "41–49.75 Hz",
    ]


def test_band_rows_grouped_includes_range():
    rows = band_rows({"delta": 1.0, "theta": 2.0, "alpha1": 0.0, "alpha2": 0.0,
                      "beta1": 0.0, "beta2": 0.0, "gamma1": 0.0, "gamma2": 0.0},
                     mode="grouped")
    assert [r["range"] for r in rows] == [
        "0.5–2.75 Hz", "3.5–6.75 Hz", "7.5–11.75 Hz",
        "13–29.75 Hz", "31–49.75 Hz",
    ]


def test_band_rows_names_come_from_band_spec():
    rows = band_rows({}, mode="detailed")
    for r in rows:
        assert r["name"] == BAND_NAMES_BY_KEY[r["key"]]
