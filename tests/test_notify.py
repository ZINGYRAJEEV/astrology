"""Tests for Telegram notify helpers (no network)."""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.notify import (
    format_scan_alert,
    prediction_alert_snippet,
    send_telegram_message,
    timing_alert_snippet,
)


def test_format_scan_alert():
    text = format_scan_alert(
        "timing", "Neev", "Now: Rahu / Mercury", "Open Timing Summary",
    )
    assert "Timing scan ready" in text
    assert "Neev" in text
    assert "Rahu / Mercury" in text
    assert "Jyotish Darshan" in text


def test_snippets():
    pred = {
        "name": "Neev",
        "summary": "A short summary of the chart.",
        "timing": {"current_maha": "Rahu", "current_antar": "Mercury", "maha_until": "2031"},
        "timing_summary": {"current": {"antar_theme": "study, business"}},
        "position_brief": {"summary": "Watch career."},
    }
    sn = prediction_alert_snippet(pred)
    assert "Rahu" in sn and "Mercury" in sn

    timing = {
        "current": {
            "maha": "Rahu", "antar": "Mercury", "antar_until": "Feb 2027",
            "maha_theme": "ambition", "antar_theme": "study", "sade_sati": "Not in Sade Sati",
        },
        "chapters": [{
            "is_current": True,
            "scores": {"Career": {"score": 40}, "Wealth": {"score": 70}},
            "risks": ["Career: pressure"],
            "opportunities": ["Wealth: skills"],
        }],
    }
    ts = timing_alert_snippet(timing)
    assert "Rahu / Mercury" in ts
    assert "Impact:" in ts


def test_send_without_config_is_noop_fail():
    with patch("astro.notify.get_telegram_config", return_value={
        "bot_token": "", "chat_id": "", "enabled": False, "configured": False, "source": "none",
    }):
        ok, detail = send_telegram_message("hello")
        assert ok is False
        assert "not configured" in detail.lower()


def test_send_success_mocked():
    fake_resp = MagicMock()
    fake_resp.read.return_value = b'{"ok": true, "result": {}}'
    fake_resp.__enter__.return_value = fake_resp
    fake_resp.__exit__.return_value = False
    with patch("astro.notify.get_telegram_config", return_value={
        "bot_token": "T", "chat_id": "1", "enabled": True, "configured": True, "source": "ui",
    }):
        with patch("urllib.request.urlopen", return_value=fake_resp):
            ok, detail = send_telegram_message("hello world")
            assert ok is True
            assert detail == "Sent"


if __name__ == "__main__":
    test_format_scan_alert()
    test_snippets()
    test_send_without_config_is_noop_fail()
    test_send_success_mocked()
    print("notify tests OK")
