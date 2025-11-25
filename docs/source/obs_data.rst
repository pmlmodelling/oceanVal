Compatible data
============

oceanVal is designed to validate ocean model simulations using two types of observational data: gridded observations and in-situ observations.

This data will need to be in specific formats. However, it should be easy to convert your data into these formats.

Simulation output
---------------------------

oceanVal is designed to validate ocean model output that is in NetCDF format.

Files should be CF-compliant as far as possible. Most ocean model output files are CF-compliant, so there should be no compatibility issues.


**Unstructured grids**: oceanVal will not be compatible out-of-the box with unstructured grid model output. However, if the unstructured grid data can be regridded onto a regular grid and saved as a CF-compliant NetCDF file, then oceanVal will be able to use it.    

**Vertical grids**: oceanVal can handle both z-level and files where the vertical grid varies, but where the cell thickness is stored in the simulation output. 

**Folder structure**: oceanVal requires that simulation files are stored in a folder with a consistent and logically file naming convention.
For example, files could be named YYYY/MM/model_output_YYYYMMDD.nc. oceanVal will automatically identify the naming convention of files and match up to the appropriate files. 

**Time requirements**: oceanVal requires at least a single year of model output.







Gridded observational data
---------------------------

If you want to validate your model against gridded observational data (e.g. satellite data), then the data should be in a NetCDF format.

Observations can either be contained in a single NetCDF file or multiple files.

oceanVal requires files to be CF-compliant. However, gridded observational products almost always are, so there should be no compatiability issues.

Vertically-resolved files can be supplied. These should be files with depth as a dimension, and the vertical grid should be consistent, which will almost always be the case with gridded data products.

In-situ observational data
-----------------------

If you want to validate your model against in-situ observational data (e.g. from research cruises or moorings), then the data should be in CSV format.

The CSV file can contain the following columns, with required columns (lon/lat/observation) in bold:

- **lon**: Longitude of the observation (decimal degrees)
- **lat**: Latitude of the observation (decimal degrees)
- depth: Depth of the observation (metres)
- year: Year of the observation
- month: Month of the observation (1-12)
- day: Day of the observation (1-31)
- **observation**: Value of the observation (units should match those of the model output)

The depth variable is required if you are validating against subsurface model data.

If you are validating against surface model data only, then the depth variable is optional. If is supplied, only the top 5m will be used for surface validation. 

oceanVal will check if you have supplied the required columns and will raise an error if any are missing.
