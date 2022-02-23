start = '2021-11-05'
stop = '2021-11-12'
bbox = {'north': 37.7, 
        'south': 37.6, 
        'west': -119.1, 
        'east': -119}
        

MOD09
MOD09GA


https://worldview.earthdata.nasa.gov/?v=-119.67211032035331,36.95036100736455,-118.3986006159679,38.266652678381675&lg=true&t=2021-11-12-T19%3A37%3A33Z

https://ladsweb.modaps.eosdis.nasa.gov/search/order/4/MOD09--6,MOD09GA--61/2021-11-05..2021-11-12/DB/-119.1,37.7,-119,37.6


# CRS:
### QGIS
{ 'CRS' : QgsCoordinateReferenceSystem('USER:100000'), 'EXTENT' : '-11119505.196699999,-10007554.676999999,3335851.559000000,4447802.078700000 []', 'HOVERLAY' : 0, 'HSPACING' : 463.312716527778, 'OUTPUT' : 'TEMPORARY_OUTPUT', 'TYPE' : 2, 'VOVERLAY' : 0, 'VSPACING' : 463.312716527778 }

### WKT
PROJCS["Sinusoidal",
    GEOGCS["GCS_Undefined",
        DATUM["Undefined",
            SPHEROID["User_Defined_Spheroid",6371007.181,0.0]],
        PRIMEM["Greenwich",0.0],
        UNIT["Degree",0.0174532925199433]],
    PROJECTION["Sinusoidal"],
    PARAMETER["False_Easting",0.0],
    PARAMETER["False_Northing",0.0],
    PARAMETER["Central_Meridian",0.0],
    UNIT["Meter",1.0]]



Note that the inverse flattening is 0! I.e. we are on a sphere!

https://www.ibm.com/docs/en/db2-for-zos/11?topic=systems-coordinate-syntax
    

## GDAL
### GDAL can read EOS SWATH granules. 

```bash
gdal_translate "MOD09GA.A2021309.h08v05.061.2021311034604.hdf":"MODIS_Grid_500m_2D":"sur_refl_b01_1" a.tif
```+

"HDF4_EOS:EOS_SWATH:"MOD09.A2021309.1825.006.2021311021513.hdf":""MODIS SWATH TYPE L2"":""500m Surface Reflectance Band 1"""

### GDAL can read EOS GRID

"HDF4_EOS:EOS_GRID:"MOD09GA.A2021309.h08v05.061.2021311034604.hdf":MODIS_Grid_500m_2D:sur_refl_b01_1"


## MErging data
```bash
gdal_merge.py -separate -ot int16 -of GTiff -o rgb.tif --optfile optfile.txt
```
