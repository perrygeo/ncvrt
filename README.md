# ncvrt
Use VRTs to deal with some quirks of NetCDF and GDAL interaction

**Status**: Not ready for production, use at your own risk

The `ncvrt` script will create a GDAL [VRT](http://www.gdal.org/gdal_vrttut.html) to wrap your 
netCDF files. Instead of converting potentially huge amounts of data, this approach
simply uses the VRT as a wrapper to deal with these quirks

## `--flip` or invert latitude of "bottom up" data

Many NetCDF files are *bottum up*, i.e. the origin is in the lower left. Most raster data is 
assumed to have an origin in the upper left. As a result, GDAL will attempt to read in reverse
but it can only do so 1 line at a time! If the blocksize does not support that, you'll get errors like 

    ERROR 1: nBlockYSize = 90, only 1 supported when reading bottom-up dataset
 
So we can either rewrite the entire dataset using CDO or Numpy. But that uses a lot of disk space.

Instead we can set an environment variable to tell GDAL to read in normal order 
    
    export GDAL_NETCDF_BOTTOMUP=NO

But now our image is inverted, with south "up". Well affine transformations can help - this script simply modifies
the `GeoTransform` so that the pixelYSize is positive. Mathmatically correct, though not many software packages 
can handle it well. You've been warned. 

## `--wrap` longitudes from 0:360 to -180:180

Many global netcdf files come referenced with longitudes from 0 to 360. We need -180 to 180 to interoperate
with common coordinate reference systems like `EPSG:4326`. 

We can use the VRT to read the raster in two halfs, east and west, and effectively swap them. The `Geotransform` is adjusted accordingly.

Currently this is not very smart as it assumes 0 to 360, centered on 180 as international date line with an even number of pixels on both sides. If this is not the case, this script won't work.

## Example

```
ncvrt --flip --wrap temperature.nc > temperature.vrt
```

And then use `temperature.vrt` in any GDAL app that can support non-negative `pixelYSize` (admittedly very few, QGIS does but performance is degraded)
