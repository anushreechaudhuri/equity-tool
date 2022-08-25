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
from mapbounds import generate_from_data, zoom_center
from pdfreport import generate_pdf

st.set_page_config(
    page_title="Report",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help':
        'https://www.energy.gov/eere/buildings/building-technologies-office',
        'Report a bug': "https://github.com/anushreechaudhuri/equity-tool",
        'About': "### National Building Upgrade Challenge Equity Tool"
    })
st.title("Generate a Report for Your Location")


def select_level():
    with st.form("Select Level"):
        level = st.radio(
            options=("Census Tract ID", "City", "County", "State",
                     "Tribe or Territory"),
            label="Search By",
            index=2,
        )
        if st.form_submit_button(
                "Submit", help="Select a geographic level to search by."):
            st.session_state["previous_level"] = level
            return level
        return st.session_state["previous_level"]


def select_location(boundary, level):
    with st.form("Select a Location"):
        shape = st.selectbox(options=boundary["NAME"].unique(),
                             label=f"Select a {level}",
                             index=1)
        with st.expander("Additional Report Parameters"):
            col1, col2, col3 = st.columns([1, 1, 1])
            eb = col1.slider(
                label="Energy Burden Percentile",
                min_value=0,
                max_value=100,
                value=(30, 100),
                step=1,
                help=
                "Use the slider to select a range of Energy Burden Percentile values. Only census tracts within the selected range will be included in the report."
            )
            dac_filter = col2.checkbox(
                label="Disadvantaged Community Status",
                value=True,
                help=
                "Check this box to only include Disadvantaged Census Tracts in the report."
            )
            qct_filter = col3.checkbox(
                label="Housing Tax Credit Eligible Status",
                value=False,
                help=
                "Check this box to only include Housing Tax Credit Eligible Census Tracts in the report."
            )
            col4, col5 = st.columns([1, 1])

            cover_page = col4.checkbox(
                label="Include Cover Page Only",
                value=False,
                help=
                "Check this box to only include a cover page with summary statistics of the selected location in the report."
            )
            include_nhpd = col5.checkbox(
                label="Include Affordable Housing List",
                value=False,
                help="Check this box to include a full list of every affordable housing property in the report. You can download the housing data separately under the Housing Data tab below."
            )
        submitted = st.form_submit_button(
            "Search",
            help=
            "Select a location by typing in a location name or selecting from the dropdown. Expand the Additional Report Parameters section to change what data will be included in the report."
        )
        if submitted:
            return (shape, eb, dac_filter, qct_filter, cover_page, include_nhpd)

    return None


def load_dac():
    with st.spinner("Loading census tract data..."):
        with open('../data/report_data/dac.pkl', "rb") as f:
            dac = pickle.load(f)
    return dac


def load_nhpd():
    with st.spinner("Loading NHPD data..."):
        with open('../data/report_data/nhpd.pkl', "rb") as f:
            nhpd = pickle.load(f)
    return nhpd


def load_boundary(level):
    with st.spinner(f"Loading {level} boundaries..."):
        if level == "Census Tract ID":
            with open('../data/report_data/dac.pkl', "rb") as f:
                dac_boundary = pickle.load(f)
            dac_boundary["NAME"] = dac_boundary["GEOID"]
            return dac_boundary[["NAME", "geometry"]]
        elif level == "City":
            with open('../data/report_data/dac.pkl', "rb") as f:
                dac_boundary = pickle.load(f)
            # Drop columns where there is no city name
            dac_boundary = dac_boundary[dac_boundary["city"].notna()]
            dac_boundary["NAME"] = dac_boundary["city"] + " (" + dac_boundary["county_name"] + ")"
            return dac_boundary[["city", "county_name", "NAME", "geometry"]]
        elif level == "County":
            with open('../data/report_data/counties.pkl', "rb") as f:
                return pickle.load(f)
        elif level == "State":
            with open('../data/report_data/states.pkl', "rb") as f:
                return pickle.load(f)
        else:
            with open('../data/report_data/tt_shp.pkl', "rb") as f:
                return pickle.load(f)


