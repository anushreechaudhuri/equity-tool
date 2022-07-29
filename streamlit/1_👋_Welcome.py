import streamlit as st

st.set_page_config(layout="wide")
st.title("Welcome to the Equity Tool!")

# Embed a an iframe in Streamlit

st.text("There will be information on the tool and usage here, and demo videos!")


st.components.v1.iframe(
    src="https://www.loom.com/embed/a3f0d4a9cd0148dd897318a1265c4bbb",
    height=520,
    scrolling=True,
)
