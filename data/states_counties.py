import pandas as pd
import geopandas as gpd
import numpy as np
import sqlite3 as sql
import subprocess
import sys
import os
from os import mkdir
from os.path import exists, sep
import pyproj
from shapely.validation import explain_validity, make_valid


# COUNTIES
counties = gpd.read_file("raw/counties_500k_2021.zip")
# Change "NAME" column to append "STUSPS" to the end of the name
counties["COUNTY"] = counties["NAMELSAD"]
counties["STATE"] = counties["STATE_NAME"]
counties["NAME"] = counties["NAMELSAD"] + ", " + counties["STUSPS"]
# Change order of columns
counties = counties[[
    "NAME", "GEOID", "STATE", "COUNTY", "STATEFP", "COUNTYFP", "STUSPS",
    "geometry"
]]
# Sort alphabetically by name
counties = counties.sort_values(by="NAME")
# Save to geojson in CARTO and REPORT
# counties.to_file("carto_data/counties.geojson", driver="GeoJSON")
counties = counties.to_crs(pyproj.CRS.from_epsg(4269), inplace=False)
for i, row in counties.iterrows():
    counties.at[i, "geometry"] = make_valid(row["geometry"])
counties.to_file("report_data/counties.geojson", driver="GeoJSON")
# Save to pickle in REPORT
counties.to_pickle("report_data/counties.pkl")
print("Counties file exported")

# STATES
states = gpd.read_file("raw/states_500k_2021.zip")
states = states[["NAME", "STUSPS", "GEOID", "STATEFP", "geometry"]]
# Remove rows where STATEFP = 60, 66, 69, 72, 78 (these are territories, not states)
states = states[~states["STATEFP"].isin(["60", "66", "69", "72", "78"])]
# Sort alphabetically by name
states = states.sort_values(by="NAME")
states = states.to_crs(pyproj.CRS.from_epsg(4269), inplace=False)
# Save to geojson in REPORT
states.to_file("report_data/states.geojson", driver="GeoJSON")
# Save to pickle in REPORT
states.to_pickle("report_data/states.pkl")
print("States file exported")
