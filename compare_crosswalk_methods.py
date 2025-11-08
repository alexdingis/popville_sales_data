# %%
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import geopandas as gpd
import io
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import requests
import time
import urllib

parent     = os.path.dirname(os.getcwd())
load_dotenv(os.path.join(parent, ".env"))
pd.options.display.float_format = '{:,.2f}'.format

"""
Data Plan
 - Load datasets
 - Produce median close price for census tracts for all sales during 2024
    * Note YEAR AND MONTH are when Popville posted the excel table
    * SELL_YEAR and SELL_MONTH are when the data was from. This has been spot checked against CLOSE_DATE.
    * CLOSE_DATE was not available in all source tables, therefore, it was not reliable to generate SELL_YEAR and SELL_MONTH.
 - Produce median close price for ZIP codes for all sales during 2024
    * Sales data is regularly reported at the ZIP code level
 - Crosswalk median close price from ZIP --> tract
 - Final dataset will have the following columns
    * TRACT
    * TRACT_MEDIAN_CLOSE_PRICE - this is the source of truth
    * Crosswalked ZIP --> Tract median close price estimates
    * 
"""

# %%
# Get dc tracts
# This is useful for mapping, not necessary for crosswalking
tracts_url = r"https://tigerweb.geo.census.gov/arcgis/rest/services/Generalized_TAB2020/Tracts_Blocks/MapServer/3/query"
def fetch_geographies(state_fips):
    dfs = []
    for st in state_fips:
        params = {
            "where": f"STATE='{st}'",
            "outFields": "*",
            "outSR": "4326",
            "f": "geojson"
        }
        url = f"{tracts_url}?{urllib.parse.urlencode(params)}"
        try:
            gdf = gpd.read_file(url)
            if not gdf.empty:
                dfs.append(gdf)
                print(f"Fetched: {st} ({len(gdf):,} tracts)")
        except Exception as e:
            print(f"Failed {st}: {e}")
    return gpd.GeoDataFrame(pd.concat(dfs, ignore_index=True))

gdf_tracts = fetch_geographies(["11"])
print(len(gdf_tracts))
print(gdf_tracts.head(5))
gdf_tracts.plot()
plt.show()

# %%
# Load crosswalk
# Assumes two locally download crosswalk files are in the same place as this file
zip_tract     = os.path.join(os.getcwd(), r"crosswalk\ZIP_TRACT_062025.xlsx")
tract_zip     = os.path.join(os.getcwd(), r"crosswalk\TRACT_ZIP_062025.xlsx")

dfzt          = pd.read_excel(zip_tract)
dfzt["ZIP"]   = dfzt["ZIP"].astype(str).apply(lambda x: (str(x).replace(".0", "").zfill(5)))
dfzt["TRACT"] = dfzt["TRACT"].astype(str).apply(lambda x: (str(x).replace(".0", "").zfill(11)))

dftz          = pd.read_excel(tract_zip)
dftz["ZIP"]   = dftz["ZIP"].astype(str).apply(lambda x: (str(x).replace(".0", "").zfill(5)))
dftz["TRACT"] = dftz["TRACT"].astype(str).apply(lambda x: (str(x).replace(".0", "").zfill(11)))

print(dftz.head(5))

# %%
final             = r"https://raw.githubusercontent.com/alexdingis/popville_sales_data/refs/heads/main/scraped_and_compiled.csv"
df                = pd.read_csv(final, low_memory= False)
df["FULL_TRACT"]  = df["FULL_TRACT"].astype(str).apply(lambda x: (str(x).replace(".0", "").zfill(11)))
df["YEAR"]        = df["YEAR"].astype(str).apply(lambda x: (str(x).replace(".0", "").zfill(4)))
df["MONTH"]       = df["MONTH"].astype(str).apply(lambda x: (str(x).replace(".0", "").zfill(2)))
df["CLOSE_PRICE"] = pd.to_numeric(df["CLOSE_PRICE"], errors="coerce").astype("float64")
df["LIST_PRICE"]  = pd.to_numeric(df["LIST_PRICE"],  errors="coerce").astype("float64")

# Set SELL_YEAR and SELL_MONTH to one month back
df["DATE"]        = pd.to_datetime(df["YEAR"] + df["MONTH"], format="%Y%m")
df["SELL_DATE"]   = df["DATE"] - pd.DateOffset(months=1)
df["SELL_YEAR"]   = df["SELL_DATE"].dt.year.astype(str)
df["SELL_MONTH"]  = df["SELL_DATE"].dt.month.astype(str).str.zfill(2)

# %%
"""
Global median
"""
df2       = df[(df["SELL_YEAR"] == "2024")]
med_list  = df2["LIST_PRICE"].median()
med_close = df2["CLOSE_PRICE"].median()
print(f"\nMedian list price: {med_list:,}\nMedian close price: ${med_close:,}\n")
desc      = df2[["CLOSE_PRICE", "LIST_PRICE"]].describe()
print(desc)
print(f"\nNumber of unique census tracts: {len(list(df2["FULL_TRACT"].unique()))}\n")

