import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import s3fs

# Enter file paths
NHPD = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/report/nhpd.geojson"
DAC = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/report/dac.geojson"
TT = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/report/tt_shp.geojson"
COUNTIES = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/report/counties.geojson"
STATES = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/report/states.geojson"

st.set_page_config(layout="wide")
st.title("Generate a Report for Your Location")
s3 = s3fs.S3FileSystem(anon=False)

level = st.selectbox(
    options=("Census Tract ID", "County", "State", "Tribe and Territory"),
    label="Search By",
    index=1,
)


@st.experimental_memo
def load_nhpd():
    return gpd.read_file(f"s3://equity-tool/report/nhpd.geojson")


@st.experimental_memo
def load_dac():
    return gpd.read_file(f"s3://equity-tool/report/dac.geojson")


@st.experimental_memo
def load_boundary(level):
    if level == "Census Tract ID":
        dac_boundary = load_dac()
        dac_boundary["NAME"] = dac_boundary["GEOID"]
        return dac_boundary
    elif level == "County":
        return gpd.read_file(f"s3://equity-tool/report/counties.geojson")
    elif level == "State":
        return gpd.read_file(f"s3://equity-tool/report/states.geojson")
    else:
        return gpd.read_file(f"s3://equity-tool/report/tt_shp.geojson")


with st.spinner("Loading housing data..."):
    nhpd = load_nhpd()
with st.spinner("Loading demographic data..."):
    dac = load_dac()
with st.spinner("Loading boundary data..."):
    boundary = load_boundary(level)
    dac = dac.to_crs(boundary.crs)
    nhpd = nhpd.to_crs(boundary.crs)


selected = st.selectbox(
    options=boundary["NAME"].unique(), label=f"Select a {level}", index=1
)

with st.spinner("Loading report - map and tables..."):
    # Find the row in counties that corresponds to selected "county"
    shape = boundary.loc[boundary["NAME"] == selected]
    # Spatial join of nhpd and boundary shape
    nhpd_select = gpd.sjoin(shape, nhpd, how="inner", predicate="intersects")
    # Spatial join of dac and boundary shape
    def dac_select(shape, level):
        if level == "Census Tract ID":
            return shape
        if level == "County":
            # Find first five characters of GEOID in dacs
            # return dac.loc[dac["GEOID"].str[:5].equals(shape["GEOID"].values[0][:5])]
            return dac.drop(
                dac[dac["GEOID"].str[:5].ne(shape["GEOID"].values[0])].index
            )
        if level == "State":
            return dac.drop(
                dac[dac["GEOID"].str[:2].ne(shape["GEOID"].values[0])].index
            )
        else:
            return dac.drop(dac[dac["GEOID"].str[:].ne(shape["GEOID"].values[0])].index)

    dac_select = dac_select(shape, level)
    if nhpd_select.empty:
        st.write("No housing data found for this location.")
    if dac_select.empty:
        st.write("No census tracts found for this location.")
    if dac_select.empty == False or nhpd_select.empty == False:
        with st.expander("Map"):
            fig = (
                px.scatter_mapbox(
                    nhpd_select,
                    lat="lat",
                    lon="lon",
                    hover_data=["Property Name", "Street Address"],
                )
                .update_traces(marker={"size": 5, "opacity": 0.5, "color": "red"})
                .update_layout(
                    mapbox={
                        "style": "carto-positron",
                        "layers": [
                            {
                                "source": json.loads(dac_select.geometry.to_json()),
                                "below": "traces",
                                "type": "fill",
                                "color": "blue",
                                "opacity": 0.2,
                            },
                            {
                                "source": json.loads(shape.geometry.to_json()),
                                "type": "line",
                                "color": "gray",
                                "line": {"width": 3},
                                "below": "traces",
                            },
                        ],
                    },
                    margin={"l": 0, "r": 0, "t": 0, "b": 0},
                )
            )
            fig.update_geos(fitbounds="locations")
            st.plotly_chart(fig, use_container_width=True)
            image = fig.write_image("fig.png")
            with open("fig.png", "rb") as file:
                btn = st.download_button(
                    label="Download Map", data=file, file_name="fig.png"
                )
        with st.expander("Tables"):
            nhpd_display = (
                pd.DataFrame(nhpd_select.drop(["geometry"], axis=1).iloc[:, 8:])
                .reset_index()
                .drop(["index", "lat", "lon"], axis=1)
            )
            dac_display = (
                pd.DataFrame(dac_select.drop(["geometry"], axis=1))
                .reset_index()
                .drop(["index"], axis=1)
            )
            display_housing = st.checkbox("Show housing data", value=True)
            if display_housing:
                st.dataframe(nhpd_display)
            st.download_button(
                label="Download Housing Data", data=nhpd_display.to_csv()
            )
            display_tracts = st.checkbox("Show census tracts", value=False)
            if display_tracts:
                st.dataframe(dac_display)
            st.download_button(
                label="Download Census Tract Data", data=dac_display.to_csv()
            )
        with st.spinner("Generating report..."):
            st.download_button(label="Download Report", data=nhpd_select.to_csv())
