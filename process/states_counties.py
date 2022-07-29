import pandas as pd
import geopandas as gpd
import numpy as np
import sqlite3 as sql
import subprocess
import sys
import os
from os import mkdir
from os.path import exists, sep

WD = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data"
RAW = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/raw"
SQL_OUTPUT = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/sql_output"
CARTO = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/carto"
REPORT = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/report"


# COUNTIES
os.chdir(RAW)
counties = gpd.read_file("counties_500k_2021.zip")
# Change "NAME" column to append "STUSPS" to the end of the name
counties["COUNTY"] = counties["NAMELSAD"]
counties["STATE"] = counties["STATE_NAME"]
counties["NAME"] = counties["NAMELSAD"] + ", " + counties["STUSPS"]
# Change order of columns
counties = counties[
    ["NAME", "GEOID", "STATE", "COUNTY", "STATEFP", "COUNTYFP", "STUSPS", "geometry"]
]
# Sort alphabetically by name
counties = counties.sort_values(by="NAME")
# Save to geojson in CARTO and REPORT
os.chdir(CARTO)
counties.to_file("counties.geojson", driver="GeoJSON")
os.chdir(REPORT)
counties.to_file("counties.geojson", driver="GeoJSON")

# STATES
os.chdir(RAW)
states = gpd.read_file("states_500k_2021.zip")
states = states[["NAME", "STUSPS", "GEOID", "STATEFP", "geometry"]]
# Remove rows where STATEFP = 60, 66, 69, 72, 78 (these are territories, not states)
states = states[~states["STATEFP"].isin(["60", "66", "69", "72", "78"])]
# Sort alphabetically by name
states = states.sort_values(by="NAME")
# Save to geojson in REPORT
os.chdir(REPORT)
states.to_file("states.geojson", driver="GeoJSON")
