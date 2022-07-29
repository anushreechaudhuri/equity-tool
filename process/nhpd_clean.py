# NHPD Raw -> Change any null values for fields to "Not Available"
# NHPD Carto -> Save as a CSV to reduce storage on Carto server
# NHPD for Report -> Clean the lat lon and save as spatial file

import pandas as pd
import geopandas as gpd
import numpy as np
import sqlite3 as sql
import subprocess
import sys
import os
from os import mkdir
from os.path import exists, sep

# Enter directory paths here
WD = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data"
RAW = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/raw"
SQL_OUTPUT = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/sql_output"
CARTO = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/carto"
REPORT = "/Users/anushreechaudhuri/pCloud Drive/MIT/MIT Work/DC DOE/app_files/equity-tool/data/report"

os.chdir(RAW)
nhpd = pd.read_csv("nhpd.csv")

nhpd = nhpd[
    [
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
        "Manager Name",
        "Manager Type",
        "0-1 Bedroom Units",
        "Two Bedroom Units",
        "Three+ Bedroom Units",
        "Target Population",
        "Earliest Construction Date",
        "Latest Construction Date",
        "Rent to FMR Ratio",
        "Known Total Units",
        "Renewal Type Name",
        "Inactive Status Description",
        "Construction Type",
        "Renewal Name",
        "Renewal ID",
        "SOA Code",
        "Latitude",
        "Longitude",
    ]
]
carto_nhpd = nhpd[
    [
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
        "Manager Name",
        "Manager Type",
        "0-1 Bedroom Units",
        "Two Bedroom Units",
        "Three+ Bedroom Units",
        "Target Population",
        "Earliest Construction Date",
        "Latest Construction Date",
        "Rent to FMR Ratio",
        "Known Total Units",
        "Renewal Type Name",
        "Inactive Status Description",
        "Construction Type",
        "Renewal Name",
        "Renewal ID",
        "SOA Code",
        "Latitude",
        "Longitude",
    ]
]

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
        "Manager Name": "mgr",
        "Manager Type": "mtype",
        "0-1 Bedroom Units": "0-1",
        "Two Bedroom Units": "2-4",
        "Three+ Bedroom Units": "5-+",
        "Target Population": "pop",
        "Earliest Construction Date": "econ",
        "Latest Construction Date": "lcon",
        "Rent to FMR Ratio": "rtfmr",
        "Known Total Units": "totun",
        "Renewal Type Name": "rtype",
        "Inactive Status Description": "inact",
        "Construction Type": "ctype",
        "Renewal Name": "rname",
        "Renewal ID": "rid",
        "SOA Code": "soa",
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


nhpd["lat"] = nhpd["Latitude"].apply(str_to_float)
nhpd["lon"] = nhpd["Longitude"].apply(str_to_float)
# Drop rows with NaN
nhpd = nhpd.dropna(subset=["lat", "lon"])
nhpd = gpd.GeoDataFrame(nhpd, geometry=gpd.points_from_xy(nhpd.lon, nhpd.lat))

# Export carto_nhpd to CARTO
os.chdir(CARTO)
carto_nhpd.to_csv("carto_nhpd.csv", index=False)

# Export nhpd to REPORT as a geojson
os.chdir(REPORT)
nhpd.to_file("nhpd.geojson", driver="GeoJSON")
