# Burnt Area Mapper

<div align:"center">
  <img src="https://github.com/otakamrlw/burntareamapper/blob/master/burnseverity_crop.png">
</div>
Automatic burnt area mapper using Sentinel-2 data

## Table of contents
[Overview](#overview) 
[Usage](#usage)
[Methodoogy](#methodology)  
[Approach with Python](#approach-with-python)  
[Processing steps](#processing-steps)

## Overview

## Usage

------
## Methodology
The aim of this step-by-step procedure is the generation of a burn severity map for the assessment of the areas affected by wildfires. The Normalized Burn Ratio (NBR) is used, as it was designed to highlight burned areas and estimate burn severity. It uses near-infrared (NIR) and shortwave-infrared (SWIR) wavelengths. Healthy vegetation before a fire has very high NIR reflectance and a low SWIR response. In contrast, recently burned areas have a low reflectance in the NIR and high reflectance in the SWIR band. More information about the NBR can be found on the [UN-SPIDER Knowledge Portal](https://un-spider.org/advisory-support/recommended-practices/recommended-practice-burn-severity/in-detail/normalized-burn-ratio). 
The NBR is calculated for images before the fire (pre-fire NBR) and for images after the fire (post-fire NBR) and the post-fire image is subtracted from the pre-fire image to create the differenced (or delta) NBR (dNBR) image. The dNBR can be used for burn severity assessment, as areas with higher dNBR values indicate more severe damage whereas areas with negative dNBR values might show increased vegetation productivity. The dNBR values can be classified according to burn severity ranges proposed by the United States Geological Survey (USGS).  
## Data and software required

## Processing steps
In order to generate the burn severity map with Sentinel-2 imagery, the Sentinel-2 bands B8A and B12 are used. Thus, in the Python code (after the function definitions) the bands of both pre- and post-fire images are loaded and the NBR is calculated. As it is already mentioned NBR is calculated using the NIR and SWIR bands of Sentinel-2 in this practice, using the formula shown below:

`NBR = (NIR - SWIR) / (NIR + SWIR)`

`NBR = (B8A - B12) / (B8A + B12)`

After calculating NBR for both pre and post-fire images, it is possible to determine their difference and obtain dNBR. Therefore, the difference between the NBR before and after the fire, referred to as dNBR during this practice is calculated. For that, the NBR of the post-images is subtracted from the NBR of the pre-images, as shown in the formula below:

`dNBR = pre-fire NBR – post-fire NBR`

In addition, the shapefile of the correspondent area is used to clip the raster dNBR to obtain an image reflecting only the study area. As during this recommended practice, we are using the area of Empedrado region in Chile, the administrative boundary of the aforementioned area is used. In order to be able to clip the data, the shapefile and dNBR should be in the same projection and thus the shapefile is firt reprojected.

Then, USGS standard is used to classify the burn severity map according to the proposed number ranges, as explained here.

Finally, in order to quantify the area in each burn severity class, the statistics of the raster must be calculated. A transformation of the raster, so that all pixels are assigned one value for each burn severity class is necessary before the calculation.