def dac_selector(dac, shape, level):
    if level == "Census Tract ID":
        return dac.drop(dac[dac["GEOID"].str[:].ne(
            shape["NAME"].values[0])].index)
    if level == "City":
        dac = dac.drop(dac[dac["city"].str[:].ne(
            shape["city"].values[0])].index)
        return dac.drop(dac[dac["county_name"].str[:].ne(
            shape["county_name"].values[0])].index)
    if level == "County":
        return dac.drop(dac[dac["GEOID"].str[:5].ne(
            shape["GEOID"].values[0])].index)
    if level == "State":
        return dac.drop(dac[dac["GEOID"].str[:2].ne(
            shape["GEOID"].values[0])].index)
    else:
        try:
            dac_select = gpd.sjoin(dac,
                                   shape,
                                   how="inner",
                                   predicate="intersects")
            dac_select.rename(columns={"GEOID_left": "GEOID"}, inplace=True)
            return dac_select.loc[:, "GEOID":"geometry"].reset_index()
        except:
            # Exact match
            return dac.drop(dac[dac["GEOID"].str[:].ne(
                shape["GEOID"].values[0])].index)


def create_map(shape, dac_select, nhpd_select):
    with st.expander("Map", expanded=True):
        shape_geometry = json.loads(shape.geometry.to_json())
        shape_coords = shape_geometry["features"][0]["geometry"]["coordinates"]
        type = shape_geometry["features"][0]["geometry"]["type"]
        if type == "Polygon":
            zoom, center = zoom_center(lons=[i[0] for i in shape_coords[0]],
                                       lats=[i[1] for i in shape_coords[0]])
        else:  # For multipolygon - with islands
            zooms_centers = []
            for polygon in range(len(shape_coords)):
                zoom, center = zoom_center(
                    lons=[i[0] for i in shape_coords[polygon][0]],
                    lats=[i[1] for i in shape_coords[polygon][0]])
                zooms_centers.append((zoom, center))
            # Choose smallest zoom as zoom level
            zoom = min([i[0] for i in zooms_centers])
            # Choose center of that zoom
            center = [i[1] for i in zooms_centers if i[0] == zoom][0]
            zoom = zoom - 1
        with open("legend.png", "rb") as image_file:
            encoded_string = base64.b64encode(
                image_file.read()).decode('utf-8')
        colors = [
            "red" if row.DAC_status == "Disadvantaged" else "black"
            for _, row in dac_select.iterrows()
        ]
        stroke_width = [
            5 if row.DAC_status == "Disadvantaged" else 0
            for _, row in dac_select.iterrows()
        ]

        fig = px.choropleth_mapbox(
            dac_select,
            geojson=dac_select["geometry"],
            locations=dac_select.index,
            color="avg_energy_burden_natl_pctile",
            color_continuous_scale="ylorbr",
            mapbox_style="carto-positron",
            zoom=0.8 * zoom,
            center=center,
            labels={
                "avg_energy_burden_natl_pctile": "Energy Burden Percentile",
                "GEOID": "Census Tract ID",
                "QCT_status": "Housing Tax Credit Status"
            },
            hover_data={
                "GEOID": True,
                "avg_energy_burden_natl_pctile": True,
                "QCT_status": True
            },
            hover_name="DAC_status",
        )
        fig.update_layout(margin=dict(l=20, r=20, t=0, b=0),
            mapbox={
                "style":
                "carto-positron",
                "layers": [
                    {
                        "source": json.loads(shape.geometry.to_json()),
                        "type": "line",
                        "color": "gray",
                        "line": {
                            "width": 3
                        },
                        "below": "traces",
                    },
                ],
            })

        fig.update_geos(fitbounds="geojson", visible=False)
        fig.update_traces(
            marker_line_color=colors,
            marker_line_width=stroke_width,
            marker_opacity=0.5,
        )
        # Save the map as an image before adding housing data to enable the report to display it
        png = fig.write_image("fig.png")
        # Add housing data to the map
        if not nhpd_select.empty:
            fig.add_scattermapbox(
                lat=nhpd_select.lat,
                lon=nhpd_select.lon,
                mode="markers+text",
                marker_size=10,
                marker_color="black",
                opacity=0.5,
                text=[i for i in nhpd_select["Property Name"].values],
            )
        # Plot map on Streamlit page
        st.plotly_chart(fig, use_container_width=True)
        st.components.v1.html(html=f'<img src="data:image/png;base64,{encoded_string}" alt="0" style="width: 35%; display: block; margin-left: 20px; margin-right: auto; margin-top: 0px;" align="left">', height=50)        # Create button to download map image
        with open("fig.png", "rb") as file:
            btn = st.download_button(
                label="Download Map",
                data=file,
                file_name=f"{shape.iloc[0]['NAME']}.png",
            )


