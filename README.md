[![Documentation Status](https://readthedocs.org/projects/oceanval/badge/?version=latest)](https://oceanval.readthedocs.io/en/latest/?badge=latest)

# oceanVal 
Marine ecosystem model validation made easy in Python

oceanVal is a fully automated marine ecosystem model tool that reduces ecosystem model validation to a simple to follow step-by-step producedure. It is designed to validate ecosystem models stored in NetCDF format against a range of in-situ and gridded observations. Currently, it uses curated data sets for validations of models on the northwest European shelf. 

# oeanVal functions

The core functionality of oceanVal is to match up model output with observational data, and then validate the model output against the observations. The following functions are available:
- `matchup`: Matches model output with observational data for validation.
- `validate`: Generates validation reports based on matched data.
- `compare`: Compares multiple model simulations against each other and against observations. This requires `matchup` and `validate` to have been run first on each simulation. This may not be backward compatible with older versions of ecoval, so ensure you have run `matchup` and `validate` using the latest version of ecoval before using `compare`.



First, clone this directory:

```sh
git clone https://github.com/pmlmodelling/oceanval.git
```

Then move to this directory.

```sh
cd oceanval
```


Second, set up a conda environment. If you want the envionment to called something other than `oceanval`, you can change the name in the oceanval.yml file. 

```sh
conda env create -f oceanval.yml
```



Activate this environment.

```sh
conda activate oceanval
```

Now, sometimes R package installs go wrong in conda. Run the following command to ensure Rcpp is installed correctly.

```sh
Rscript -e "install.packages('Rcpp', repos = 'https://cloud.r-project.org/')"
```

Now, install the package.

```sh
pip install .

```sh
conda activate oceanval
```


Now, install the package.

```sh
pip install .

```
Alternatively, install the conda environment and package using the following commands:

```sh
    conda env create --name oceanval -f https://raw.githubusercontent.com/pmlmodelling/oceanval/main/oceanval.yml
    conda activate oceanval​
    pip install git+https://github.com/pmlmodelling/oceanval.git​
```



You can now build the docs in two steps. First, matchup the data in Python. You can specify a start and end years for the comparisons. In this only the years from 2000-2005 are validated. This process might take a couple of hours to run, depending on the size of the simulation. Increase the number of cores to get faster matchups. To ensure you are ignoring cells close to the boundary you will have to specify the longitude and latitude limits. This is done using the `lon_lim` and `lat_lim` arguments. 



```sh
import oceanval
oceanval.matchup(sim_dir = "/foo/bar", cores = 6, start = 2000, end = 2005, lon_lim = [-18, 9], lat_lim = [42, 62])

```
This will put all relevant matchup data into a folder called matched. Note: this could take a couple of hours if you have a large simulation. Note: you will have to specify whether the surface is the top or bottom level in the file structure. This is almost always the top level.

Ideally, the data directory specified will only have model simulation output in it, and it should have a consistent structure. The matchup function will infer the folder structure and read in all the relevant data. But if things are inconsistent, or you have stray files, things could go wrong.

Once this is done you can build the docs. This should take 10-15 minutes.


```sh
import oceanval
oceanval.validate()
```


## Minimal simulation requirements

Simulations should have at least one year of complete data. Simulation output can be split across multiple files and directories. All that oceanval requires is that the directories are logiccally structured. For example, files could be of the format YYYY/MM/sim_output_YYYYMMDD.nc.

Matchups for gridded data will require the model to have at least monthly resolution; if it is daily gridded model output will be averaged in each month to matchup with gridded observations. 

Point observation matchups will do a strict day/month/year matchup. If you have monthly output only, any point matchups will be relatively ineffective.


## Modifying jupyter notebooks produced

If you want to tweak the analysis produced by oceanval, you can do so by changing the notebooks oceanval uses to produce the validation summary.

Internally, oceanval will create a number of notebook, run them and then generate an html file. If you would like to work with one of the notebooks, you can open them in the book/notebooks directory. So long as you are using the conda environment created using the commands above, you should able to run the notebooks problem free. 

Once you have modified notebooks, you can then rebuild the validation docs. Do this by running the following commands from the same directory as `validate` was run before::



```sh
import oceanval
oceanval.rebuild()
```


# Matchup Function Arguments Summary

## Overview
The `matchup` function is used to match up model output with observational data for validation purposes. This document provides a comprehensive summary of all available arguments.

## Required Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `sim_dir` | `str` | **Required.** Folder containing model outputNeeded to ensure you are ignoring cells near the boundary. Subdirs probably look like this: **/**/*.nc  |
| `start` | `int` | **Required.** Start year - first year of simulations to matchup. Ensure this is after spinup. |
| `end` | `int` | **Required.** End year - final year of simulations to matchup |
| `lon_lim` | `list` | **Required.** Needed to ensure you are ignoring cells near the boundary. List of two floats [lon_min, lon_max]. Sensible values for AMM7: `[-18, 9]` |
| `lat_lim` | `list` | **Required.** List of two floats [lat_min, lat_max]. Sensible values for AMM7: `[42, 63]` |


## Processing Configuration

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `cores` | `int` | `6` | Number of cores for parallel processing. Set to a high value to speed things up. Auto-adjusts to system cores if less than 6 available |
| `overwrite` | `bool` | `True` | Whether to overwrite existing output files. Set to False if you have already matched up some of the data |
| `ask` | `bool` | `True` | Whether to ask user for confirmation during processing. Set to False if you are running using slurm |

## File and Directory Configuration

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `thickness` | `str` | `None` | Path to thickness file or variable name. This is **required** for bottom matchups. Use "z_level" for z-level models |
| `exclude` | `list` | `[]` | List of strings to exclude from file matching. Use in case you have random files that could confuse oceanval's file identifier |

## Data Processing Options

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `n_dirs_down` | `int` | `2` | Directory levels to search for netCDF files (format: `*/*/*.nc`) If all files are in the sim_dir, set to 0 |
| `point_time_res` | `list`  | `["year", "month", "day"]` | Time resolution for point data matchup. For example, if you only have 1 year of simulation output, you might want to set this to `["month", "day"]` so that it picks up observational data for all years to compare with the 1 year of simulation output. Note: if you do not include year, all simulated years (between start and end) will be included. |



# Validate Function Arguments Summary

## Overview
The `validate` function is the core function in oceanval that generates automated validation reports for marine ecosystem models. It processes matched model and observational data to create comprehensive validation documentation in either HTML or PDF format.

## Function Signature
```python
def validate(
    title="Automated model evaluation",
    concise=True,
    author=None,
    variables="all",
    ask=False,
    r_warnings=False,
    model=None,
    test=False,
    lon_lim=None,
    lat_lim=None,
)
```

## Arguments

### Report Configuration

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `title` | `str` | `"Automated model evaluation"` | The title of the validation report book |
| `author` | `str` | `None` | The author name to include in the report |
| `concise` | `bool` | `True` | Whether to generate a concise report (excludes model info section) |

### Variable Selection

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `variables` | `str` or `list` | `"all"` | Variables to include in validation. Can be:<br>- `"all"`: All available variables<br>- `list`: Specific variables to validate<br>- `str`: Single variable name |

### Spatial Configuration

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `lon_lim` | `list` or `None` | `None` | Longitude limits for validation [lon_min, lon_max].<br>**Must be a list of exactly 2 floats** |
| `lat_lim` | `list` or `None` | `None` | Latitude limits for validation [lat_min, lat_max].<br>**Must be a list of exactly 2 floats** |

### Model Information

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `model` | `str` | `None` | Ecosystem model type for providing model info and schematics.<br>Currently supports: `"ersem"` |

### Process Control

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `ask` | `bool` | `False` | Whether to ask user for confirmation before overwriting existing directories |
| `r_warnings` | `bool` | `False` | Whether to show R warnings. Set to `True` only for debugging |
| `test` | `bool` | `False` | Internal testing flag. **Ignore unless testing oceanval** |

# Variable Configuration: add_gridded_comparison

## Overview
The `add_gridded_comparison` method allows you to configure gridded observational datasets for validation against model output. This method is part of the `Validator` class and enables you to define how gridded observations should be matched up with model data for validation purposes.

## Function Signature
```python
definitions.add_gridded_comparison(
    name,
    long_name=None,
    short_name=None,
    short_title=None,
    source=None,
    description=None,
    model_variable=None,
    obs_dir="auto",
    obs_var="auto",
    start=-1000,
    end=3000,
    vertical=False,
    climatology=None,
    obs_unit_multiplier=1
)
```

## Required Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `name` | `str` | **Required.** Unique identifier for the variable (e.g., "chlorophyll", "temperature") |
| `climatology` | `bool` | **Required.** Whether the gridded observations are climatological data |

## Variable Identification

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `long_name` | `str` | `None` | Descriptive name for the variable. If `None`, defaults to `name` |
| `short_name` | `str` | `None` | Short identifier for the variable. If `None`, defaults to `name` |
| `short_title` | `str` | `None` | Title for plots and reports. If `None`, defaults to `name.title()` |

## Data Source Configuration

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `source` | `str` | `None` | **Required.** Source identifier for the observational dataset |
| `description` | `str` | `None` | Description of the data source. If `None`, defaults to "Source for {source}" |
| `obs_dir` | `str` | `"auto"` | Directory path containing gridded observational data |
| `obs_var` | `str` | `"auto"` | Variable name in the observational NetCDF files |

## Model Configuration

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `model_variable` | `str` | `None` | **Required.** Name of the corresponding variable in model output files |
| `obs_unit_multiplier` | `float` | `1` | Multiplier to convert observational units to match model units |

## Temporal Configuration

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `start` | `int` | `-1000` | Start year for temporal matching (inclusive) |
| `end` | `int` | `3000` | End year for temporal matching (inclusive) |

## Spatial Configuration

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `vertical` | `bool` | `False` | Whether the gridded data has vertical (depth) dimensions |

## Usage Example

```python
import oceanval
from oceanval.parsers import definitions

# Add a chlorophyll gridded comparison
definitions.add_gridded_comparison(
    name="chlorophyll",
    long_name="Chlorophyll-a concentration",
    short_name="chl",
    short_title="Chlorophyll-a",
    source="SeaWiFS",
    description="SeaWiFS satellite chlorophyll-a data",
    model_variable="chl",
    obs_dir="/path/to/seawifs/data",
    obs_var="chlor_a",
    start=1998,
    end=2010,
    vertical=False,
    climatology=True,
    obs_unit_multiplier=1.0
)

# Add a temperature comparison with depth
definitions.add_gridded_comparison(
    name="temperature",
    long_name="Sea water temperature",
    source="EN4",
    model_variable="temp",
    obs_dir="/path/to/en4/data",
    vertical=True,
    climatology=False
)
```

## Important Notes

- **Existing Variables**: If a variable with the same `name` already exists from a point comparison, this method will merge the gridded configuration with existing point configuration
- **Source Keys**: Source identifiers cannot contain underscores (`_`)
- **Model Variable Consistency**: If the variable already exists, the `model_variable` must match the existing one (unless it was set to `"auto"`)
- **Directory Validation**: If `obs_dir` is not `"auto"`, the directory must exist
- **Unit Conversion**: Use `obs_unit_multiplier` to convert observational units to match model units (e.g., if observations are in mg/m³ and model is in mmol/m³)

## Error Handling

The method includes comprehensive validation:
- Ensures required arguments are provided
- Validates data types for all parameters
- Checks directory existence when specified
- Prevents conflicts with existing variable definitions
- Validates source key format (no underscores allowed)

# Variable Configuration: add_point_comparison

## Overview
The `add_point_comparison` method allows you to configure point (in-situ) observational datasets for validation against model output. This method is part of the `Validator` class and enables you to define how point observations should be matched up with model data for validation purposes. Point observations are typically from moorings, research cruises, or other discrete measurement platforms.

## Function Signature
```python
definitions.add_point_comparison(
    name=None,
    long_name=None,
    depths=None,
    short_name=None,
    short_title=None,
    source=None,
    description=None,
    model_variable=None,
    start=-1000,
    end=3000,
    obs_dir="auto"
)
```

## Required Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `name` | `str` | **Required.** Unique identifier for the variable (e.g., "chlorophyll", "temperature") |
| `depths` | `str` | **Required.** Depth configuration. Must be either `"surface"` or `"all"` |

## Variable Identification

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `long_name` | `str` | `None` | Descriptive name for the variable. If `None`, defaults to `name` |
| `short_name` | `str` | `None` | Short identifier for the variable. If `None`, defaults to `name` |
| `short_title` | `str` | `None` | Title for plots and reports. If `None`, defaults to `name.title()` |

## Data Source Configuration

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `source` | `str` | `None` | **Required.** Source identifier for the observational dataset |
| `description` | `str` | `None` | Description of the data source. If `None`, defaults to "Source for {source}" |
| `obs_dir` | `str` | `"auto"` | Directory path containing point observational data (CSV files) |

## Model Configuration

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `model_variable` | `str` | `None` | **Required.** Name of the corresponding variable in model output files |

## Temporal Configuration

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `start` | `int` | `-1000` | Start year for temporal matching (inclusive) |
| `end` | `int` | `3000` | End year for temporal matching (inclusive) |

## Point Data File Requirements

The CSV files in the observation directory must contain specific columns:

### Required Columns
- `lon`: Longitude coordinate
- `lat`: Latitude coordinate  
- `observation`: The measured value

### Optional Columns
- `year`: Year of observation
- `month`: Month of observation
- `day`: Day of observation
- `depth`: Depth of observation (required if `depths="all"`)
- `source`: Data source identifier

### Invalid Columns
Any columns not in the valid list (`lon`, `lat`, `year`, `month`, `day`, `depth`, `observation`, `source`) will cause an error.

## Usage Examples

### Surface Chlorophyll from Multiple Sources
```python
import oceanval
from oceanval.parsers import definitions

# Add surface chlorophyll point comparison
definitions.add_point_comparison(
    name="chlorophyll",
    long_name="Chlorophyll-a concentration",
    short_name="chl",
    short_title="Chlorophyll-a",
    depths="surface",
    source="CPR",
    description="Continuous Plankton Recorder chlorophyll data",
    model_variable="chl",
    obs_dir="/path/to/cpr/data",
    start=1990,
    end=2020
)
```

### Temperature Profile Data
```python
# Add temperature comparison with all depths
definitions.add_point_comparison(
    name="temperature",
    long_name="Sea water temperature", 
    depths="all",
    source="CTD",
    description="CTD profile temperature measurements",
    model_variable="temp",
    obs_dir="/path/to/ctd/data",
    start=2000,
    end=2015
)
```

### Combining with Existing Gridded Comparison
```python
# First add gridded comparison
definitions.add_gridded_comparison(
    name="salinity",
    source="WOA",
    model_variable="sal",
    climatology=True
)

# Then add point comparison for the same variable
definitions.add_point_comparison(
    name="salinity",  # Same name merges with gridded config
    depths="all",
    source="Argo",
    description="Argo float salinity measurements",
    model_variable="sal",  # Must match existing model_variable
    obs_dir="/path/to/argo/data"
)
```

## Important Notes

- **CSV File Validation**: All CSV files in the observation directory are automatically validated for proper column structure
- **Existing Variables**: If a variable with the same `name` already exists from a gridded comparison, this method will merge the point configuration with existing gridded configuration
- **Source Keys**: Source identifiers cannot contain underscores (`_`)
- **Model Variable Consistency**: If the variable already exists, the `model_variable` must match the existing one (unless it was set to `"auto"`)
- **Directory Validation**: If `obs_dir` is not `"auto"`, the directory must exist and contain at least one CSV file
- **Vertical Detection**: The method automatically detects if data is vertical (3D) based on the presence of `depth` columns in CSV files
- **Temporal Matching**: Point observations are matched to model output using exact day/month/year matching when available

## Depth Configuration

| Value | Description | Requirements |
|-------|-------------|--------------|
| `"surface"` | Only surface observations | CSV files should not contain `depth` column |
| `"all"` | All depth levels | CSV files may contain `depth` column for 3D matching |

## Error Handling

The method includes comprehensive validation:
- Ensures required arguments (`name`, `depths`) are provided
- Validates `depths` parameter is either `"surface"` or `"all"`
- Validates data types for all parameters
- Checks directory existence and CSV file presence when specified
- Validates CSV file structure and column names
- Prevents conflicts with existing variable definitions
- Validates source key format (no underscores allowed)
- Ensures required columns (`lon`, `lat`, `observation`) are present in all CSV files



