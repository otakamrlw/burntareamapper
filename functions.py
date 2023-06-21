#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 15 17:49:31 2023

@author: takayuki
"""


import warnings
import rasterio.mask
import rasterio as rio
import json

warnings.filterwarnings('ignore')


def selSquare(minLon: float, minLat: float, maxLon: float, maxLat: float):
    """
    Get a bounding box based on four coordinates.

    Parameters
    ----------
    minLon : float
    minLat : float
    maxLon : float
    maxLat : float

    Returns
    -------
    geometry : TYPE
        A bounding box based on the provided coordinates.

    """
    c1 = [maxLon, maxLat]
    c2 = [maxLon, minLat]
    c3 = [minLon, minLat]
    c4 = [minLon, maxLat]
    geometry = {"type": "Polygon", "coordinates": [[c1, c2, c3, c4, c1]]}
    return geometry


def getFeatures(gdf):
    """
    Take a feature from geodataframe and convert into list so that rasterio can read.

    Parameters
    ----------
    gdf : TYPE
        GeoDataFrame.

    Returns
    -------
    list
        The list that contains the features of satellites.

    """
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


def crop_image(src_path: str, dest_path: str, coords):
    """
    Crop the satellite image based on the AOI and save the cropped image.

    Parameters
    ----------
    src_path : str
        Path of the image that is cropped.
    dest_path : str
        Path of the cropped image.
    coords : TYPE
        Coordinates of the AOI that defin the cropping area.

    Returns
    -------
    out_image : TYPE
        Cropped image.

    """
    # Open the source image
    with rio.open(src_path) as src:
        print(src.crs)

        # Perform the image cropping
        out_image, out_transform = rio.mask.mask(src, coords, crop=True)

        # Update the metadata
        out_meta = src.meta
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        # Write the cropped image
        with rio.open(dest_path, "w", **out_meta) as dest:
            dest.write(out_image)
    return out_image


# reference: https://github.com/UN-SPIDER/burn-severity-mapping-EO/blob/master/burn_severity1.py
def nbr(band1, band2):
    """
    This function takes an input the arrays of the bands from the read_band_image
    function and returns the Normalized Burn ratio (NBR)

    input:  band1   array (n x m)      array of first band image e.g B8A
            band2   array (n x m)      array of second band image e.g. B12
    output: nbr     array (n x m)      normalized burn ratio
    """
    nbr = (band1 - band2) / (band1 + band2)
    return nbr


def dnbr(nbr1, nbr2):
    """
    This function takes as input the pre- and post-fire NBR and returns the dNBR

    input:  nbr1     array (n x m)       pre-fire NBR
            nbr2     array (n x m)       post-fire NBR
    output: dnbr     array (n x m)       dNBR
    """
    dnbr = nbr1 - nbr2
    return dnbr
