How to use oceanVal
=====================

Validating simulations using oceanVal involves three main steps:

    1. Register the observational datasets you want to use for validation.
    2. Matchup the model simulation output with the observational datasets.
    3. Calculate validation statistics and generate plots. 

Step 1: Register observational datasets
------------------------------------

You first need to register the observational datasets you want to use for validation. 
This involves specifying the location of the data files and any necessary metadata.
You can register both gridded and in-situ observational datasets using the `oceanval.add_point_comprison` and `oceanval.add_gridded_comparison` functions. 

**Setting up point (in-situ) observational data**

To register an in-situ observational dataset, you will need to specify the following:

- `name`: A name for the dataset, e.g. "temperature". This is so that oceanVal can keep track of things.
- `source`: The source of the observational data (e.g. "NOAA"). 
- `model_variable`: A string specifying the name of the model variable to compare against the observations. 
- `obs_dir`: The path to the directory containing the observational data files.

The following optional parameters can also be specified:
- `source_info`: Additional information about the source of the data (e.g. publication details)
- `short_name`: A short name for the observational variable (e.g. "temp" for temperature)
- `short_title`: A short title for plots (e.g. "Nitrate Concentration")
- `long_name`: A long name for the observational variable (e.g. "sea surface temperature")
- `vertical`: A boolean indicating whether vertical validation should be carried out. This defaults to False, so only surface validation will occur.
- `start`: The first year of observations to use. If not specified, all years in the data will be used. 
- `end`: The last year of observations to use. If not specified, all years in the data will be used.
- `obs_multiplier`: A multiplier to apply to the observational data (e.g. to convert units). This defaults to 1.0 (no change). 
- `binning`: Specify if you want data to be spatially binned to a specific lon/lat resolution. This is of the format [lon_bin_size, lat_bin_size] in degrees. If not specified, no binning will be applied.

An example is shown below:

.. code:: ipython3

    oceanval.add_point_comparison(
        name="nitrate",
        source = "ICES",
        source_info = "In-situ observations from the International Council for the Exploration of the Sea"
        short_name = "nitrate concentration"
        model_variable="temp",
        obs_dir="/path/to/obs_data/",
    )



**Setting up gridded observational data**

To register a gridded observational dataset, you will need to specify the following:

- `name`: A name for the dataset, e.g. "temperature". This is so that oceanVal can keep track of things.
- `source`: The source of the observational data (e.g. "CMEMS"). 
- `model_variable`: A string specifying the name of the model variable to compare against the observations.
- `obs_dir`: The path to the directory containing the observational data files.
- `obs_variable`: A string specifying the name of the variable in the observational data files.
- `climatology`: A boolean indicating whether the observational data is a climatology. 

The following optional parameters can also be specified:

- `source_info`: Additional information about the source of the data (e.g. publication details)
- `short_name`: A short name for the observational variable (e.g. "oxygen concentration")
- `long_name`: A long name for the observational variable (e.g. "dissolved oxygen concentration")
- `short_title`: A short title for plots (e.g. "Oxygen Concentration")
- `vertical`: A boolean indicating whether vertical validation should be carried out. This defaults to False, so only surface validation will occur.
- `start`: The first year of observations to use for validation.
- `end`: The last year of observations to use for validation.
- `obs_multiplier`: A multiplier to apply to the observational data (e.g. to convert units). This defaults to 1.0 (no change).

An example is shown below:

.. code:: ipython3

    oceanval.add_gridded_comparison(
        name="oxygen",
        source = "CMEMS",
        source_info = "Gridded observations from the Copernicus Marine Environment Monitoring Service"
        short_name = "oxygen concentration"
        model_variable="oxygen",
        obs_variable="O2_concentration",
        obs_dir="/path/to/obs_data/",
        climatology=False,
    )




Step 2: Matchup model output with observations
--------------------------------------
Once you have registered your observational datasets, you can matchup the model simulation output with the observations using the `oceanval.matchup` function.

You will need to specify the following:

- `sim_dir`: The path to the directory containing the model simulation output files.
- `start`: The first year of the simulation to use for validation. 
- `end`: The last year of the simulation to use for validation.
- `cores`: The number of CPU cores to use for parallel processing.
- `lon_lim`: The longitude limits for the validation region (e.g. [-180, 180]).
- `lat_lim`: The latitude limits for the validation region (e.g. [-90, 90]).

The following variable is required if you are carrying out vertical validation: 

- `thickness`: Either "z_level" or a string specifying the name of the variable in the model output files that contains the cell thickness information.

The following optional parameters can also be specified:

- `n_dirs_down`: The number of directory levels to search down for model output files. This defaults to 2, assuming files are stored in for example a YYYY/MM/ structure.
- `overwrite`: A boolean indicating whether to overwrite existing matchup files. This defaults to False.
- `ask`: A boolean indicating whether to ask for confirmation before overwriting existing matchup files. This defaults to True.
- `cache`: A boolean indicating whether to cache intermediate results. This defaults to False.
- `exclude`: A list of strings that should not appear in any simulation files paths. 
- `out_dir`: The path to the directory where matchup files should be saved. If not specified, matchup files will be saved in the execution directory.
- `point_time_res`: The time resolution for the point (in-situ) observation matchup. This defaults ["year", "month", "day"] for totally precise matchups. Set to ["month", "day"], if you want to compare climatological simulation output with observations.
- `n_check`: The number of files to check when identifying the file naming convention. oceanVal checks all files in a random subdirectory. Set n_check for a random subset in cases where all simulation files are in a single directory. 
- 

An example is shown below:

.. code:: ipython3

    oceanval.matchup(
        sim_dir="/path/to/simulation/output/",
        start=2000,
        end=2010,
        cores=4,
        lon_lim=[-80, 0],
        lat_lim=[20, 60],
        thickness="cell_thickness",
    )

Step 3: Calculate validation statistics and generate html summary
--------------------------------------

Once you have matched up the model simulation output with the observations, you can calculate validation statistics and generate plots using the `oceanval.validate` function.

You can do this as follows:

.. code:: ipython3

    oceanval.validate()
This must be run in the same directory where the matchup files were created.