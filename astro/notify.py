"""Telegram alerts after a chart / timing scan completes.

Configuration (first match wins for token/chat):
  1. Streamlit secrets: ``st.secrets["telegram"]["bot_token"]`` / ``chat_id``
  2. Session UI overrides (Alerts page / expander) — never written to git

If Telegram is not configured, every call is a silent no-op so the app
keeps working offline.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional, Tuple


def _secrets_telegram() -> Dict[str, str]:
    try:
        import streamlit as st
        block = st.secrets.get("telegram", {})
        if hasattr(block, "to_dict"):
            block = block.to_dict()
        return dict(block) if block else {}
    except Exception:
        return {}


def get_telegram_config() -> Dict[str, Any]:
    """Resolved bot token, chat id, and enabled flag."""
    try:
        import streamlit as st
        ui = st.session_state.get("telegram_ui") or {}
    except Exception:
        ui = {}

    sec = _secrets_telegram()
    token = (ui.get("bot_token") or sec.get("bot_token") or "").strip()
    chat_id = str(ui.get("chat_id") or sec.get("chat_id") or "").strip()
    enabled_default = bool(token and chat_id)
    enabled = ui.get("enabled")
    if enabled is None:
        enabled = enabled_default
    else:
        enabled = bool(enabled) and enabled_default
    return {
        "bot_token": token,
        "chat_id": chat_id,
        "enabled": bool(enabled and token and chat_id),
        "configured": bool(token and chat_id),
        "source": "ui" if (ui.get("bot_token") or ui.get("chat_id")) else (
            "secrets" if sec else "none"
        ),
    }


def is_telegram_enabled() -> bool:
    return bool(get_telegram_config().get("enabled"))


def send_telegram_message(
    text: str,
    *,
    bot_token: Optional[str] = None,
    chat_id: Optional[str] = None,
    timeout: float = 8.0,
) -> Tuple[bool, str]:
    """POST to Telegram Bot API. Returns ``(ok, detail)`` — never raises."""
    cfg = get_telegram_config()
    token = (bot_token or cfg["bot_token"] or "").strip()
    chat = str(chat_id or cfg["chat_id"] or "").strip()
    if not token or not chat:
        return False, "Telegram not configured (need bot_token + chat_id)."
    if not text or not str(text).strip():
        return False, "Empty message."

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat,
        "text": str(text)[:4000],
        "disable_web_page_preview": True,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(body) if body else {}
            if parsed.get("ok"):
                return True, "Sent"
            return False, str(parsed.get("description") or body or "Telegram error")
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", errors="replace")
        except Exception:
            detail = str(e)
        return False, f"HTTP {e.code}: {detail[:240]}"
    except Exception as e:
        return False, str(e)[:240]


def format_scan_alert(
    kind: str,
    title: str,
    snippet: str,
    page_hint: str = "",
) -> str:
    """Short, readable Telegram alert body."""
    kind_label = {
        "timing": "Timing scan ready",
        "prediction": "Birth chart reading ready",
        "life_prediction": "Life prediction ready",
        "matching": "Horoscope matching ready",
        "numerology": "Numerology chart ready",
        "test": "Test alert",
    }.get(kind, "Scan ready")
    lines = [
        f"✨ {kind_label}",
        f"👤 {title or 'Native'}",
        "",
        (snippet or "").strip()[:900],
    ]
    if page_hint:
        lines += ["", f"📱 {page_hint}"]
    lines += ["", "— Jyotish Darshan"]
    return "\n".join(lines)


def notify_scan_complete(
    kind: str,
    title: str,
    snippet: str,
    page_hint: str = "",
    *,
    once_key: Optional[str] = None,
) -> Tuple[bool, str]:
    """Send alert if enabled. With ``once_key``, skip duplicates in this session."""
    cfg = get_telegram_config()
    if not cfg["enabled"]:
        return False, "Alerts off or not configured."

    if once_key:
        try:
            import streamlit as st
            sent = st.session_state.setdefault("_tg_sent_keys", set())
            if once_key in sent:
                return False, "Already notified for this scan in this session."
        except Exception:
            sent = None
    else:
        sent = None

    text = format_scan_alert(kind, title, snippet, page_hint)
    ok, detail = send_telegram_message(text)
    if ok and once_key and sent is not None:
        try:
            import streamlit as st
            st.session_state["_tg_sent_keys"].add(once_key)
        except Exception:
            pass
    return ok, detail


def prediction_alert_snippet(pred: Dict) -> str:
    """Compact snippet from a prediction dict."""
    parts = []
    name = pred.get("name") or "Native"
    summary = (pred.get("summary") or pred.get("opening") or "").strip()
    if summary:
        parts.append(summary[:320])
    timing = pred.get("timing") or {}
    maha = timing.get("current_maha")
    antar = timing.get("current_antar")
    if maha:
        line = f"Dasha: {maha}" + (f" / {antar}" if antar else "")
        if timing.get("maha_until"):
            line += f" (Maha until {timing['maha_until']})"
        parts.append(line)
    ts = pred.get("timing_summary") or {}
    cur = ts.get("current") or {}
    if cur.get("antar_theme"):
        parts.append(f"Flavour: {cur.get('antar_theme')}")
    brief = pred.get("position_brief") or {}
    if brief.get("summary"):
        parts.append(str(brief["summary"])[:220])
    return "\n".join(p for p in parts if p) or f"Reading for {name} is ready."


def timing_alert_snippet(summary: Dict) -> str:
    """Compact snippet from a timing summary dict."""
    cur = summary.get("current") or {}
    lines = [
        f"Now: {cur.get('maha') or '—'} / {cur.get('antar') or '—'}",
        f"Antar until: {cur.get('antar_until') or '—'}",
        f"Theme: {cur.get('maha_theme') or '—'} · {cur.get('antar_theme') or '—'}",
        f"Sade Sati: {cur.get('sade_sati') or '—'}",
    ]
    chapters = summary.get("chapters") or []
    if chapters:
        ch = next((c for c in chapters if c.get("is_current")), chapters[0])
        scores = ch.get("scores") or {}
        bits = [
            f"{a} {row['score']}" for a, row in list(scores.items())[:5]
        ]
        if bits:
            lines.append("Impact: " + " · ".join(bits))
        if ch.get("risks"):
            lines.append("Watch: " + "; ".join(ch["risks"][:2]))
        if ch.get("opportunities"):
            lines.append("Lean into: " + "; ".join(ch["opportunities"][:2]))
    return "\n".join(lines)
