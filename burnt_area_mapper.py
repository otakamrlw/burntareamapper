#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 18 12:25:17 2023

@author: Takayuki Ota
"""

from functions import crop_image, nbr, dnbr, selSquare, getFeatures
from shapely.geometry import box
import warnings
from pystac_client import Client
from fiona.crs import from_epsg
import rasterio as rio
import matplotlib.pyplot as plt
import os
import numpy as np
import geopandas as gpd
import matplotlib
import sys

warnings.filterwarnings('ignore')

print("Libraries import done")

# To load Sentinel-2 data, we have two options(API and local).
# The corrdinates of fire (Alpha Road Tambaroora)
# (min lon, min lat, max lon, max lat)
# bbox = selSquare(148.79697, -33.20518, 150.05036, -32.64876)
# dates = '2023-03-05/2023-03-19'


# Option 1. Via STAC API
def get_data_from_api():
    # Get inputs from an user
    coordinates = input(
        "Enter the coordinates: minLon, minLat, maxLon, maxLat:")
    minLon, minLat, maxLon, maxLat = map(float, coordinates.split(','))
    bbox = selSquare(minLon, minLat, maxLon, maxLat)

    dates = input(
        "Enter the time range in the format as 2020-01-01/2020-01-31:")

    api_url = 'https://earth-search.aws.element84.com/v0'
    collection = "sentinel-s2-l2a-cogs"  # Sentinel-2, Level 2A (BOA)
    s2STAC = Client.open(api_url, headers=[])

    s2Search = s2STAC.search(
        intersects=bbox,
        datetime=dates,
        query={"sentinel:data_coverage": {"gt": 80}},
        collections=collection)

    s2_items = [i.to_dict()
                for i in s2Search.get_items()]  # List of dictionaries
    print(f"{len(s2_items)} scenes acquired.")

    resdict = s2Search.get_all_items_as_dict()
    url_b8a_pre = resdict['features'][-1]['assets']['B8A']['href']
    url_b8a_post = resdict['features'][0]['assets']['B8A']['href']
    url_b12_pre = resdict['features'][-1]['assets']['B12']['href']
    url_b12_post = resdict['features'][0]['assets']['B12']['href']

    print('NIR band for pre-fire scene loading...')
    b8a_pre = rio.open(url_b8a_pre)
    print('NIR band for post-fire scene loading...')
    b8a_post = rio.open(url_b8a_post)
    print('SWIR band for pre-fire scene loading...')
    b12_pre = rio.open(url_b12_pre)
    print('SWIR band for post-fire scene loading...')
    b12_post = rio.open(url_b12_post)
    print('Done.')

    return b8a_pre, b8a_post, b12_pre, b12_post, minLon, minLat, maxLon, maxLat


# Option 2. Load local files.
def get_data_from_local():

    # Get inputs from an user
    b8a_pre = input("Enter the file path for prefire B8A band: ")
    b12_pre = input("Enter the file path for prefire B12 band: ")
    b8a_post = input("Enter the file path for postfire B8A band: ")
    b12_post = input("Enter the file path for postfire B12 band: ")

    coordinates = input(
        "Enter the coordinates: minLon, minLat, maxLon, maxLat:")
    minLon, minLat, maxLon, maxLat = map(float, coordinates.split(','))

    print('NIR band for pre-fire scene loading...')
    b8a_pre = rio.open(b8a_pre)
    print('NIR band for post-fire scene loading...')
    b8a_post = rio.open(b8a_post)
    print('SWIR band for pre-fire scene loading...')
    b12_pre = rio.open(b12_pre)
    print('SWIR band for post-fire scene loading...')
    b12_post = rio.open(b12_post)
    print('Done.')

    return b8a_pre, b8a_post, b12_pre, b12_post, minLon, minLat, maxLon, maxLat

# Convert AOI's coordinates based on the CRS of Sentinel-2 collection
# reference ：https://automating-gis-processes.github.io/CSC18/lessons/L6/clipping-raster.html

# Calculate NBR and dNBR
# NBR (Normalized Burn Ratio)
# NBR = (NIR - DWIR) / (NIR + SWIR)
# dNBR = (postfire NBR - prefire NBR)


def main():
    # Check the command-line argument
    if len(sys.argv) > 1:
        option = sys.argv[1]
        if option == 'api':
            try:
                b8a_pre, b8a_post, b12_pre, b12_post, minLon, minLat, maxLon, maxLat = get_data_from_api()
            except Exception as e:
                print("An error occurred while getting data from the API:")
                print(str(e))
                sys.exit(1)
        elif option == 'local':
            try:
                b8a_pre, b8a_post, b12_pre, b12_post, minLon, minLat, maxLon, maxLat = get_data_from_local()
            except Exception as e:
                print("An error occurred while getting data from the local directory:")
                print(str(e))
                sys.exit(1)
        else:
            print("Invalid option. Please choose 'api' or 'local'.")
            sys.exit(1)
    else:
        print("No option provided. Please choose 'api' or 'local'.")
        sys.exit(1)

    bbox_polygon = box(minLon, minLat, maxLon, maxLat)

    aoi = gpd.GeoDataFrame({'geometry': bbox_polygon},
                           index=[0], crs=from_epsg(4326))
    # Change CRS same as Sentinel-2's collection
    aoi = aoi.to_crs(crs=b8a_pre.crs)

    coords = getFeatures(aoi)

    NBR_dir = 'content/NBR'
    os.makedirs(NBR_dir, exist_ok=True)

    print("Creating NBR pre-fire, NBR post-fire and dNBR images. This might take a while...")
    nir_pre = b8a_pre.read()
    swir_pre = b12_pre.read()
    nir_post = b8a_post.read()
    swir_post = b12_post.read()

    NBR_pre = nbr(nir_pre, swir_pre)
    NBR_post = nbr(nir_post, swir_post)
    dNBR = dnbr(NBR_pre, NBR_post)

    NBR_pre_path = os.path.join(NBR_dir, 'COGsentinel-2_' + 'api_pre_NBR.tif')
    NBR_post_path = os.path.join(
        NBR_dir, 'COGsentinel-2_' + 'api_post_NBR.tif')
    dNBR_path = os.path.join(NBR_dir, 'COGsentinel-2_' + 'api_dNBR.tif')

    out_meta = b8a_pre.meta
    out_meta.update(driver='GTiff')
    out_meta.update(dtype=rio.float32)
    print("Done")

    print("Saving images ...")
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

    # Plot pre fire NBR, post fire NBR and dNBR
    print("Plotting pre-fire NBR, post-fire NBR and dNBR ...")
    NBR_pre_2d = np.squeeze(NBR_pre_crop, axis=0)
    NBR_post_2d = np.squeeze(NBR_post_crop, axis=0)
    dNBR_2d = np.squeeze(dNBR_crop, axis=0)

    fig, ax = plt.subplots(figsize=(8, 6))
    NBR_pre_plot = ax.imshow(NBR_pre_2d, cmap='RdBu_r', vmin=-1, vmax=1)
    cbar = plt.colorbar(NBR_pre_plot, ticks=[-1, -0.5, 0, 0.5, 1])
    cbar.set_label('NBR')
    ax.set_title('NBR Pre-fire')
    plt.subplots_adjust(left=0.05, right=0.9)
    plt.ion()
    plt.show()
    input("Press enter to continue to the next figure.")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 6))
    NBR_post_plot = ax.imshow(NBR_post_2d, cmap='RdBu_r', vmin=-1, vmax=1)
    cbar = plt.colorbar(NBR_post_plot, ticks=[-1, -0.5, 0, 0.5, 1])
    cbar.set_label('NBR')
    ax.set_title('NBR Post-fire')
    plt.subplots_adjust(left=0.05, right=0.9)
    plt.ion()
    plt.show()
    input("Press enter to continue to the next figure.")
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 6))
    dNBR_plot = plt.imshow(dNBR_2d, cmap='RdBu_r', vmin=-1, vmax=1)
    cbar = plt.colorbar(dNBR_plot, ticks=[-1, -0.5, 0, 0.5, 1])
    cbar.set_label('dNBR')
    ax.set_title('dNBR')
    plt.subplots_adjust(left=0.05, right=0.9)
    plt.ion()
    plt.show()
    input("Press enter to continue to the next figure.")
    plt.close()

    # Define dNBR classification bins
    cmap = matplotlib.colors.ListedColormap(
        ['green', 'yellow', 'orange', 'red', 'purple'])
    cmap.set_over('purple')
    cmap.set_under('white')
    bounds = [-0.5, 0.1, 0.27, 0.440, 0.660, 1.3]
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

    filename = 'BurnSeverityMap'
    fig, ax = plt.subplots(figsize=(8, 6))
    cax = ax.imshow(dNBR_2d, cmap=cmap, norm=norm)
    plt.title('Burn Severity Map')
    cbar = fig.colorbar(cax, ax=ax, fraction=0.035, pad=0.04,
                        ticks=[-0.2, 0.18, 0.35, 0.53, 1])
    cbar.ax.set_yticklabels(['Unburnt', 'Low Severity',
                            'Moderate-low Severity', 'Moderate-high Severity', 'High Severity'])
    plt.subplots_adjust(left=0.05, right=0.9)
    plt.ion()
    plt.show()
    input("Press enter to exit.")
    plt.savefig(filename, bbox_inches="tight")
    plt.close()
    print("Done.")


if __name__ == "__main__":
    main()
