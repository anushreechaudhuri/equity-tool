import streamlit as st
st.set_page_config(page_title="Visualize", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items={
         'Get Help': 'https://www.energy.gov/eere/buildings/building-technologies-office',
         'Report a bug': "https://github.com/anushreechaudhuri/equity-tool",
         'About': "### National Building Upgrade Challenge Equity Tool"
     }
)

st.title("Explore a National Map")

st.markdown("Collapse the sidebar to expand the map. [Click here](https://mit.carto.com/u/anuc/builder/0ea6ddd5-3c32-45c1-8468-dc16b7def05a/embed) to open the map on its own page. See [How-To: 🗺 Visualize](http://localhost:8501/#how-to-visualize) for a tutorial on how to use this map.")

st.components.v1.iframe(
    src="https://mit.carto.com/u/anuc/builder/0ea6ddd5-3c32-45c1-8468-dc16b7def05a/embed?state=%7B%22map%22%3A%7B%22ne%22%3A%5B19.228176737766262%2C-137.90039062500003%5D%2C%22sw%22%3A%5B60.108670463036%2C-57.74414062500001%5D%2C%22center%22%3A%5B42.94033923363183%2C-97.82226562500001%5D%2C%22zoom%22%3A4%7D%2C%22widgets%22%3A%7B%22da6b212a-c6cf-43f0-b5f4-f8b680f8cac5%22%3A%7B%22collapsed%22%3Atrue%7D%2C%22e905d706-9235-4988-a059-ae2568b71a7e%22%3A%7B%22normalized%22%3Atrue%2C%22collapsed%22%3Atrue%7D%2C%22b80be7f9-3e6e-4748-bc11-9d9a47938881%22%3A%7B%22normalized%22%3Atrue%2C%22collapsed%22%3Atrue%7D%7D%7D",
    height=520,
    scrolling=True,
)
