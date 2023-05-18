#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 17 12:25:17 2023

@author: Takayuki Ota
"""

from functions import crop_image, nbr, dnbr, selSquare, getFeatures
from shapely.geometry import box
import warnings
from pystac_client import Client
from fiona.crs import from_epsg
import rasterio.mask
import rasterio as rio
import matplotlib.pyplot as plt
import os
import numpy as np
import geopandas as gpd
import matplotlib
import sys
matplotlib.rcParams['figure.dpi'] = 300

warnings.filterwarnings('ignore')

print("Libraries import done")


# ----- step 1. Load Sentinel-2 data
# Option 1. Via STAC API

# the corrdinates of fire (Alpha Road Tambaroora)
# (min lon, min lat, max lon, max lat)
# bbox = selSquare(148.79697, -33.20518, 150.05036, -32.64876)
# dates = '2023-03-05/2023-03-19'

def get_data_from_api():
    # Get inputs from an user
    coordinates = input("Enter the coordinates: minLon, minLat, maxLon, maxLat:")
    minLon, minLat, maxLon, maxLat = map(float, coordinates.split(','))
    bbox = selSquare(minLon, minLat, maxLon, maxLat)
    
    dates = input("Enter the time range in the format as 2020-01-01/2020-01-31:")
    
    api_url = 'https://earth-search.aws.element84.com/v0'
    collection = "sentinel-s2-l2a-cogs"  # Sentinel-2, Level 2A (BOA)
    s2STAC = Client.open(api_url, headers=[])
    
    s2Search = s2STAC.search(
        intersects=bbox,
        datetime=dates,
        query={"sentinel:data_coverage": {"gt": 80}},
        collections=collection)
    
    s2_items = [i.to_dict() for i in s2Search.get_items()]  # List of dictionaries
    print(f"{len(s2_items)} scenes acquired.")
    
    resdict = s2Search.get_all_items_as_dict()
    url_b8a_pre = resdict['features'][-1]['assets']['B8A']['href']
    url_b8a_post = resdict['features'][0]['assets']['B8A']['href']
    url_b12_pre = resdict['features'][-1]['assets']['B12']['href']
    url_b12_post = resdict['features'][0]['assets']['B12']['href']
    
    print('NIR band for prefire scene loading...')
    b8a_pre = rasterio.open(url_b8a_pre)
    print('NIR band for postfire scene loading...')
    b8a_post = rasterio.open(url_b8a_post)
    print('SWIR band for prefire scene loading...')
    b12_pre = rasterio.open(url_b12_pre)
    print('SWIR band for postfire scene loading...')
    b12_post = rasterio.open(url_b12_post)
    print('Done.')
    
    return b8a_pre, b8a_post, b12_pre, b12_post, minLon, minLat, maxLon, maxLat


# Option 2. Load local files.
# b8a_pre = rio.open(
#     r'S2A_MSIL1C_20230305T000221_N0509_R030_T56HKJ_20230305T010015.SAFE/GRANULE/L1C_T56HKJ_A040210_20230305T000218/IMG_DATA/T56HKJ_20230305T000221_B8A.jp2')
# b12_pre = rio.open(
#     r'S2A_MSIL1C_20230305T000221_N0509_R030_T56HKJ_20230305T010015.SAFE/GRANULE/L1C_T56HKJ_A040210_20230305T000218/IMG_DATA/T56HKJ_20230305T000221_B12.jp2')

# b8a_post = rio.open(
#     r'S2A_MSIL1C_20230318T001111_N0509_R073_T55HFD_20230318T011314.SAFE /GRANULE/L1C_T55HFD_A040396_20230318T001107/IMG_DATA/T55HFD_20230318T001111_B8A.jp2')
# b12_post = rio.open(
#     r'S2A_MSIL1C_20230318T001111_N0509_R073_T55HFD_20230318T011314.SAFE /GRANULE/L1C_T55HFD_A040396_20230318T001107/IMG_DATA/T55HFD_20230318T001111_B12.jp2')

def get_data_from_local():
    
    # Get inputs from an user
    b8a_pre = input("Enter the file path for prefire B8A band: ")
    b12_pre = input("Enter the file path for prefire B12 band: ")
    b8a_post = input("Enter the file path for postfire B8A band: ")
    b12_post = input("Enter the file path for postfire B12 band: ")
    
    coordinates = input("Enter the coordinates: minLon, minLat, maxLon, maxLat:")
    minLon, minLat, maxLon, maxLat = map(float, coordinates.split(','))
    
    print('NIR band for prefire scene loading...')
    b8a_pre = rasterio.open(b8a_pre)
    print('NIR band for postfire scene loading...')
    b8a_post = rasterio.open(b8a_post)
    print('SWIR band for prefire scene loading...')
    b12_pre = rasterio.open(b12_pre)
    print('SWIR band for postfire scene loading...')
    b12_post = rasterio.open(b12_post)
    print('Done.')
    
    return b8a_pre, b8a_post, b12_pre, b12_post, minLon, minLat, maxLon, maxLat


# Check the command-line argument
if len(sys.argv) > 1:
    option = sys.argv[1]
    if option == 'api':
        b8a_pre, b8a_post, b12_pre, b12_post, minLon, minLat, maxLon, maxLat = get_data_from_api()
    elif option == 'local':
        b8a_pre, b8a_post, b12_pre, b12_post, minLon, minLat, maxLon, maxLat = get_data_from_local()
    else:
        print("Invalid option. Please choose 'api' or 'local'.")
else:
    print("No option provided. Please choose 'api' or 'local'.")
    

# ----- Step 2. Convert AOI's coordinates based on the CRS of Sentinel-2 collection
bbox_polygon = box(minLon, minLat, maxLon, maxLat)

aoi = gpd.GeoDataFrame({'geometry': bbox_polygon}, index=[0], crs=from_epsg(4326))
aoi = aoi.to_crs(crs=b8a_pre.crs)  # Change CRS same as Sentinel-2's collection

coords = getFeatures(aoi)
# print(coords)
# reference ：https://automating-gis-processes.github.io/CSC18/lessons/L6/clipping-raster.html

# ------ Step 3. Calculate NBR and dNBR
# NBR (Normalized Burn Ratio)
# NBR = (NIR - DWIR) / (NIR + SWIR)
# dNBR = (postfire NBR - prefire NBR)

NBR_dir = 'content/NBR'
os.makedirs(NBR_dir, exist_ok=True)

nir_pre = b8a_pre.read()
swir_pre = b12_pre.read()
nir_post = b8a_post.read()
swir_post = b12_post.read()

NBR_pre = nbr(nir_pre, swir_pre)
NBR_post = nbr(nir_post, swir_post)
dNBR = dnbr(NBR_pre, NBR_post)

NBR_pre_path = os.path.join(NBR_dir, 'COGsentinel-2_' + 'api_pre_NBR.tif')
NBR_post_path = os.path.join(NBR_dir, 'COGsentinel-2_' + 'api_post_NBR.tif')
dNBR_path = os.path.join(NBR_dir, 'COGsentinel-2_' + 'api_dNBR.tif')

out_meta = b8a_pre.meta
out_meta.update(driver='GTiff')
out_meta.update(dtype=rio.float32)

print("Creating a NBR image ...")
# Save pre, post NBR and dNBR as tif file
with rio.open(NBR_pre_path, "w", **out_meta) as dest:
    dest.write(NBR_pre)

with rio.open(NBR_post_path, "w", **out_meta) as dest:
    dest.write(NBR_post)

with rio.open(dNBR_path, "w", **out_meta) as dest:
    dest.write(dNBR)
print("Done.")

# Crop the AOI
print("Cropping the AOI ...")
NBR_pre_crop = crop_image(NBR_pre_path, NBR_pre_path, coords)
NBR_post_crop = crop_image(NBR_post_path, NBR_post_path, coords)
dNBR_crop = crop_image(dNBR_path, dNBR_path, coords)
print("Done.")

# ------- Step 4. Plot results
# Plot pre fire NBR, post fire NBR and dNBR
print("Plotting prefire NBR, postfire NBR and dNBR ...")
NBR_pre_2d = np.squeeze(NBR_pre_crop, axis=0)
NBR_post_2d = np.squeeze(NBR_post_crop, axis=0)
dNBR_2d = np.squeeze(dNBR_crop, axis=0)

NBR_pre_plot = plt.imshow(NBR_pre_2d, cmap='RdBu_r', vmin=-1, vmax=1)
cbar = plt.colorbar(NBR_pre_plot, ticks=[-1, -0.5, 0, 0.5, 1])
cbar.set_label('NBR')
plt.title('NBR Pre fire')
plt.show()

NBR_post_plot = plt.imshow(NBR_post_2d, cmap='RdBu_r', vmin=-1, vmax=1)
cbar = plt.colorbar(NBR_post_plot, ticks=[-1, -0.5, 0, 0.5, 1])
cbar.set_label('NBR')
plt.title('NBR Post fire')
plt.show()

dNBR_plot = plt.imshow(dNBR_2d, cmap='RdBu_r', vmin=-1, vmax=1)
cbar = plt.colorbar(dNBR_plot, ticks=[-1, -0.5, 0, 0.5, 1])
cbar.set_label('dNBR')
plt.title('dNBR')
plt.show()

# Define dNBR classification bins
cmap = matplotlib.colors.ListedColormap(
    ['green', 'yellow', 'orange', 'red', 'purple'])
cmap.set_over('purple')
cmap.set_under('white')
bounds = [-0.5, 0.1, 0.27, 0.440, 0.660, 1.3]
norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={
                       'xticks': [], 'yticks': []})
cax = ax.imshow(dNBR_2d, cmap=cmap, norm=norm)
plt.title('Burn Severity Map')
cbar = fig.colorbar(cax, ax=ax, fraction=0.035, pad=0.04,
                    ticks=[-0.2, 0.18, 0.35, 0.53, 1])
cbar.ax.set_yticklabels(['Unburned', 'Low Severity',
                        'Moderate-low Severity', 'Moderate-high Severity', 'High Severity'])
plt.show()
# plt.savefig(fname, bbox_inches="tight")
print("Done.")