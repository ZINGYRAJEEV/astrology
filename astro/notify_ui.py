"""Streamlit UI for Telegram alert settings."""

from __future__ import annotations

import streamlit as st

from .notify import get_telegram_config, notify_scan_complete, send_telegram_message


def render_telegram_settings(*, expanded: bool = False, key_prefix: str = "tg") -> None:
    """Expander: enable alerts, paste chat id / optional token, send test."""
    cfg = get_telegram_config()
    ui = st.session_state.setdefault("telegram_ui", {})

    with st.expander("Telegram alerts", expanded=expanded):
        st.caption(
            "Get a short message on Telegram when a timing scan or reading finishes. "
            "Create a bot with @BotFather, start a chat with it, then paste your Chat ID "
            "(from @userinfobot). Prefer putting the **bot token** in Streamlit secrets."
        )
        st.markdown(
            "Secrets file (local) or Streamlit Cloud → Settings → Secrets:\n\n"
            "```toml\n[telegram]\nbot_token = \"123456:ABC...\"\nchat_id = \"123456789\"\n```"
        )

        enabled = st.toggle(
            "Send me Telegram alerts after scans",
            value=bool(ui.get("enabled", cfg["configured"])),
            key=f"{key_prefix}_enabled",
        )
        chat_default = str(ui.get("chat_id") or cfg.get("chat_id") or "")
        chat_id = st.text_input(
            "Your Telegram chat ID",
            value=chat_default,
            key=f"{key_prefix}_chat",
            help="Numeric ID for your user or group. Required.",
        )
        use_custom_token = st.checkbox(
            "Use a bot token here (only for local testing — prefer secrets)",
            value=bool(ui.get("bot_token")),
            key=f"{key_prefix}_tok_chk",
        )
        bot_token = ""
        if use_custom_token:
            bot_token = st.text_input(
                "Bot token",
                value=ui.get("bot_token") or "",
                type="password",
                key=f"{key_prefix}_token",
            )

        st.session_state["telegram_ui"] = {
            "enabled": enabled,
            "chat_id": chat_id.strip(),
            "bot_token": bot_token.strip() if use_custom_token else ui.get("bot_token", ""),
        }
        # If not using custom token field, keep prior UI token only if checkbox was on before;
        # otherwise clear UI token so secrets are used.
        if not use_custom_token:
            st.session_state["telegram_ui"]["bot_token"] = ""

        cfg2 = get_telegram_config()
        if cfg2["configured"]:
            st.success(
                f"Telegram ready ({cfg2['source']}). "
                + ("Alerts ON." if cfg2["enabled"] else "Alerts toggled OFF.")
            )
        else:
            st.warning("Not configured yet — add bot_token (secrets) and chat_id.")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Send test alert", key=f"{key_prefix}_test", use_container_width=True):
                ok, detail = notify_scan_complete(
                    "test",
                    "Jyotish Darshan",
                    "If you see this, Telegram alerts are working.",
                    "Open Timing Summary or Horoscope & Reading in the app.",
                )
                if ok:
                    st.success("Test alert sent — check Telegram.")
                else:
                    st.error(f"Could not send: {detail}")
        with c2:
            if st.button("Clear alert session lock", key=f"{key_prefix}_clear", use_container_width=True):
                st.session_state["_tg_sent_keys"] = set()
                st.caption("You can receive the same scan alert again this session.")
