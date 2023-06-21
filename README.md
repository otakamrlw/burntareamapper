# Burnt Area Mapper

<div align:"center">
  <img src="https://github.com/otakamrlw/burntareamapper/blob/master/burnseverity_crop.png">
</div>
Automatic burnt area mapper using Sentinel-2 data

## Overview
The Burnt Area Mapper is a project aimed at assessing the severity of areas affected by wildfires using satellite imagery and the Normalized Burn Ratio (NBR) index. The project combines the use of Sentinel-2 pre- and post-fire satellite imagery to analyze the changes in vegetation and identify burnt areas. It uses near-infrared (NIR) and shortwave-infrared (SWIR) wavelengths. Healthy vegetation before a fire has very high NIR reflectance and a low SWIR response. In contrast, recently burnt areas have a low reflectance in the NIR and high reflectance in the SWIR band. The NBR is calculated for images before the fire (pre-fire NBR) and for images after the fire (post-fire NBR) and the post-fire image is subtracted from the pre-fire image to create the differenced (or delta) NBR (dNBR) image. The dNBR can be used for burn severity assessment, as areas with higher dNBR values indicate more severe damage whereas areas with negative dNBR values might show increased vegetation productivity. The dNBR values can be classified according to burn severity ranges proposed by the United States Geological Survey (USGS).


## Usage
To use the Burnt Area Mapper, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/otakamrlw/burntareamapper.git
   
2. Set up the environment using the provided requirements.txt file:

   ```bash
   pip3 install -r requirements.txt



3. Run the burnt_area_mapper.py script with the desired parameter:

To get data via API:
   
   ```bash
   python3 burnt_area_mapper.py api
   ```


This will ask you to provide coordinates and time range and then the script will retrieve the required data via the API.
As an example, you can use the Alpha Road Tambaroora bushfire in NSW Central West, Australia that occurred between 05.03.2023 and 19.03.2023. The coordinates and time range are (148.79697, -33.20518, 150.05036, -32.64876) and 2023-03-05/2023-03-19.  

To use data already stored in a local directory:
   
   ```bash
   python burnt_area_mapper.py local
   ```

This will use the data stored in the local directory. You can download the data manually at https://scihub.copernicus.eu/dhus/#/home or use the example data stored in this repository.


5. You will get the NBR of prefire, postfire, dNBR and a burn severity map as a plot.


------
## Methodology
The Burnt Area Mapper utilizes Sentinel-2 satellite imagery to analyze burnt areas and evaluate their severity. This is achieved through the calculation of the Normalized Burn Ratio (NBR) index, a widely accepted measure for assessing fire severity. The NBR is derived from the near-infrared (NIR) and shortwave-infrared (SWIR) wavelengths. Before a fire, healthy vegetation exhibits high NIR reflectance and low SWIR response. In contrast, recently burnt areas display low NIR reflectance and high SWIR reflectance.

The Burnt Area Mapper calculates the pre-fire NBR and post-fire NBR by analyzing images taken before and after the fire, respectively. The differenced NBR (dNBR) image is then generated by subtracting the post-fire NBR from the pre-fire NBR. The dNBR values are useful for assessing burn severity, as higher values indicate more severe damage, while negative values may indicate increased vegetation productivity.

The Burnt Area Mapper utilizes burn severity ranges proposed by the United States Geological Survey (USGS) to classify the dNBR values and provide insights into the severity of the burnt areas. For more information about the NBR and its applications, you can visit the UN-SPIDER Knowledge Portal.

## Processing steps
In order to generate the burn severity map with Sentinel-2 imagery, the Sentinel-2 bands B8A and B12 are used. Thus, the bands of both pre- and post-fire images are loaded and the NBR is calculated. The formula are shown below:

`NBR = (NIR - SWIR) / (NIR + SWIR)`

`NBR = (B8A - B12) / (B8A + B12)`

After calculating NBR for both pre and post-fire images, it is possible to determine their difference and obtain dNBR. Therefore, the difference between the NBR before and after the fire, referred to as dNBR during this practice is calculated. For that, the NBR of the post-images is subtracted from the NBR of the pre-images, as shown in the formula below:

`dNBR = pre-fire NBR – post-fire NBR`

In addition, the given coordinate of the Area of Interest is used to clip the raster dNBR to obtain an image reflecting only the study area. In order to be able to clip the data, the AOI and dNBR should be in the same projection and thus the AOI is firt reprojected.

Finally, USGS standard is used to classify the burn severity map according to the proposed number ranges, as explained here.


## Reference:
- https://github.com/UN-SPIDER/burn-severity-mapping-EO
- https://un-spider.org/advisory-support/recommended-practices/recommended-practice-burn-severity/in-detail/normalized-burn-ratio
