import streamlit as st

st.set_page_config(page_title="Sources", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items={
         'Get Help': 'https://www.energy.gov/eere/buildings/building-technologies-office',
         'Report a bug': "https://github.com/anushreechaudhuri/equity-tool",
         'About': "### National Building Upgrade Challenge Equity Tool"
     }
)
# Paste Page Content Here
st.title("Data Sources")
st.header("Building Upgrade Challenge Equity Tool: Data Definitions")
st.markdown("The data definitions for the data used in this tool are available for download. The census tract indicators are included on the first sheet of the Excel file and the housing indicators are on the second sheet.")
with open("data_definitions.xlsx", "rb") as file:
    btn = st.download_button(
        label="Download Data Definitions",
        data=file,
        file_name="data_definitions.xlsx",
    )
st.header("Justice40 Disadvantaged Census Tracts")
st.markdown("More information about the methodology used to determine the Disadvantaged status of census tracts can be found on the [Department of Energy (DOE) Justice40 page](https://www.energy.gov/diversity/justice40-initiative). The DOE has also created a [Disadvantaged Communities Reporter Tool](https://energyjustice.egs.anl.gov/) which provides a national map, detailed information on individual census tracts, and further links to download raw data.")
st.header("National Housing Preservation Database")
st.markdown("The National Housing Preservation Database (NHPD) is licensed for use by the Department of Energy in this public-facing mapping and reporting tool. The data can be accessed for personal use by [registering on this site](https://preservationdatabase.org/register-as-a-new-user/). The full NHPD [Data Dictionary](https://preservationdatabase.org/documentation/data-dictionary/) and [Data Sources](https://preservationdatabase.org/documentation/data-sources/) are also accessible on their website.")
st.header("Qualified Census Tracts")
st.markdown("The list of 2022 Qualified Census Tracts for the Low-Income Housing Tax Credit are available on the [US Department of Housing and Urban Development’s site](https://www.huduser.gov/portal/qct/index.html).")
st.header("County and State Boundaries")
st.markdown("This tool uses [2021 Cartographic Boundary Files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html) at the 1 : 500,000 national scale for county and state boundaries.")
st.header("Access and Use")
st.markdown("All data, with the exception of the National Housing Preservation Database (NHPD), are available for public use. The NHPD is available for personal use by the public but must be licensed for use in a public-facing tool or report. The code for this tool is available on [GitHub](https://github.com/anushreechaudhuri/equity-tool) under an MIT License.")
st.header("Questions about Tool Development")
st.markdown("Contact the [DOE Building Technologies Office](adam.hasz@ee.doe.gov) for questions about the National Building Upgrade Challenge. Contact [Argonne National Laboratory’s Data Team](epfister@anl.gov) for questions about tool development.")