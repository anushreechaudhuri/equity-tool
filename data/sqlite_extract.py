# You must have GDAL installed to use this script
# Only need to run once to create the geojson and csv files

import pandas as pd
import geopandas as gpd
import sqlite3 as sql
import subprocess
import sys
import os
from os import mkdir
from os.path import exists, sep


# Runs a command on the shell and pipes its output to STDOUT
def run_command(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    for c in iter(lambda: process.stdout.read(1), b""):
        sys.stdout.write(c)


views = ["MappingDisplay_Data", "MappingDisplay_TribesAndTerritories"]

SQLDATA = "raw/gis_data.sqlite"
for view in views:
    if exists(f"{view}.geojson"):
        print(
            f"Skipping exporting view {view} from database (geojson already exists)."
        )
        continue
    print(
        f"Exporting view {view} from database to GeoJSON (this will take a bit)..."
    )
    # Export the results of the view to geojson so we can pass it to tippecanoe
    run_command(
        f'ogr2ogr -f GeoJson -sql "SELECT * from {view}" sql_output/{view}.geojson {SQLDATA}'
    )

con = sql.connect(SQLDATA)
dac_pct = pd.read_sql_query("SELECT * from DAC_percentiles_data", con)
con.close()
# Save dac_pct to csv in SQL_OUTPUT
dac_pct.to_csv(f"sql_output/dac_pct.csv")
