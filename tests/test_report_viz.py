"""Tests for spiderweb / dashboard report visuals."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.chart_engine import BirthData, compute_chart
from astro.prediction import generate_prediction
from astro.report_viz import (
    dashboard_metrics, life_area_scores, spiderweb_figure, spiderweb_svg,
)


BIRTH = BirthData(
    name="Test Native", year=1990, month=5, day=15, hour=14, minute=30,
    latitude=28.6139, longitude=77.2090, tz_offset=5.5, place="New Delhi, India",
)


def test_life_area_scores_and_spiderweb():
    pred = generate_prediction(compute_chart(BIRTH), "General reading")
    scores = life_area_scores(pred)
    assert len(scores) >= 5
    for row in scores:
        assert 0 <= row["score"] <= 100
        assert row["label"] and row["verdict"] in {"Supported", "Mixed", "Challenged"}
    metrics = dashboard_metrics(pred)
    assert 0 <= metrics["birth_quality"] <= 100
    assert metrics["supported"] + metrics["challenged"] + metrics["mixed"] == metrics["area_count"]
    svg = spiderweb_svg(pred, theme="horoscope")
    assert "<svg" in svg and "Life-area strength map" in svg
    fig = spiderweb_figure(pred, theme="horoscope")
    if fig is not None:
        assert fig.data and fig.data[0].type == "scatterpolar"


if __name__ == "__main__":
    test_life_area_scores_and_spiderweb()
    print("Report viz tests passed.")
