import streamlit as st

st.set_page_config(layout="wide")
st.title("Data Sources and Methodology")
st.markdown("## Justice40 Disadvantaged Census Tracts")
st.markdown("The Disadvantaged Communities Reporter is DOE's mapping tool intended to allow users to explore and produce reports on the census tracts DOE has categorized as DACs. The tool shows census tracts categorized as DACs in blue and federally recognized tribal lands and U.S. territories in green. The left panel enables a location search by either common geographies (zip, city county), tract number (GEOID), tribal name, or territory name. The left display shows the top 10 burden indicators for the selected census tract and the report shows values for all 36 burden indicators for the selected census tract. Additional information for federally recognized tribal lands and U.S. territories is forthcoming.")
st.button("Access DOE’s Justice40 Tool")
st.markdown("## National Housing Preservation Database")
st.button("Access the NHPD")
st.markdown("## Qualified Census Tracts")
st.button("Access the HUD QCT Data")
st.markdown("## County and State Boundaries")
st.button("Access the Census Cartographic Boundaries")
st.markdown("## Data Access and Use")
st.markdown("## Questions about Tool Development")

