import streamlit as st
import pandas as pd
import pickle
import numpy as np
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import s3fs
from datetime import datetime
import base64
import subprocess
from helpers import generate_from_data, zoom_center


# Enter file paths
DATA_PATH = (
    "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app/equity-tool/DATA.pkl"
)
NHPD = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/report/nhpd.geojson"
DAC = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/report/dac.geojson"
TT = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/report/tt_shp.geojson"
COUNTIES = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/report/counties.geojson"
STATES = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/report/states.geojson"
s3 = s3fs.S3FileSystem(anon=False)

st.set_page_config(layout="wide")
st.title("Generate a Report for Your Location")

level = st.selectbox(
    options=("Census Tract ID", "County", "State", "Tribe and Territory"),
    label="Search By",
    index=1,
)


# @st.experimental_memo(show_spinner=False, max_entries=1, persist="disk")
# def load_nhpd():
#     return gpd.read_file(f"s3://equity-tool/report/nhpd.geojson")


# @st.experimental_memo
# def load_dac():
#     return gpd.read_file(f"s3://equity-tool/report/dac.geojson")


with st.spinner("Loading NHPD, DAC, Boundary Data..."):
    with open(DATA_PATH, "rb") as f:
        nhpd, dac, boundary = pickle.load(f)


@st.experimental_memo
def load_boundary(level):
    if level == "Census Tract ID":
        dac_boundary = dac.copy()
        dac_boundary["NAME"] = dac_boundary["GEOID"]
        return dac_boundary
    elif level == "County":
        return gpd.read_file(COUNTIES)
    elif level == "State":
        return gpd.read_file(STATES)
    else:
        return gpd.read_file(TT)


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
    def dac_selector(shape, level):
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

    dac_select = dac_selector(shape, level)
    if nhpd_select.empty:
        st.write("No housing data found for this location.")
    if dac_select.empty:
        st.write("No census tracts found for this location.")
    if dac_select.empty == False or nhpd_select.empty == False:
        with st.expander("Map"):
            import pyproj
            import pandas as pd

            dac_proj = dac_select.to_crs(pyproj.CRS.from_epsg(4326), inplace=False)
            dac_proj = dac_proj[~pd.isna(dac_proj.geometry)]
            colors = [
                "red" if row.DAC_status == "Disadvantaged" else "black"
                for _, row in dac_proj.iterrows()
            ]
            stroke_width = [
                2 if row.DAC_status == "Disadvantaged" else 0
                for _, row in dac_proj.iterrows()
            ]

            x = json.loads(shape.geometry.to_json())
            coords = x["features"][0]["geometry"]["coordinates"]
            zoom, center = zoom_center(
                lons=[i[0] for i in coords[0]], lats=[i[1] for i in coords[0]]
            )

            fig = px.choropleth_mapbox(
                dac_proj,
                geojson=dac_proj["geometry"],
                locations=dac_proj.index,
                color="avg_energy_burden_natl_pctile",
                mapbox_style="white-bg",
                zoom=0.9 * zoom,
                center=center,
            )
            fig.update_layout(
                mapbox={
                    "style": "white-bg",
                    "layers": [
                        {
                            "source": json.loads(shape.geometry.to_json()),
                            "type": "line",
                            "color": "gray",
                            "line": {"width": 3},
                            "below": "traces",
                        },
                    ],
                }
            )

            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_traces(
                marker_line_color=colors,
                marker_line_width=stroke_width,
                marker_opacity=0.3,
            )

            lats = nhpd_select.lat
            lons = nhpd_select.lon

            png = fig.write_image("fig.png")

            fig.add_scattermapbox(
                lat=lats,
                lon=lons,
                mode="markers+text",
                marker_size=3,
                marker_color="green",
            )

            st.plotly_chart(fig, use_container_width=True)

            with open("fig.png", "rb") as file:
                btn = st.download_button(
                    label="Download Map",
                    data=file,
                    file_name=f"{shape.iloc[0]['NAME']}.png",
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
            image = {}

            with open("fig.png", "rb") as f:
                encoded_string = base64.b64encode(f.read())
                image["map"] = encoded_string.decode("utf-8")
                image[
                    "map"
                ] = '<img src="data:image/png;base64,{0}" class="w-full h-auto">'.format(
                    image["map"]
                )
            generate_from_data(shape, image["map"], dac_select, nhpd_select)

            with open("out.pdf", "rb") as file:
                btn = st.download_button(
                    label="Download Report",
                    data=file,
                    file_name=f"{shape.iloc[0]['NAME']}.pdf",
                )