def report_data_filter(dac_select, eb, dac_filter, qct_filter):
    # Filter dac_select by energy burden percentile
    dac_select = dac_select.loc[
        (dac_select["avg_energy_burden_natl_pctile"] >= eb[0])
        & (dac_select["avg_energy_burden_natl_pctile"] <= eb[1])]
    if dac_filter:
        # Filter dac_select by DAC status
        dac_select = dac_select.loc[dac_select["DAC_status"] ==
                                    "Disadvantaged"]
    if qct_filter:
        # Filter dac_select by QCT status
        dac_select = dac_select.loc[dac_select["QCT_status"] == "Eligible"]            # Create a new column called "DAC_check" with a checkmark if the row has "DAC_status" == "Disadvantaged" and a cross if it doesn't
    dac_select["DAC_check"] = dac_select["DAC_status"].apply(lambda x: "Yes" if x == "Disadvantaged" else "No")
    # Create a new column called "QCT_check" with a checkmark if the row has "QCT_status" == "Eligible" and a cross if it doesn't
    dac_select["QCT_check"] = dac_select["QCT_status"].apply(lambda x: "Yes" if x == "Eligible" else "No")
    return dac_select


if __name__ == "__main__":
    if "previous_level" not in st.session_state:
        st.session_state["previous_level"] = None
    level = select_level()
    if level == None:
        st.write("Click the Submit button to continue.")
        st.stop()
    with st.spinner("Loading boundary data..."):
        boundary = load_boundary(level)
    output = select_location(boundary, level)
    if output == None:
        st.write("Click the Search button to continue.")
        st.stop()
    location, eb, dac_filter, qct_filter, cover_page, include_nhpd = output
    with st.spinner("Loading results (may take up to one minute)..."):
        dac = load_dac()
        nhpd = load_nhpd()
        shape = boundary.loc[boundary["NAME"] == location]
        nhpd_select = gpd.sjoin(shape,
                                nhpd,
                                how="inner",
                                predicate="intersects")
        dac_select = dac_selector(dac, shape, level)
        if nhpd_select.empty:
            st.write("No housing data found for this location.")
        if dac_select.empty:
            st.write("No census tracts found for this location.")
        if not nhpd_select.empty:
            with st.expander("Housing Data"):
                nhpd_display = (pd.DataFrame(
                    nhpd_select.drop(
                        ["geometry"],
                        axis=1).loc[:, 'Property Name':]).reset_index().drop(
                            ["index", "lat", "lon"], axis=1))
                st.dataframe(nhpd_display)
                st.download_button(
                    label="Download Housing Data",
                    data=nhpd_display.to_csv(),
                    help=
                    "Download housing data as a CSV file and reset the search."
                )
        if not dac_select.empty:
            with st.expander("Census Tract Data"):
                dac_display = (pd.DataFrame(
                    dac_select.drop(["geometry"],
                                    axis=1)).reset_index().drop(["index"],
                                                                axis=1))
                st.dataframe(dac_display)
                st.download_button(
                    label="Download Census Tract Data",
                    data=dac_display.to_csv(),
                    help=
                    "Download census tract data as a CSV file and reset the search."
                )
        if not nhpd_select.empty or not dac_select.empty:
            create_map(shape, dac_select, nhpd_select)
            if not dac_select.empty:
                with st.spinner("Generating report..."):
                    # Open the map image saved earlier and add it to the report
                    dac_select = report_data_filter(dac_select, eb, dac_filter, qct_filter)
                    generate_pdf(shape, "fig.png", dac_select, nhpd_select, cover_page, include_nhpd, out_path="report.pdf")
                    # Save as a PDF
                    with open("report.pdf", "rb") as file:
                        with st.expander("Report"):
                            encoded_string = base64.b64encode(file.read()).decode('utf-8')
                            pdf_display = f'<embed src="data:application/pdf;base64,{encoded_string}" width="700" height="400" type="application/pdf">'
                            st.markdown(pdf_display, unsafe_allow_html=True)
                        btn = st.download_button(
                            label="Download Report",
                            data=file,
                            file_name=f"{shape.iloc[0]['NAME']}.pdf",
                            help=
                            "Download the report as a PDF file and open in your browser or PDF viewer, or expand the Report section above."
                        )
