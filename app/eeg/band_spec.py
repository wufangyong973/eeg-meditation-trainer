"""Single source of truth for EEG frequency-band keys, display names and Hz ranges.

The 8 detailed bands follow the NeuroSky ThinkGear ``ASIC_EEG_POWER`` (0x83)
protocol order and the hardware's measured ranges (verified 2026-09-26):

    delta 0.5–2.75, theta 3.5–6.75, alpha1(low-alpha) 7.5–9.25,
    alpha2(high-alpha) 10–11.75, beta1(low-beta) 13–16.75,
    beta2(high-beta) 18–29.75, gamma1(low-gamma) 31–39.75,
    gamma2(mid-gamma) 41–49.75.

The 5 grouped bands use the overall span of their sub-bands (the hardware
bands have gaps, e.g. 9.25–10 Hz; the span is the conventional display).

Display names are kept as the app has always shown them ("Delta", "Alpha 1",
…) — they match the custom-formula variables ``alpha1 … gamma2`` and the user
manual. NeuroSky's "low/high/mid" naming is deliberately not adopted here.
"""
from __future__ import annotations

__all__ = ("BAND_RANGES", "BAND_NAMES_BY_KEY", "GROUPED_RANGES", "format_range")

# key -> (display name, low hz, high hz), in protocol (frequency) order.
BAND_RANGES: dict[str, tuple[str, float, float]] = {
    "delta": ("Delta", 0.5, 2.75),
    "theta": ("Theta", 3.5, 6.75),
    "alpha1": ("Alpha 1", 7.5, 9.25),
    "alpha2": ("Alpha 2", 10.0, 11.75),
    "beta1": ("Beta 1", 13.0, 16.75),
    "beta2": ("Beta 2", 18.0, 29.75),
    "gamma1": ("Gamma 1", 31.0, 39.75),
    "gamma2": ("Gamma 2", 41.0, 49.75),
}

# key -> display name (subset convenience lookup).
BAND_NAMES_BY_KEY: dict[str, str] = {k: v[0] for k, v in BAND_RANGES.items()}

# Grouped bands -> sub-band keys, in protocol order.
_GROUP_SUBS: dict[str, tuple[str, ...]] = {
    "delta": ("delta",),
    "theta": ("theta",),
    "alpha": ("alpha1", "alpha2"),
    "beta": ("beta1", "beta2"),
    "gamma": ("gamma1", "gamma2"),
}


def _group_display(key: str) -> str:
    return {
        "delta": "Delta",
        "theta": "Theta",
        "alpha": "Alpha",
        "beta": "Beta",
        "gamma": "Gamma",
    }[key]


def _group_range(key: str) -> tuple[float, float]:
    subs = _GROUP_SUBS[key]
    return (min(BAND_RANGES[s][1] for s in subs),
            max(BAND_RANGES[s][2] for s in subs))


# grouped key -> (display name, low hz, high hz)
GROUPED_RANGES: dict[str, tuple[str, float, float]] = {
    k: (_group_display(k), *_group_range(k)) for k in _GROUP_SUBS
}


def format_range(key: str, *, grouped: bool = False) -> str:
    """Human label for a band's frequency span, e.g. ``7.5–9.25 Hz``.

    Whole numbers are rendered without a trailing ``.0``.
    """
    src = GROUPED_RANGES if grouped else BAND_RANGES
    _name, lo, hi = src[key]

    def _fmt(v: float) -> str:
        return str(int(v)) if float(v).is_integer() else f"{v:g}"

    return f"{_fmt(lo)}–{_fmt(hi)} Hz"
