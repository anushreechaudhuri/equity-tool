# * DACs -> Join DAC Percentiles with Mapping Display Data. Make sure data types are correct (floats, not strings). Join QCT Data.
# Carto_DACs -> short column names
# Report_DACs -> full column names
# Tribes and Territories -> Get from GIS SQLite. Naming format should be same as Counties and States.

import pandas as pd
import geopandas as gpd
import numpy as np
import sqlite3 as sql
import subprocess
import sys
import os
from os import mkdir
from os.path import exists, sep

qct = pd.read_csv("raw/qct.csv", dtype=str)

qct = qct[["qct_id"]]
# Rename 'fips' to 'GEOID' for qct
qct.rename(columns={"qct_id": "GEOID"}, inplace=True)

# If qct GEOID has 11 characters, add a '0' to the front
qct["GEOID"] = qct["GEOID"].str.pad(12, side="left", fillchar="0")
# Remove the last character from the GEOID
qct["GEOID"] = qct["GEOID"].str[:-1]

# Load DAC files
dac_pct = pd.read_csv("sql_output/dac_pct.csv", dtype=str)
dac_shp = gpd.read_file("sql_output/MappingDisplay_Data.geojson")
tt_shp = gpd.read_file(
    "sql_output/MappingDisplay_TribesAndTerritories.geojson")

dac_shp = dac_shp[[
    "GEOID", "city", "county_name", "population", "DAC_indicator", "geometry"
]]

# Merge dac_pct and dac_shp on 'GEOID'
# Remove "Unnamed: 0" column from dac_
dac_pct.drop(columns=["Unnamed: 0"], inplace=True)
dac = dac_shp.merge(dac_pct, on="GEOID")

# If 'DAC_indicator' is '1', then set 'DAC_status' to 'Disadvantaged'
# If 'DAC_indicator' is '0', then set 'DAC_status' to 'Not Disadvantaged'
dac["DAC_status"] = dac["DAC_indicator"].apply(
    lambda x: "Disadvantaged" if x == 1 else "Not Disadvantaged")

# If QCT "GEOID" in dac "GEOID", add a column "QCT_status" to dac with value = "Eligible" otherwise "Not Eligible"
dac["QCT_status"] = dac["GEOID"].apply(
    lambda x: "Eligible" if x in qct["GEOID"].values else "Not Eligible")

dac = dac[[
    "GEOID",
    "city",
    "county_name",
    "population",
    "DAC_indicator",
    "DAC_status",
    "QCT_status",
    "linguistic_isolation_pct_natl_pctile",
    "over64_pct_natl_pctile",
    "lead_paint_pct_natl_pctile",
    "ej_index_diesel_natl_pctile",
    "ej_index_cancer_natl_pctile",
    "ej_index_traffic_natl_pctile",
    "ej_index_water_natl_pctile",
    "ej_index_npl_natl_pctile",
    "ej_index_remediation_natl_pctile",
    "ej_index_tsdf_natl_pctile",
    "ej_index_pm25_natl_pctile",
    "over_30min_commute_pct_natl_pctile",
    "no_car_pct_natl_pctile",
    "avg_energy_burden_natl_pctile",
    "fossil_emp_rank_natl_pctile",
    "coal_emp_rank_natl_pctile",
    "grid_outages_county_natl_pctile",
    "grid_outage_duration_natl_pctile",
    "food_desert_pct_natl_pctile",
    "job_access_natl_pctile",
    "avg_housing_burden_natl_pctile",
    "renters_pct_natl_pctile",
    "avg_transport_burden_natl_pctile",
    "no_internet_pct_natl_pctile",
    "green_space_natl_pctile",
    "unhoused_pct_natl_pctile",
    "uninsured_pct_natl_pctile",
    "unemployed_pct_natl_pctile",
    "disability_pct_natl_pctile",
    "incomplete_plumbing_pct_natl_pctile",
    "single_parent_pct_natl_pctile",
    "mobile_home_pct_natl_pctile",
    "nonwhite_pct_natl_pctile",
    "nongrid_heat_pct_natl_pctile",
    "lessHS_pct_natl_pctile",
    "lowincome_fpl_pct_natl_pctile",
    "population_natl_pctile",
    "lowincome_ami_pct_natl_pctile",
    "fema_loss_of_life_natl_pctile",
    "tract_input_percentile_sum",
    "tract_national_percentile",
    "tract_state_percentile",
    "geometry",
]]

non_floats = [
    "GEOID",
    "city",
    "county_name",
    "DAC_indicator",
    "DAC_status",
    "QCT_status",
    "geometry",
]
for column in dac.columns:
    if column not in non_floats:
        dac[column] = dac[column].astype(float)
        if column.endswith("_natl_pctile") or column.endswith("_percentile"):
            # Convert to percentiles and round to 2 decimal places
            dac[column] = dac[column].apply(lambda x: round(x * 100, 2))
        if column.endswith("_sum"):
            # Round to 2 decimal places
            dac[column] = dac[column].apply(lambda x: round(x, 2))

carto_dac = dac[[
    "GEOID",
    "city",
    "county_name",
    "population",
    "DAC_status",
    "QCT_status",
    "avg_energy_burden_natl_pctile",
    "avg_housing_burden_natl_pctile",
    "incomplete_plumbing_pct_natl_pctile",
    "nonwhite_pct_natl_pctile",
    "nongrid_heat_pct_natl_pctile",
    "tract_input_percentile_sum",
    "tract_national_percentile",
    "tract_state_percentile",
    "geometry",
]]

# Rename columns
carto_names = {
    "county_name": "county",
    "population": "pop",
    "DAC_status": "dac",
    "QCT_status": "qct",
    "avg_energy_burden_natl_pctile": "eb_pct",
    "avg_housing_burden_natl_pctile": "hb_pct",
    "incomplete_plumbing_pct_natl_pctile": "plumb",
    "nonwhite_pct_natl_pctile": "race",
    "nongrid_heat_pct_natl_pctile": "heat",
    "tract_input_percentile_sum": "score",
    "tract_national_percentile": "nat_pct",
    "tract_state_percentile": "st_pct",
}
for key in carto_names.keys():
    carto_dac[carto_names[key]] = carto_dac[key]
    carto_dac.drop(key, axis=1, inplace=True)

# Export to geojson file in REPORT
dac.to_file("report_data/dac.geojson", driver="GeoJSON")
# Export to pickle file in REPORT
dac.to_pickle("report_data/dac.pkl")
# Export to geojson file in CARTO
dac.to_file("carto_data/carto_dac.shp", driver="ESRI Shapefile")
print("DAC data exported to geojson and pickle files.")

tt_shp["NAME"] = tt_shp["namelsad"]
tt_shp["GEOID"] = tt_shp["geoid"]
tt_shp = tt_shp[["GEOID", "NAME", "geometry"]]

# Export tt_shp to geojson file in report and carto
tt_shp.to_file("report_data/tt_shp.geojson", driver="GeoJSON")
tt_shp.to_file("carto_data/tt_shp.geojson", driver="GeoJSON")
# Export to pickle file in REPORT
tt_shp.to_pickle("report_data/tt_shp.pkl")
print("Tribes and territories data exported to geojson and pickle files.")
