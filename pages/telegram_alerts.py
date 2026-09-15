"""Telegram Alerts — configure scan notifications."""

from __future__ import annotations

import streamlit as st

from astro.notify_ui import render_telegram_settings
from astro.notify import get_telegram_config

st.set_page_config(page_title="Telegram Alerts", page_icon="\U0001f4f1", layout="wide")

st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(180deg,#070912,#0c1020); color:#e8ebf2; }
      h1,h2,h3 { color:#f5c542 !important; font-family:'Georgia',serif; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# \U0001f4f1 Telegram Alerts")
st.caption(
    "Get a short Telegram message when a Timing scan or birth-chart reading finishes."
)

st.markdown(
    """
### Setup (once)
1. Open Telegram → search **@BotFather** → `/newbot` → copy the **bot token**.
2. Message your new bot once (press Start).
3. Get your **chat ID** from **@userinfobot** (or any “get chat id” bot).
4. Put the token in Streamlit **secrets** (recommended), paste chat ID below, enable alerts.
5. Click **Send test alert**, then run a Timing Summary or Horoscope reading.
"""
)

render_telegram_settings(expanded=True, key_prefix="tg_page")

cfg = get_telegram_config()
st.markdown("### What triggers an alert")
st.markdown(
    """
- **Timing Summary** — after the timing map is built (once per chart / date / horizon in a session)
- **Horoscope & Reading → Your Report** — after the prediction is generated (once per chart / intent)
- **Life Prediction** — after you click **Generate Prediction**
"""
)
if cfg["enabled"]:
    st.success("Alerts are ON for this session.")
elif cfg["configured"]:
    st.info("Configured but toggled off — enable the switch above.")
else:
    st.warning("Configure bot token + chat ID to enable alerts.")