# %%
"""
Tract-level medians
"""
tract_medians         = df2.groupby(["FULL_TRACT"])[["CLOSE_PRICE"]].median().reset_index()
tract_medians.columns = ["FULL_TRACT", "TRACT_MEDIAN_CLOSE_PRICE"]
print(tract_medians.head(5))
print(tract_medians.tail(5))

# %%
"""
ZIP-level medians
"""
zip_medians         = df2.groupby(["ZIP"])[["CLOSE_PRICE"]].median().reset_index()
zip_medians.columns = ["ZIP", "ZIP_MEDIAN_CLOSE_PRICE"]

# %%
"""
Crosswalk ZIP code data to tract medians using tract-to-ZIP crosswalk file
"""
dfx = pd.merge(dftz, zip_medians, how = "left", left_on = "ZIP", right_on = "ZIP")
# print(len(dfx))
# print(dfx.head(5))

# View DC only but don't use this
dfx_dc = dfx[(dfx["ZIP"].isin(["20010", "20009"])) | (dfx["TRACT"].isin(["11001002702"]))]
print(len(dfx_dc))
print(dfx_dc[["TRACT", "ZIP", "RES_RATIO", "ZIP_MEDIAN_CLOSE_PRICE"]].head(14))

# %%
"""
Calculate weighted average by tract
"""
# Weighted average by TRACT, handle edge cases (e.g., division by 0), and other pandas-specific warnings (thanks, LLM)
weighted_avg = (
    dfx[["TRACT", "ZIP_MEDIAN_CLOSE_PRICE", "RES_RATIO"]]
    .groupby("TRACT")
    .apply(lambda x: (
        (x["ZIP_MEDIAN_CLOSE_PRICE"] * x["RES_RATIO"]).sum() /
        x["RES_RATIO"].sum() if x["RES_RATIO"].sum() > 0 else float("nan")
    ))
    .reset_index(name="WEIGHTED_CLOSE_PRICE")
)

print(weighted_avg[weighted_avg["TRACT"] == "11001002702"])

# %%
"""
Merge actual values and estimates to polygons
"""
gdf2 = gdf_tracts.merge(tract_medians, how = "left", left_on = "GEOID", right_on = "FULL_TRACT")
gdf2 = gdf2.merge(weighted_avg, how = "left", left_on = "GEOID", right_on = "TRACT")
print(len(gdf2))
print(gdf2[["GEOID", "TRACT_MEDIAN_CLOSE_PRICE", "WEIGHTED_CLOSE_PRICE"]].head(12))

# %%
dataframe = gdf2
print(f"\nRecords in dataframe: {len(dataframe):,}\n")
max_col_len = max(len(col) for col in dataframe.columns)

for idx, col in enumerate(dataframe.columns):
    dtype     = str(dataframe[col].dtype).ljust(len("datetime64[ns]"))
    colname   = col.ljust(max_col_len)
    nulls     = str(dataframe[col].isna().sum()).ljust(5)
    first_val = dataframe[col].iloc[0]
    print(f"{str(idx).zfill(3)} | {dtype} | {colname} | {nulls} | {first_val}")
# %%
"""
Checks:
    - The census tract GEOIDs are correct
    - The median price per tract looks reasonable (upper NW is very high while the rest are high)
    - There are no sales at: 
        * Georgetown University
        * Catholic University
        * National Mall + White House area
        * The census tract with RFK, city jail, Congressional Cemetary, etc.
        * Bolling AFB 
"""
a = list(gdf_tracts["GEOID"])
b = list(tract_medians["FULL_TRACT"])
count = sum(x in a for x in b)
print(count)
for elem in b:
    if elem not in a:
        print(elem)
gdf2.plot("TRACT_MEDIAN_CLOSE_PRICE",legend=True)
#,title="Median Close Price by Census Tract (2024)"
plt.show()
# %%
"""
Checks:
 - Similar patterns as the tract level but with smaller areas taken out
    * American University, Catholic University, Georgetown University
    * Bolling AFB, other military bases, other Federeal lands and institutions
"""
zip_url   = r"https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Location_WebMercator/FeatureServer/4/query?outFields=*&where=1%3D1&f=geojson"
zip_codes = gpd.read_file(zip_url)
zip_codes = zip_codes.merge(zip_medians, how = "left", left_on = "ZIP_CODE_TEXT", right_on = "ZIP")
zip_codes.plot("ZIP_MEDIAN_CLOSE_PRICE",legend=True)
print(f"Records: {len(zip_url):,}")
print(zip_codes.head())
print(zip_codes.crs)

# %%
