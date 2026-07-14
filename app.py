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
        "pages/daily_panchang.py",
        title="Daily Panchang",
        icon="\U0001f4c5",
    ),
    st.Page(
        "pages/life_prediction.py",
        title="Life Prediction",
        icon="\U0001f52e",
    ),
])
pg.run()
