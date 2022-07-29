import streamlit as st

st.set_page_config(layout="wide")
st.title("Explore a National Map")

st.components.v1.iframe(
    src="https://mit.carto.com/u/anuc/builder/0ea6ddd5-3c32-45c1-8468-dc16b7def05a/embed",
    height=520,
    scrolling=True,
)
