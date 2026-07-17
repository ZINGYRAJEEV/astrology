"""Jyotish Darshan — navigation entrypoint."""

import streamlit as st

pg = st.navigation([
    st.Page(
        "pages/horoscope.py",
        title="Horoscope & Reading",
        icon="\u2728",
        default=True,
    ),
    st.Page(
        "pages/today_dashboard.py",
        title="Today for You",
        icon="\U0001f31e",
    ),
    st.Page(
        "pages/daily_panchang.py",
        title="Daily Panchang",
        icon="\U0001f4c5",
    ),
    st.Page(
        "pages/life_prediction.py",
        title="Life Prediction",
        icon="\U0001f52e",
    ),
    st.Page(
        "pages/muhurta_finder.py",
        title="Muhurta Finder",
        icon="\U0001f550",
    ),
    st.Page(
        "pages/horoscope_matching.py",
        title="Horoscope Matching",
        icon="\U0001f491",
    ),
])
pg.run()
