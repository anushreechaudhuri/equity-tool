# NHPD Carto -> Save as a CSV to reduce storage on Carto server
# NHPD for Report -> Clean the lat lon and save as spatial file and pickle file for quick loading in app

import pandas as pd
import geopandas as gpd
import numpy as np
import sqlite3 as sql
import subprocess
import sys
import os
from os import mkdir
from os.path import exists, sep
import pickle
import pyproj

nhpd = pd.read_csv("raw/nhpd.csv")

nhpd = nhpd[[
    "Property Name",
    "Street Address",
    "City",
    "State",
    "Zip Code",
    "Subsidy Status",
    "Subsidy Name",
    "Subsidy Subname",
    "Start Date",
    "End Date",
    "Assisted Units",
    "Owner Name",
    "Owner Type",
    "0-1 Bedroom Units",
    "Two Bedroom Units",
    "Three+ Bedroom Units",
    "Target Population",
    "Earliest Construction Date",
    "Latest Construction Date",
    "Rent to FMR Ratio",
    "Known Total Units",
    "Inactive Status Description",
    "Latitude",
    "Longitude",
]]

carto_nhpd = nhpd[[]]

# Rename columns in Carto NHPD
carto_nhpd.rename(
    columns={
        "Property Name": "name",
        "Street Address": "add",
        "City": "city",
        "State": "state",
        "Zip Code": "zip",
        "Subsidy Status": "status",
        "Subsidy Name": "subsidy",
        "Subsidy Subname": "subnm",
        "Start Date": "start",
        "End Date": "end",
        "Assisted Units": "units",
        "Owner Name": "owner",
        "Owner Type": "otype",
        "0-1 Bedroom Units": "0-1",
        "Two Bedroom Units": "2-4",
        "Three+ Bedroom Units": "5-+",
        "Target Population": "pop",
        "Earliest Construction Date": "econ",
        "Latest Construction Date": "lcon",
        "Rent to FMR Ratio": "rtfmr",
        "Known Total Units": "totun",
        "Inactive Status Description": "inact",
        "Latitude": "latitude",
        "Longitude": "longitude",
    },
    inplace=True,
)


def str_to_float(x):
    try:
        x = float(x)
    except:
        x = np.nan
    return x


# Drop rows where Subsidy Status != "Active" or "Inconclusive"
nhpd = nhpd.loc[((nhpd['Subsidy Status'] == "Active") |
                 (nhpd['Subsidy Status'] == "Inconclusive")), :]
# Change coordinates to float
nhpd["lat"] = nhpd["Latitude"].apply(str_to_float)
nhpd["lon"] = nhpd["Longitude"].apply(str_to_float)
# Drop rows with NaN
nhpd = nhpd.dropna(subset=["lat", "lon"])
nhpd = gpd.GeoDataFrame(nhpd, geometry=gpd.points_from_xy(nhpd.lon, nhpd.lat))
# Set CRS to EPSG:4326
nhpd = nhpd.set_crs(4326, allow_override=True)
nhpd = nhpd.to_crs(pyproj.CRS.from_epsg(4269), inplace=False)

print("Cleaned data, beginning to export")
# Export carto_nhpd to CARTO
# carto_nhpd.to_csv("carto_data/carto_nhpd.csv", index=False)
print("Done exporting Carto NHPD")

# Export nhpd to REPORT as a geojson
nhpd.to_file("report_data/nhpd.geojson", driver="GeoJSON")
print("Done exporting Report NHPD Geojson")

# Export nhpd to REPORT as a pickle file
with open("report_data/nhpd.pkl", "wb") as f:
    pickle.dump(nhpd, f)
print("Done exporting Report NHPD Pickle File")
