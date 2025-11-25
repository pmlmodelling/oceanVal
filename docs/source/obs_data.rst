Compatible observational data
============

oceanVal is designed to validate two types of observational data: gridded observations and in-situ observations.

This data will need to be in specific formats. However, it should be easy to convert your data into these formats.


Gridded observational data
---------------------------

If you want to validate your model against gridded observational data (e.g. satellite data), then the data should be in a NetCDF format.

Observations can either be contained in a single NetCDF file or multiple files.

oceanVal requires files to be CF-compliant. However, gridded observational products almost always are, so there should be no compatiability issues.

In-situ observational data
-----------------------

If you want to validate your model against in-situ observational data (e.g. from research cruises or moorings), then the data should be in CSV format.

The CSV file can contain the following columns, with required columns in bold:

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
