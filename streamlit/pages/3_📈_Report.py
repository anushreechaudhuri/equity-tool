import streamlit as st
import pandas as pd
import pickle
import numpy as np
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime
import base64
import pyproj
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


with st.spinner("Loading housing and census tract data..."):
    with open(DATA_PATH, "rb") as f:
        nhpd, dac, boundary = pickle.load(f)


@st.experimental_memo(show_spinner=False, max_entries=4, persist="disk")
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


with st.spinner("Loading boundary data..."):
    boundary = load_boundary(level)
    dac = dac.to_crs(boundary.crs)
    nhpd = nhpd.to_crs(boundary.crs)

selected = st.selectbox(
    options=boundary["NAME"].unique(), label=f"Select a {level}", index=1
)

with st.spinner("Loading results..."):
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

            dac_proj = dac_select.to_crs(pyproj.CRS.from_epsg(4326), inplace=False)
            dac_proj = dac_proj[~pd.isna(dac_proj.geometry)]
            colors = [
                "red" if row.DAC_status == "Disadvantaged" else "black"
                for _, row in dac_proj.iterrows()
            ]
            stroke_width = [
                5 if row.DAC_status == "Disadvantaged" else 0
                for _, row in dac_proj.iterrows()
            ]

            shape_geometry = json.loads(shape.geometry.to_json())
            # print(shape_geometry)
            shape_coords = shape_geometry["features"][0]["geometry"]["coordinates"]
            #st.write(shape_coords)
            type=shape_geometry["features"][0]["geometry"]["type"]
            if type == "Polygon":
                zoom, center = zoom_center(
                lons=[i[0] for i in shape_coords[0]], lats=[i[1] for i in shape_coords[0]]
            )
            else:
                zoom, center = zoom_center(
                lons=[i[0] for i in shape_coords[0][0]], lats=[i[1] for i in shape_coords[0][0]]
            )

            fig = px.choropleth_mapbox(
                dac_proj,
                geojson=dac_proj["geometry"],
                locations=dac_proj.index,
                color="avg_energy_burden_natl_pctile",
                color_continuous_scale="ylorbr",
                mapbox_style="carto-positron",
                zoom=0.9 * zoom,
                center=center,
                labels={
                    "avg_energy_burden_natl_pctile": "Energy Burden Percentile",
                    "DAC_status": "DAC Status",
                    "GEOID": "Census Tract ID",
                },
                hover_data={
                    "GEOID": True,
                    "DAC_status": True,
                    "avg_energy_burden_natl_pctile": True,
                },
                hover_name="DAC_status",
            )
            fig.update_layout(
                mapbox={
                    "style": "carto-positron",
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

            fig.update_geos(fitbounds="geojson", visible=False)
            fig.update_traces(
                marker_line_color=colors,
                marker_line_width=stroke_width,
                marker_opacity=0.5,
            )
            # List of lats and lons for nhpd
            lats = nhpd_select.lat
            lons = nhpd_select.lon

            # Save the map as an image before adding housing data to enable the report to display it
            png = fig.write_image("fig.png")
            # Add housing data to the map
            fig.add_scattermapbox(
                lat=lats,
                lon=lons,
                mode="markers+text",
                marker_size=5,
                marker_color="gray",
                opacity=0.5,
                text=[nhpd_select["Property Name"].values],
                )

            st.plotly_chart(fig, use_container_width=True)

            with open("fig.png", "rb") as file:
                btn = st.download_button(
                    label="Download Map",
                    data=file,
                    file_name=f"{shape.iloc[0]['NAME']}.png",
                )
        # Display the census tract and housing data for the selected boundary in tabular format and offer option to download
        if nhpd_select.empty == False:
            with st.expander("Housing Data"):
                nhpd_display = (
                    pd.DataFrame(nhpd_select.drop(["geometry"], axis=1).iloc[:, 8:])
                    .reset_index()
                    .drop(["index", "lat", "lon"], axis=1)
                )
                st.dataframe(nhpd_display)
                st.download_button(
                    label="Download Housing Data", data=nhpd_display.to_csv()
                )
        if dac_select.empty == False:
            with st.expander("Census Tract Data"):
                dac_display = (
                    pd.DataFrame(dac_select.drop(["geometry"], axis=1))
                    .reset_index()
                    .drop(["index"], axis=1)
                )
                st.dataframe(dac_display)
                st.download_button(
                    label="Download Census Tract Data", data=dac_display.to_csv()
                )
if dac_select.empty == False or nhpd_select.empty == False:

    with st.spinner("Generating report..."):
        # Open the map image saved earlier and add it to the report
        with open("fig.png", "rb") as f:
            encoded_string = base64.b64encode(f.read())
            map = encoded_string.decode("utf-8")
            map = '<img src="data:image/png;base64,{0}" class="w-full h-auto">'.format(map)
        # Call helper function to create report
        generate_from_data(shape, map, dac_select, nhpd_select)
        # Save as a PDF
        with open("out.pdf", "rb") as file:
            btn = st.download_button(
                label="Download Report",
                data=file,
                file_name=f"{shape.iloc[0]['NAME']}.pdf",
            )
