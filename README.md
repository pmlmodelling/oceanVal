![GitHub Testing](https://github.com/pmlmodelling/ecoval/actions/workflows/python-app-daily.yml/badge.svg)

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



