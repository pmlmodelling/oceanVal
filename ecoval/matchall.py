import copy
import time
import nctoolkit as nc
import re
import importlib
import glob
import subprocess
import multiprocessing
import pathlib
import os
import pandas as pd
import string
import random
import warnings
import pickle
import xarray as xr
from ecoval.session import session_info
from ecoval.parsers import Validator, definitions
from multiprocessing import Manager
from tqdm import tqdm
from ecoval.utils import extension_of_directory
from ecoval.parsers import generate_mapping
from ecoval.gridded import gridded_matchup

def is_z_up(ff, variable = None):
    import netCDF4 as nc4
    try:
        ds1 = nc.open_data(ff, checks = False)
        var = ds1.variables[0]
        if variable is not None:
            var = variable
        # select variable using nco
        ds1.nco_command(f"ncks -v {var}")
        ds1.run()
        ds = xr.open_dataset(ds1[0])
        ds = ds
        for x in ds[var].metpy.coordinates("longitude"):
            lon_name = x.name
        for x in ds[var].metpy.coordinates("latitude"):
            lat_name = x.name
        for x in ds[var].metpy.coordinates("time"):
            time_name = x.name
        coords = [x for x in list(ds.coords) if x not in [lon_name, lat_name, time_name]]
        coords = [x for x in coords if "time" not in x.lower()]

        ds = nc4.Dataset(ff)
        if len(coords) == 1:

            z = ds.variables[coords[0]]
            if hasattr(z, 'positive'):
                if z.positive == 'down':
                    return False
                else:
                    raise ValueError("The z-axis is down. You therefore need to pre-process your data to have a z-axis that is up.") 
        raise ValueError("Could not determine if z-axis is down from the provided file.")
    except:
        raise ValueError("Could not determine if z-axis is down from the provided file.")


def extract_units(df, sim_dir, n_dirs_down):
    # 
    # remove df rows where pattern is None
    df = df[df.pattern.notna()].reset_index(drop=True)
    patterns = set(df.pattern.dropna())
    sim_dir = sim_dir + "/"
    file_mapping = dict()
    for pp in patterns:
        wild_card = pp
        for i in range(n_dirs_down):
            wild_card = "/**/" + wild_card
        wild_card = wild_card.replace("**", "*")
        # replace double stars with 1
        wild_card = wild_card.replace("**", "*")
        if wild_card[0] == "/":
            wild_card = wild_card[1:]
        if pp in file_mapping:
            continue
        if pp is None:
            continue
        # find first file matching sim_dir + pp
        # efficient approach, not using glob, recursive
          #  wild_card = os.path.basename(wild_card)
        for y in pathlib.Path(sim_dir).glob(wild_card):
            path = y
            # convert to string
            path = str(path)
            break

        file_mapping[pp] = path 
    # unit is None
    df["unit"] = None
    for index, row in df.iterrows():
        variable = row['variable']
        try:
            pattern = row['pattern']
            file = file_mapping[pattern] 
            # variable
            variable = row['variable']
            model_variable = row['model_variable']
            model_variable = model_variable.split("+")[0]
            ds = nc.open_data(file, checks = False)
            ds_contents = ds.contents
            unit = list(ds_contents.query("variable == @model_variable").unit)[0]
            df.at[index, 'unit'] = unit
        except:
            pass
    return df.loc[:,["variable", "unit"]]

# a list of valid variables for validation
valid_vars = definitions.keys 
# add some additionals

session_warnings = Manager().list()

nc.options(parallel=True)
nc.options(progress=False)


def mm_match(
    ff,
    model_variable,
    df,
    df_times,
    ds_depths,
    variable,
    df_all,
    layer = None
):
    """
    Parameters
    -------------
    ff: str
        Path to file
    model_variable: str
        Variable name in the simulation 
    df: pd.DataFrame
        Dataframe of observational data
    df_times: pd.DataFrame
        Dataframe of observational data with /erie_0001.nctime information
    ds_depths: list
        Depths to match

    """

    if session_info["cache"]:
        try:
            ff_read = session_info["cache_mapping"].query("path == @ff & layer == @layer & variable == @variable").output
            # read this pickle file in
            with open(ff_read.values[0], "rb") as f:
                df_ff = pickle.load(f)
                df_all.append(df_ff)
                return None
        except:
            pass

    df_ff = None

    if ds_depths is not None:
        nc.session.append_safe(ds_depths[0])
    try:
        with warnings.catch_warnings(record=True) as w:
            ds = nc.open_data(ff, checks=False)
            var_match = model_variable.split("+")

            valid_locs = ["lon", "lat", "year", "month", "day", "depth"]
            valid_locs = [x for x in valid_locs if x in df.columns]

            valid_times = (
                "year" in df.columns or "month" in df.columns or "day" in df.columns
            )

            if valid_times:
                df_locs = (
                    df_times.query("path == @ff")
                    .merge(df)
                    .loc[:, valid_locs]
                    .drop_duplicates()
                    .reset_index(drop=True)
                )
            else:
                df_locs = df.loc[:, valid_locs]

            ds.subset(variables=var_match)
            # not benbio
            if "benbio" != variable:
                if "depth" not in df_locs.columns:
                    ds.cdo_command("topvalue")

            if (
                "year" in df_locs.columns
                or "month" in df_locs.columns
                or "day" in df_locs.columns
            ):
                # idenify if the files have data from multiple days
                # if "day" in df_locs.columns:
                #     if len(set(df_locs.day)) < 3:
                #         df_locs = (
                #             df_locs.drop(columns=["month"])
                #             .drop_duplicates()
                #             .reset_index(drop=True)
                #         )
                ff_indices = df_times.query("path == @ff")

                ff_indices = ff_indices.reset_index(drop=True).reset_index()
                ff_indices = ff_indices
                ff_indices = ff_indices.merge(df_locs)
                ff_indices = ff_indices["index"].values
                ff_indices = [int(x) for x in ff_indices]
                ff_indices = list(set(ff_indices))

                if len(ff_indices) == 0:
                    return None
                ds.subset(time=ff_indices)
            ds.as_missing(0)
            ds.run()

            if len(var_match) > 1:
                    ds.sum_all()
            the_dict = {"model_variable": model_variable}
            session_info["adhoc"] = copy.deepcopy(the_dict)

            if len(df_locs) > 0:
                ds.run()
                df_ff = ds.match_points(
                    df_locs, depths=ds_depths, quiet=True, max_extrap = 0
                )
                if df_ff is not None:
                    valid_vars = ["lon", "lat", "year", "month", "day", "depth"]
                    for vv in ds.variables:
                        valid_vars.append(vv)
                    valid_vars = [x for x in valid_vars if x in df_ff.columns]
                    df_ff = df_ff.loc[:, valid_vars]
                    # add this to the cache if necessary
                    if session_info["cache"]:
                        cache_dir = session_info["cache_dir"]
                        if cache_dir is not None:
                            if not os.path.exists(cache_dir):
                                os.makedirs(cache_dir)
                            # create a random string
                            random_string = "".join(
                                random.choices(string.ascii_lowercase + string.digits, k=10)
                            )
                            cache_file = (
                                cache_dir
                                + "output/"  
                                + "/matchup_"
                                + layer
                                + "_"
                                + variable
                                + "_"
                                + random_string
                                + ".pkl"
                            )
                            if not os.path.exists(cache_dir + "/output"):
                                os.makedirs(cache_dir + "/output")
                            with open(cache_file, "wb") as f:
                                pickle.dump(df_ff, f)
                            # add a mapping to session_info["cache_files"]
                            # add to session_info["cache_dir"] + "/mappings"
                            mapping_file = (
                                cache_dir
                                + "/mappings/mapping_"
                                + layer
                                + "_"
                                + variable
                                + "_"
                                + random_string
                                + ".pkl"
                            )
                            if not os.path.exists(cache_dir + "/mappings"):
                                os.makedirs(cache_dir + "/mappings")
                            # dump ff
                            with open(mapping_file, "wb") as f:
                                output_dir = {ff: cache_file}
                                pickle.dump(output_dir, f)

                    df_all.append(df_ff)
            else:
                return None
        if df_ff is not None:
            for ww in w:
                if str(ww.message) not in session_warnings:
                    session_warnings.append(str(ww.message))

    except Exception as e:
        print(e)


def get_time_res(x, folder=None):
    """
    Get the time resolution of the netCDF files


    Parameters
    -------------
    x : str
        The extension of the file
    folder : str
        The folder containing the netCDF files

    Returns
    -------------
    res : str
        The time resolution of the netCDF files

    """

    final_extension = extension_of_directory(folder)

    if final_extension[0] == "/":
        final_extension = final_extension[1:]

    wild_card = final_extension + x
    wild_card = wild_card.replace("**", "*")
    # replace double stars with 1
    wild_card = wild_card.replace("**", "*")

    wild_card = os.path.basename(wild_card)
    for y in pathlib.Path(folder).glob(wild_card):
        path = y
        # convert to string
        path = str(path)
        break

    ds = nc.open_data(path, checks=False)
    ds_times = ds.times
    months = [x.month for x in ds_times]
    days = [x.day for x in ds_times]
    years = [x.year for x in ds_times]
    df_times = pd.DataFrame({"month": months, "day": days, "year": years})

    n1 = len(
        df_times.loc[:, ["month", "year"]].drop_duplicates().reset_index(drop=True)
    )
    n2 = len(df_times)
    if n1 == n2:
        return "m"
    else:
        return "d"


random_files = []


def extract_variable_mapping(folder, exclude=[], n_check = None):
    """
    Find paths to netCDF files
    Parameters
    -------------
    folder : str
        The folder containing the netCDF files
    exclude : list
        List of strings to exclude

    Returns
    -------------
    all_df : pd.DataFrame
        A DataFrame containing the paths to the netCDF files
    """

    # add restart to exclude
    exclude.append("restart")

    while True:

        levels = session_info["levels_down"]

        new_directory = folder + "/"
        if levels > 0:
            for i in range(levels + 1):
                dir_glob = glob.glob(new_directory + "/**")
                # randomize dir_glob

                random.shuffle(dir_glob)
                for x in dir_glob:
                    # figure out if the the base directory is an integer
                    try:
                        if levels != 0:
                            y = int(os.path.basename(x))
                        new_directory = x + "/"
                    except:
                        pass
        options = glob.glob(new_directory + "/**.nc")
        # if n_check is not None and an integer, limit options to n_check
        if n_check is not None and isinstance(n_check, int):
            options = random.sample(options, min(n_check, len(options)))
        if True:
            # options = [x for x in options if "part" not in os.path.basename(x)]
            options = [x for x in options if "restart" not in os.path.basename(x)]

        if len([x for x in options if ".nc" in x]) > 0:
            break

    all_df = []
    print("********************************")
    print("Parsing model information from netCDF files")

    # remove any files from options if parts of exclude are in them
    for exc in exclude:
        options = [x for x in options if f"{exc}" not in os.path.basename(x)]

    print("Searching through files in a random directory to identify variable mappings")
    # randomize options
    for ff in tqdm(options):
        random_files.append(ff)
        ds = nc.open_data(ff, checks=False)
        stop = True
        ds_dict = generate_mapping(ds)
        try:
            ds_dict = generate_mapping(ds)
            stop = False
        # output error and ff
        except:
            pass
        if stop:
            continue

        ds_vars = ds.variables

        if len([x for x in ds_dict.values() if x is not None]) > 0:
            new_name = ""
            for x in os.path.basename(ff).split("_"):
                try:
                    y = int(x)
                    if len(new_name) > 0:
                        new_name = new_name + "_**"
                    else:
                        new_name = new_name + "**"
                except:
                    if len(new_name) > 0:
                        new_name = new_name + "_" + x
                    else:
                        new_name = x
            # replace integers in new_name with **

            new_dict = dict()
            for key in ds_dict:
                if ds_dict[key] is not None:
                    new_dict[ds_dict[key]] = [key]
            # new_name. Replace numbers between _ with **

            # replace integers with 4 or more digits with **
            new_name = re.sub(r"\d{4,}", "**", new_name)
            # replace strings of the form _12. with _**.
            new_name = re.sub(r"\d{2,}", "**", new_name)
            # new_name = re.sub(r"_\d{2,}\.", "_**.", new_name)

            all_df.append(
                pd.DataFrame.from_dict(new_dict).melt().assign(pattern=new_name)
            )

    all_df = pd.concat(all_df).reset_index(drop=True)

    patterns = set(all_df.pattern)
    resolution_dict = dict()
    for folder in patterns:
        resolution_dict[folder] = get_time_res(folder, new_directory)
    all_df["resolution"] = [resolution_dict[x] for x in all_df.pattern]

    all_df = (
        all_df.sort_values("resolution").groupby("value").head(1).reset_index(drop=True)
    )
    all_df = all_df.rename(columns={"variable": "model_variable"})
    all_df = all_df.rename(columns={"value": "variable"})
    all_df = all_df.drop(columns="resolution")
    all_df = all_df.loc[:, ["variable", "model_variable", "pattern"]]

    return all_df


def matchup(
    sim_dir=None,
    start=None,
    end=None,
    lon_lim=None,
    lat_lim=None,
    cores=6,
    thickness=None,
    n_dirs_down=2,
    point_time_res=["year", "month", "day"],
    obs_dir="default",
    everything=False,
    overwrite=True,
    ask=True,
    out_dir="",
    exclude=[],
    cache = True,
    n_check = None,
    **kwargs,
):
    """
    Match up model with observational data

    Parameters
    -------------

    sim_dir : str
        Folder containing model output
    start : int
        Start year. First year of the simulations to matchup.
        This must be supplied
    end : int
        End year. Final year of the simulations to matchup.
        This must be supplied
    gridded : str, or list 
        This defaults to ['chlorophyll', 'nitrate'].
        This is a list of all gridded surface data to matchup. 
    point: list
        List of all point variables to matchup for all depths. Default is [].
    cores : int
        Number of cores to use for parallel extraction and matchups of data.
        Default is 6, or the system cores if less than 6. 
        If you use a large number of cores you may run into RAM issues, so keep an eye on things.
    thickness : str
        Path to a thickness file, i.e. cell vertical thickness or the name of the thickness variable. This only needs to be supplied if the variable is missing from the raw data.
        If the e3t variable is in the raw data, it will be used, and thickness does not need to be supplied.
    n_dirs_down : int
        Number of levels down to look for netCDF files. Default is 2, ie. the files are of the format */*/*.nc.
    point_time_res : list or dict
        List of strings or a dict. Default is ['year', 'month', 'day']. This is the time resolution of the point data matchup.
        If you want fine-grained control, provide a dictionary where the key is the variable and the value is a list of strings.
        If you provide this list make sure all variables have keys, or else provide a key called "default" with a value to use when the variable is not stated explicitly.
    exclude : list
        List of strings to exclude. This is useful if you have files in the directory that you do not want to include in the matchup.
    lon_lim : list
        List of two floats, which must be provided. The first is the minimum longitude, the second is the maximum longitude. Default is None.
    lat_lim : list
        List of two float, which must be provided.. The first is the minimum latitude, the second is the maximum latitude. Default is None.
    obs_dir : str
        Path to validation data directory. Default is 'default'. If 'default', the data directory is taken from the session_info dictionary.
    everything : bool
        If True, all possible variables at the surface and near-bottom are matched up. Default is False.
        In most cases this is overkill because point data may not tell you much gridded does not.
    ask : bool
        If True, the user will be asked if they are happy with the matchups. Default is True.
    out_dir : str
        Path to output directory. Default is "", so the output will be saved in the current directory.
    kwargs: dict
        Additional arguments

    Returns
    -------------
    None
    Data will be stored in the matched directory.

    """

    gridded = None
    point = None



    if isinstance(point_time_res, str):
        point_time_res = [point_time_res]
    if isinstance(point_time_res, list) is False:
        raise TypeError("point_time_res must be a list or a string")
    session_info["point_time_res"] = copy.deepcopy(point_time_res)
    # check it is str or list

    # make point a list if it's None
    if point is None:
        point = dict()
        point["all"] = []
        point["surface"] = []
        point["bottom"] = []
    
    # if point is str, make it a list
    if isinstance(point, str):
        point = [point]

    if not isinstance(point, list) and not isinstance(point, dict):
        raise TypeError("point must be a list or a string")
    # if point is a list, convert to a dictionary
    if isinstance(point, list):
        point_new = copy.deepcopy(point)
        point = dict()
        point["all"] = point_new
        point["surface"] = []
        point["bottom"] = []
    # loop through definition keys
    for key in definitions.keys:
        try:
            if definitions[key].depths == "surface":
                if key not in point["surface"]:
                    point["surface"].append(key)
        except:
            pass
        try:
            if definitions[key].depths == "all":
                if key not in point["all"]:
                    point["all"].append(key)
        except:
            pass
        # do the same for gridded
        try:
            if definitions[key].gridded:
                if gridded is None:
                    gridded = []
                if key not in gridded:
                    gridded.append(key)
        except:
            pass

    if isinstance(point, dict):
        # check keys are valid
        for key in point.keys():
            if key not in ["all", "surface", "bottom"]:
                raise ValueError("point dictionary keys must be 'all', 'surface' or 'bottom'")
        # check values are lists
        for key in point.keys():
            if isinstance(point[key], str):
                point[key] = [point[key]]
            # if it's None, convert to empty list
            if point[key] is None:
                point[key] = []
            if not isinstance(point[key], list):
                raise TypeError("point dictionary values must be lists or strings")
        # if any keys are absent, make them empty lists
        for key in ["all", "surface", "bottom"]:
            if key not in point.keys():
                point[key] = []

    # if gridded is str, make it a list
    if isinstance(gridded, str):
        gridded = [gridded]
    # None too
    if gridded is None:
        gridded = []

    ignore_invert_check = False
    # go through kwargs
    for key, value in kwargs.items():
        if key == "ignore_invert_check":
            ignore_invert_check = value
            # must be a bool
            if not isinstance(ignore_invert_check, bool):
                raise TypeError("ignore_invert_check must be a boolean")

    # convert sim_dir to hard path
    if sim_dir is not None:
        sim_dir = os.path.abspath(sim_dir)

    # if cache is True, create a cache directory in out_dir
    if cache:
        if out_dir == "":
            out_dir = "./"
        cache_dir = out_dir + "/.cache_ecoval/"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        session_info["cache_dir"] = cache_dir
        session_info["cache"] = True
        # create a mappings directory in cache_dir
        mappings_dir = cache_dir + "/mappings/"
        if not os.path.exists(mappings_dir):
            os.makedirs(mappings_dir)
        # list files in mappings_dir
        paths = glob.glob(mappings_dir + "/*.pkl")
        mapping_df = []
        for ff in paths:
            with open(ff, "rb") as f:
                output_dir = pickle.load(f)
            ff_path = list(output_dir.keys())[0]
            ff_output = list(output_dir.values())[0]
            ff_layer = os.path.basename(ff).split("_")[1]
            ff_variable = os.path.basename(ff).split("_")[2]
            mapping_df.append(pd.DataFrame({"variable": [ff_variable], "layer": [ff_layer], "path": [ff_path], "output": [ff_output]}))
        if len(mapping_df) > 0:
            mapping_df = pd.concat(mapping_df).reset_index(drop=True)
        session_info["cache_mapping"] = mapping_df

    else:
        session_info["cache_dir"] = None
        session_info["cache"] = False
    
    # check everything
    if not isinstance(everything, bool):
        raise TypeError("everything must be a boolean")
    if not isinstance(ask, bool):
        raise TypeError("ask must be a boolean")
    if not isinstance(overwrite, bool):
        raise TypeError("overwrite must be a boolean")
    # check n_dirs_down is an integer
    if not isinstance(n_dirs_down, int):
        raise TypeError("n_dirs_down must be an integer")
    if n_dirs_down < 0:
        raise ValueError("n_dirs_down must be a positive integer")
    # check if exclude is a list or str
    if not isinstance(exclude, list):
        if isinstance(exclude, str):
            exclude = [exclude]
        else:
            raise TypeError("exclude must be a list or a string")

    if thickness is not None:
        if isinstance(thickness, str):
            # if it ends with .nc check it exists
            if thickness.endswith(".nc"):
                if not os.path.exists(thickness):
                    raise FileNotFoundError(f"{thickness} does not exist")

    if cores == 6:
        if cores > os.cpu_count():
            cores = os.cpu_count()
            print(f"Setting cores to {cores} as this is the number of cores available on your system")
    nc.options(cores=cores)

    # check lon_lim and lat_lim are lists

    if lon_lim is None:
        raise ValueError(
            "Please provide lon_lim as a list of two floats [lon_min, lon_max]. Sensible values for the AMM7 area lon_lim = [-18,9] and lat_lim = [42, 63]"
        )
    if lat_lim is None:
        raise ValueError(
            "Please provide lon_lim as a list of two floats [lon_min, lon_max]. Sensible values for the AMM7 area lon_lim = [-18,9] and lat_lim = [42, 63]"
        )

    if lon_lim is not None or lat_lim is not None:
        # check both are lists
        if not isinstance(lon_lim, list) or not isinstance(lat_lim, list):
            raise TypeError("lon_lim and lat_lim must be lists")
    # add this info to session_info
    session_info["lon_lim"] = lon_lim
    session_info["lat_lim"] = lat_lim


    if obs_dir != "default":
        if not os.path.exists(obs_dir):
            raise ValueError(f"{obs_dir} does not exist")
        session_info["obs_dir"] = obs_dir

    ds_depths = None

    # check everything is valid

    if start is None:
        raise ValueError("Please provide a start year")

    if end is None:
        raise ValueError("Please provide an end year")

    if isinstance(start, int) is False:
        raise TypeError("Start must be an integer")

    if isinstance(end, int) is False:
        raise TypeError("End must be an integer")

    # check if the sim_dir exists
    if sim_dir is None:
        raise ValueError("Please provide a sim_dir directory")

    if not os.path.exists(sim_dir):
        raise ValueError(f"{sim_dir} does not exist")

    # set up session info, which will be needed by gridded_matchup
    session_info["overwrite"] = overwrite

    # add out_dir to session_info
    if out_dir != "":
        session_info["out_dir"] = out_dir + "/"
    else:
        session_info["out_dir"] = ""

    if n_dirs_down is not None:
        session_info["levels_down"] = n_dirs_down
    else:
        session_info["levels_down"] = 2

    if obs_dir != "default":
        session_info["user_dir"] = True
    else:
        obs_dir = session_info["obs_dir"]

    sim_start = -1000
    sim_end = 10000
    for key in kwargs:
        key_failed = True
        if key[:3] == "fol":
            if sim_dir is None:
                sim_dir = kwargs[key]
                key_failed = False
        if key_failed:
            raise ValueError(f"{key} is not a valid argument")

    if end is not None:
        sim_end = end

    if start is not None:
        sim_start = start

    # check validity of variables chosen

    all_df = None

    var_choice = gridded 
    var_choice = list(set(var_choice))
    if isinstance(gridded, str):
        var_choice = [gridded]
    
    for vv in var_choice:
        if vv not in valid_vars and vv != "all":
            # suggest another variable based on similarity to valid_vars
            from difflib import get_close_matches

            close = get_close_matches(vv, valid_vars)
            if len(close) > 0:
                raise ValueError(
                    f"{vv} is not a valid variable. Did you mean {close[0]}?"
                )
            if vv != "default":
                raise ValueError(
                    f"{vv} is not a valid variable. Please choose from {valid_vars}"
                )

    if all_df is None:
        all_df = extract_variable_mapping(sim_dir, exclude=exclude, n_check = n_check)

        # add in anything that is missing
        all_vars = valid_vars

        missing_df = pd.DataFrame({"variable": all_vars}).assign( model_variable=None, pattern=None)

        all_df = (
            pd.concat([all_df, missing_df])
            .groupby("variable")
            .head(1)
            .reset_index(drop=True)
        )
    # check if the variables are in all_df

    pattern = all_df.reset_index(drop=True).iloc[0, :].pattern

    final_extension = extension_of_directory(sim_dir)

    if final_extension[0] == "/":
        final_extension = final_extension[1:]

    wild_card = final_extension + pattern
    wild_card = wild_card.replace("**", "*")
    for x in pathlib.Path(sim_dir).glob(wild_card):
        path = x
        # convert to string
        path = str(path)
        break

    try:
        ds = nc.open_data(path, checks=False)
    except:
        raise ValueError("Problems finding files. Check n_dirs_down arg")

    # check length of lon_lim and lat_lim
    if len(session_info["lon_lim"]) != 2 or len(session_info["lat_lim"]) != 2:
        raise ValueError(
            "lon_lim and lat_lim must be lists of two floats, e.g. [-18, 9] and [42, 63]"
        )   

    with warnings.catch_warnings(record=True) as w:
        lon_max = session_info["lon_lim"][1]
        lon_min = session_info["lon_lim"][0]
        lat_max = session_info["lat_lim"][1]
        lat_min = session_info["lat_lim"][0]

    if session_info["user_dir"]:
        valid_points = list(
            set([x for x in glob.glob(obs_dir + "/point/all/*")])
        )
        for key in definitions.keys:
            dir_name = definitions[key].point_dir
            if os.path.exists(dir_name):
                if key not in valid_points:
                    valid_points.append(key)
    else:
        valid_points = list(set([x for x in glob.glob(obs_dir + "/point/all/*")]))
    # extract directory base name
    valid_points = [os.path.basename(x) for x in valid_points]

    for key in definitions.keys:
        dir_name = definitions[key].point_dir
        if dir_name is not None:
            if os.path.exists(dir_name):
                if key not in valid_points:
                    valid_points.append(key)


    if True:
        if session_info["user_dir"]:
            valid_gridded = [
                os.path.basename(x) for x in glob.glob(obs_dir + "/gridded/*")
            ]
            for key in definitions.keys:
                dir_name = definitions[key].gridded_dir
                if os.path.exists(dir_name):
                    if key not in valid_gridded:
                        valid_gridded.append(key)
        else:
            valid_gridded = [
                os.path.basename(x)
                for x in glob.glob(obs_dir + f"/gridded/*")
            ]
            # add in global data
            valid_gridded += [
                os.path.basename(x) for x in glob.glob(obs_dir + "/gridded/*")
            ]
            for key in definitions.keys:
                dir_name = definitions[key].gridded_dir
                if os.path.exists(dir_name):
                    if key not in valid_gridded:
                        valid_gridded.append(key)
    if len(gridded) > 0:
        if gridded[0] == "default" and len(gridded) == 1:
            gridded = valid_gridded

    dirs = glob.glob(obs_dir + "/gridded/**")

    if len(gridded) == 0 and len(point) == 0:
        raise ValueError("Please provide at least one variable to matchup")

    if everything:
        gridded = valid_gridded
        # only valid variables
        gridded = [x for x in gridded if x in valid_vars]
        point = dict()
        point["all"] = []
        point["surface"] = []
        point["bottom"] = []
        point["all"] = copy.deepcopy(valid_points)
        for vv in point["all"]:
            try:
                if definitions[vv].vertical is False:
                    point["all"].remove(vv)
                    point["surface"].append(vv)
            except:
                pass

    gridded = [x for x in gridded if x in valid_gridded]

    vars_available = list(
        all_df
        # drop rows where pattern is None
        .dropna()
        # get all variables
        .variable
    )
    # check variables chosen are valid

    remove = []

    gridded = [x for x in gridded if x in vars_available]
    #point = [x for x in point if x in valid_points]
    #point = [x for x in point if x in vars_available]
    #print(vars_available)
    for key in point.keys():
        point[key] = [x for x in point[key] if x in vars_available]
        point[key] = [x for x in point[key] if x in valid_points]

    for vv in point["all"]:
        if definitions[vv].vertical is False:
            point["all"].remove(vv)
            point["surface"].append(vv)
    

    var_chosen = gridded + point["all"] + point["surface"] + point["bottom"]
    var_chosen = list(set(var_chosen))

    if end < 1998:
        # kd
        gridded.remove("kd")
        print("kd is only available from 1998 onwards, removing from gridded variables")
    # create matched directory
    if not os.path.exists("matched"):
        if session_info["out_dir"] != "":
            # recusively create the directory
            os.makedirs(session_info["out_dir"] + "/matched", exist_ok=True)
        else:
            os.mkdir("matched")

    invert_thickness = False
    point_all = point["all"] + point["surface"] + point["bottom"]
    if len(point_all) > 0:
        print("Sorting out thickness")
        ds_depths = False
        with warnings.catch_warnings(record=True) as w:
            # extract the thickness dataset
            e3t_found = False
            if thickness is not None and os.path.exists(thickness):
                ds_thickness = nc.open_data(thickness, checks=False)
                invert_thickness = is_z_up(ds_thickness[0])
                if len(ds_thickness.variables) != 1:
                    if (
                        len(
                            [
                                x
                                for x in ds_thickness.variables
                                if "e3t" in x
                            ]
                        )
                        == 0
                    ):
                        raise ValueError(
                            "The thickness file has more than one variable and none include e3t. Please provide a single variable!"
                        )
                ds_thickness.rename({ds_thickness.variables[0]: "e3t"})
                e3t_found = True
                thickness = "e3t"
            else:
                print(
                    "Vertical thickness is required for your matchups, but they are not supplied"
                )
                print("Searching through simulation output to find it")
                if thickness is None:
                    thickness = "e3t"
                for ff in random_files:
                    print("Checking file for thickness: " + ff)
                    # do this quietly
                    with warnings.catch_warnings(record=True) as w:
                        ds_thickness = nc.open_data(ff, checks=False)
                        if thickness in ds_thickness.variables:
                            e3t_found = True
                            invert_thickness = is_z_up(ff, thickness)
                            break
                        else:
                            if (
                                len(
                                    [
                                        x
                                        for x in ds_thickness.variables
                                        if thickness in x
                                    ]
                                )
                                > 0
                            ):
                                e3t_found = True
                                invert_thickness = is_z_up(ff, thickness)
                                break

            if not e3t_found:
                raise ValueError("Unable to find e3t")

            if os.path.exists(thickness) == False:
                if len(ds_thickness.times) > 0:
                    ds_thickness.subset(time=0, variables=f"{thickness}*")
                else:
                    ds_thickness.subset(variables=f"{thickness}*")
            ds_thickness.run()
            var_sel = (
                ds_thickness.contents.query(
                    f"variable.str.contains('{thickness}')"
                )
                .query("nlevels > 1")
                .variable
            )
            ds_thickness.subset(variables=var_sel)
            ds_thickness.as_missing(0)
            if len(ds_thickness.variables) > 1:
                if "e3t" in ds_thickness.variables:
                    ds_thickness.subset(variables=f"{thickness}*")
                else:
                    ds_thickness.subset(variables=ds_thickness.variables[0])
            ds_thickness.run()
            print(
                f"Thickness variable is {ds_thickness.variables[0]} from {ff}"
            )
            #####
            # now output the bathymetry if it does not exists

            ff_bath = (
                session_info["out_dir"] + "matched/model_bathymetry.nc"
            )
            if not os.path.exists(ff_bath):
                ds_bath = ds_thickness.copy()
                ds_bath.vertical_sum()
                ds_bath.to_nc(ff_bath, zip=True)

            if invert_thickness and ignore_invert_check is False:
                # user check
                x = input( "The thickness data appears to have the sea surface at the bottom (i.e. increasing depth values down. DO NOT PROCEED IF THIS IS A NEMO SIMULATION. Is this correct? (y/n) ")
                if x.lower() == "n":
                    return None

            ds_thickness.run()
            if invert_thickness:
                # raise ValueError("inverted")
                ds_thickness.invert_levels()
                ds_thickness.run()

            ds_depths = ds_thickness.copy()

            ds_depths.vertical_cumsum()
            ds_thickness / 2
            ds_depths - ds_thickness
            ds_depths.run()
            ds_depths.rename({ds_depths.variables[0]: "depth"})
            if invert_thickness:
                ds_depths.run()
                ds_depths.invert_levels()
                # ds_depths.to_nc("foo.nc")
            ds_depths.run()
            try:
                ds_depths.fix_amm7_grid()
            except:
                pass

        for ww in w:
            if str(ww.message) not in session_warnings:
                session_warnings.append(str(ww.message))
        if ds_depths is False:
            raise ValueError(
                "You have asked for variables that require the specification of thickness"
            )
        print("Thickness is sorted out")

    # add the global checker here
    # sort all_df alphabetically by variable
    all_df = all_df.sort_values("variable").reset_index(drop=True)
    gridded.sort()
    print("Variables that will be matched up")
    print("******************************")
    if len(gridded) > 0:
        print(
            f"The following variables will be matched up with gridded surface data: {','.join(gridded)}"
        )

    print("******************************")
    # do a unit check
    print("Doing a unit check...")
    data_path = importlib.resources.files("ecoval").joinpath("data/standard_units.feather")
    df_standard_units = pd.read_feather(data_path)
    df_units = extract_units(all_df, sim_dir, n_dirs_down).merge(df_standard_units, on="variable", how="left")
    # only var_chosen
    df_units = df_units[df_units.variable.isin(var_chosen)].reset_index(drop=True)
    df_units = df_units.query("unit != standard_unit")
    if len(df_units) > 0:
        print("Variable units:")
        print(df_units)
        print("There are potential unit mismatches above. Please check before proceeding.")
        print("Do you want to proceed? Y/N")
        if ask:
            x = input()
        else:
            x = "y"
        if x.lower() not in ["y", "n"]:
            print("Provide Y or N")
            x = input()
        if x.lower() == "n":
            raise ValueError("Unit check failed")
    print("******************************")
    print("Unit check is complete")

    print("******************************")
    print(f"** Inferred mapping of model variable names from {sim_dir}")

    all_df_print = copy.deepcopy(all_df).reset_index(drop=True)

    # new tidied variable
    new_variable = []
    for i in range(len(all_df_print)):
        if all_df.variable[i] in var_chosen:
            if all_df.pattern[i] is not None:
                new_variable.append(all_df.variable[i] + "**")
            else:
                new_variable.append(all_df.variable[i])
        else:
            new_variable.append(all_df.variable[i])
    all_df_print["variable"] = new_variable
    all_df_print = all_df_print.sort_values("variable")
    # move variable with ** in it to the top of the data frame
    all_df_print = all_df_print.sort_values(
        by="variable", key=lambda x: x.str.replace(r".*\*\*", "", regex=True)
    )
    all_df_print = all_df_print.reset_index(drop=True)
    # add a new row with --- in it after variables with ** in them
    new_row = pd.DataFrame(
        {"variable": ["---"], "model_variable": ["---"], "pattern": ["---"]}
    )
    all_df_print = pd.concat([all_df_print, new_row], ignore_index=True)
    all_df_print = all_df_print.sort_values(
        by="variable", key=lambda x: x.str.replace(r".*\*\*", "", regex=True)
    )
    all_df_print = all_df_print.reset_index(drop=True)

    print(all_df_print.to_string(index=False))
    print(
        "Note: all possible variables are listed, not just those requested. Variables that will be matched up are starred."
    )

    print("Are you happy with these matchups? Y/N")

    if ask:
        x = input()
    else:
        x = "y"

    if x.lower() not in ["y", "n"]:
        print("Provide Y or N")
        x = input()

    if x.lower() == "n":
        length = 8
        letters = string.ascii_lowercase
        result_str = "".join(random.choice(letters) for i in range(length))
        mapping = "mapping_" + result_str + ".csv"
        print(f"Inferred mapping saved as {mapping}")
        all_df.to_csv(mapping, index=False)
        return None


    if session_info["out_dir"] != "":
        out = session_info["out_dir"] + "/matched/mapping.csv"
    else:
        out = "matched/mapping.csv"
    # check directory exists for out
    out_folder = os.path.dirname(out)
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    df_out = all_df.dropna().reset_index(drop=True)
    final_extension = extension_of_directory(sim_dir)
    df_out["pattern"] = [sim_dir + final_extension + x for x in df_out.pattern]
    df_out.to_csv(out, index=False)
    # restrict all_df to only variables chosen
    all_df = all_df.query("variable in @var_chosen").reset_index(drop=True)

    final_extension = extension_of_directory(sim_dir)
#    raise ValueError(all_df)
    path = glob.glob(sim_dir + final_extension + all_df.pattern[0])[0]
    with warnings.catch_warnings(record=True) as w:
        ds = nc.open_data(path, checks=False).to_xarray()
    lon_name = [x for x in ds.coords if "lon" in x]
    lat_name = [x for x in ds.coords if "lat" in x]
    lon = ds[lon_name[0]].values
    lat = ds[lat_name[0]].values
    lon_max = lon.max()
    lon_min = lon.min()
    lat_max = lat.max()
    lat_min = lat.min()


    # combine all variables into a list
    all_vars = gridded +  point["all"] + point["surface"] + point["bottom"]
    all_vars = list(set(all_vars))

    df_variables = all_df.query("variable in @all_vars").reset_index(drop=True)
    # remove rows where model_variable is None
    df_variables = df_variables.dropna().reset_index(drop=True)

    patterns = list(set(df_variables.pattern))

    times_dict = dict()

    print("*************************************")

    if ds_depths is not None:
        # run cdo griddes on the file and figure out if generic shows up

        output = subprocess.check_output(["cdo", "griddes", ds_depths[0]])
        if "generic" in str(output):
            ff1 = path
            ds_depths.cdo_command(f"setgrid,{ff1}")

    ff = session_info["out_dir"] + "matched/times_dict.pkl"
    # read this in
    try:
        with open(ff, "rb") as f:
            times_dict = pickle.load(f)
    except:
        times_dict = dict()
        pass

    print("*************************************")
    for pattern in patterns:
        print(f"Indexing file time information for {pattern} files")
        final_extension = extension_of_directory(sim_dir)
        ensemble = glob.glob(sim_dir + final_extension + pattern)
        for exc in exclude:
            ensemble = [x for x in ensemble if f"{exc}" not in os.path.basename(x)]

        try:
            ds = xr.open_dataset(ensemble[0])
            time_name = [x for x in list(ds.dims) if "time" in x][0]
        except:
            ds = xr.open_dataset(ensemble[0], decode_times=False)
            time_name = [x for x in list(ds.dims) if "time" in x][0]

        for ff in tqdm(ensemble):
            if ff in times_dict:
                continue
            if "restart" in ff:
                continue

            try:
                ds = xr.open_dataset(ff)
                ff_month = [int(x.dt.month) for x in ds[time_name]]
                ff_year = [int(x.dt.year) for x in ds[time_name]]
                days = [int(x.dt.day) for x in ds[time_name]]
            except:
                ds = nc.open_data(ff, checks=False)
                ds_times = ds.times
                ff_month = [int(x.month) for x in ds_times]
                ff_year = [int(x.year) for x in ds_times]
                days = [int(x.day) for x in ds_times]

            df_ff = pd.DataFrame(
                {
                    "year": ff_year,
                    "month": ff_month,
                    "day": days,
                }
            )
            times_dict[ff] = df_ff

    # save this as a pickle
    with open(session_info["out_dir"] + "matched/times_dict.pkl", "wb") as f:
        pickle.dump(times_dict, f)

    # figure out the lon/lat extent in the model
    with warnings.catch_warnings(record=True) as w:
        lons = session_info["lon_lim"]
        lats = session_info["lat_lim"]

    all_df = all_df.dropna().reset_index(drop=True)
    df_mapping = all_df
    good_model_vars = [x for x in all_df.model_variable if x is not None]

    df_mapping = all_df

    point_all = point["all"] + point["surface"] + point["bottom"]
    if len(point_all) > 0:
        print("********************************")
        print("Matching up with observational point data")
        print("********************************")

        # if model_variable is None remove from all_df

        for key, value in point.items():
            the_vars = list(df_mapping.dropna().variable)
            var_choice = [x for x in var_choice if x in the_vars]
            point_vars = value
            depths = copy.deepcopy(key)

            # sort the list
            point_vars.sort()

            for vv in point_vars:
                print(f"Matching up with {vv} point data")
                all_df = df_mapping
                all_df = all_df.query("model_variable in @good_model_vars").reset_index(
                    drop=True
                )

                all_df = all_df.dropna()
                all_df = all_df.query("variable == @vv").reset_index(drop=True)
                patterns = list(set(all_df.pattern))

                for pattern in patterns:
                    final_extension = extension_of_directory(sim_dir)
                    ensemble = glob.glob(sim_dir + final_extension + pattern)
                    for exc in exclude:
                        ensemble = [
                            x for x in ensemble if f"{exc}" not in os.path.basename(x)
                        ]

                    df_times = []
                    days = []
                    for ff in ensemble:
                        df_ff = times_dict[ff]
                        df_times.append(
                            pd.DataFrame(
                                {
                                    "month": df_ff.month,
                                    "year": df_ff.year,
                                    "day": df_ff.day,
                                }
                            ).assign(path=ff)
                        )
                    df_times = pd.concat(df_times)

                    # figure out if it is monthly or daily data

                    df_times = df_times.query(
                        "year >= @sim_start and year <= @sim_end"
                    ).reset_index(drop=True)

                    sim_paths = list(set(df_times.path))
                    sim_paths.sort()
                    # write to the report

                    min_year = df_times.year.min()
                    max_year = df_times.year.max()
                    session_info["min_year"] = min_year
                    session_info["max_year"] = max_year

                    def point_match(
                        variable, layer="all", ds_depths=None, df_times=None
                    ):
                        with warnings.catch_warnings(record=True) as w:
                            point_variable = variable
                            model_variable = list(
                                all_df.query(
                                    "variable == @point_variable"
                                ).model_variable
                            )[0]

                            if layer != "bottom":
                                layer_select = "all"
                            else:
                                layer_select = "bottom"


                            if session_info["user_dir"]:
                                paths = glob.glob(
                                    f"{obs_dir}/point/{layer_select}/{variable}/**{variable}**.feather"
                                )
                            else:
                                paths = glob.glob(
                                    f"{obs_dir}/point/{layer_select}/{variable}/**{variable}**.feather"
                                )
                            # paths bottom
                            if definitions[variable].point_dir != "auto":
                                paths = glob.glob(
                                    f"{definitions[variable].point_dir}/**.feather"
                                )

                            if session_info["user_dir"]:
                                paths_bottom = glob.glob(
                                    f"{obs_dir}/point/bottom/{variable}/**{variable}**.feather"
                                )
                            else:
                                paths_bottom = glob.glob(
                                    f"{obs_dir}/point/bottom/{variable}/**{variable}**.feather"
                                )

                            # try finding source in definitions
                            source = definitions[variable].point_source

                            if definitions[variable].point_dir == "auto":
                                paths = [x for x in paths if f"{point_variable}/" in x]

                            for exc in exclude:
                                paths = [
                                    x
                                    for x in paths
                                    if f"{exc}" not in os.path.basename(x)
                                ]

                            df = pd.concat([pd.read_feather(x) for x in paths])
                            if "year" in df.columns:
                                # find point_start
                                point_start = definitions[variable].point_start
                                point_end = definitions[variable].point_end
                                df = df.query(
                                    "year >= @point_start and year <= @point_end"
                                ).reset_index(drop=True)

                            # remove source if it's in df
                            if "source" in df.columns:
                                df = df.query("source == @source").reset_index(drop=True)
                            # if it exists, coerce year to int
                            if "year" in df.columns:
                                df = df.assign(year=lambda x: x.year.astype(int))
                                # subset to
                            if "month" in df.columns:
                                df = df.assign(month=lambda x: x.month.astype(int))
                            if "day" in df.columns:
                                df = df.assign(day=lambda x: x.day.astype(int))
                            if layer == "surface":
                                if "depth" in df.columns:
                                    df = df.query("depth <= 5").reset_index(
                                        drop=True
                                    )
                                    # drop depth
                                    df = df.drop(columns=["depth"])

                            # extract point_time_res from dictionary
                            point_time_res = copy.deepcopy(session_info["point_time_res"])
                            for x in [
                                x
                                for x in ["year", "month", "day"]
                                if x not in point_time_res
                            ]:
                                if x in df.columns:
                                    df = df.drop(columns=x)
                            # restrict the lon_lat
                            lon_min = lons[0]
                            lon_max = lons[1]
                            lat_min = lats[0]
                            lat_max = lats[1]
                            df = df.query(
                                "lon >= @lon_min and lon <= @lon_max and lat >= @lat_min and lat <= @lat_max"
                            ).reset_index(drop=True)

                            sel_these = point_time_res
                            sel_these = [x for x in df.columns if x in sel_these]
                            if variable not in [
                                "benbio"
                            ]:
                                paths = list(
                                    set(
                                        df.loc[:, sel_these]
                                        .drop_duplicates()
                                        .merge(df_times)
                                        .path
                                    )
                                )
                            else:
                                paths = list(set(df_times.path))


                            if len(paths) == 0:
                                print(f"No matching times for {variable}")
                                raise ValueError("here")

                            manager = Manager()
                            # time to subset the df to the lon/lat ranges
                            # get the minimum and maximum lon/lat
                            lon_min = float(df.lon.min())
                            lon_max = float(df.lon.max())
                            lat_min = float(df.lat.min())
                            lat_max = float(df.lat.max())

                            df_times_new = copy.deepcopy(df_times)

                            with warnings.catch_warnings(record=True) as w:
                                ds_grid = nc.open_data(paths[0], checks=False)
                                ds_grid.subset(variables=ds_grid.variables[0])
                                ds_grid.top()
                                ds_grid.subset(time=0)
                                amm7 = False
                                if max(ds_grid.contents.npoints) == 111375:
                                    amm7 = True
                                    try:
                                        ds_grid.fix_amm7_grid()
                                    except:
                                        pass
                                ds_xr = ds_grid.to_xarray()
                                for ww in w:
                                    if str(ww.message) not in session_warnings:
                                        session_warnings.append(str(ww.message))
                                lon_name = [x for x in list(ds_xr.coords) if "lon" in x][0]
                                lon_min = ds_xr[lon_name].values.min()
                                lon_max = ds_xr[lon_name].values.max()
                                lat_name = [x for x in list(ds_xr.coords) if "lat" in x][0]
                                lat_min = ds_xr[lat_name].values.min()
                                lat_max = ds_xr[lat_name].values.max()
                                df = df.query(
                                    "lon >= @lon_min and lon <= @lon_max and lat >= @lat_min and lat <= @lat_max"
                                ).reset_index(drop=True)
                                # for ww in w:
                                #     if str(ww.message) not in session_warnings:
                                #         session_warnings.append(str(ww.message))


                            valid_cols = [
                                "lon",
                                "lat",
                                "day",
                                "month",
                                "year",
                                "depth",
                                "observation",
                            ]
                            select_these = [x for x in df.columns if x in valid_cols]


                            if len(df) == 0:
                                print("No data for this variable")
                                return None

                            if "year" not in df.columns:
                                try:
                                    point_time_res.remove("year")
                                except:
                                    pass
                            if "month" not in df.columns:
                                try:
                                    point_time_res.remove("month")
                                except:
                                    pass
                            if "day" not in df.columns:
                                try:
                                    point_time_res.remove("day")
                                except:
                                    pass

                            df_all = manager.list()

                            grid_setup = False
                            pool = multiprocessing.Pool(cores)

                            pbar = tqdm(total=len(paths), position=0, leave=True)
                            results = dict()


                            for ff in paths:
                                if grid_setup is False:
                                    with warnings.catch_warnings(record=True) as w:

                                        ds_grid = nc.open_data(ff, checks=False)
                                        var = ds_grid.variables[0]
                                        ds_grid.subset(variables=var)
                                        ds_grid.top()

                                        ds_grid.as_missing(0)
                                        if max(ds_grid.contents.npoints) == 111375:
                                            try:
                                                ds_grid.fix_amm7_grid()
                                            except:
                                                pass
                                        df_grid = (
                                            ds_grid.to_dataframe().reset_index()
                                            # .dropna()
                                        )
                                        columns = [
                                            x
                                            for x in df_grid.columns
                                            if "lon" in x or "lat" in x
                                        ]
                                        df_grid = df_grid.loc[
                                            :, columns
                                        ].drop_duplicates()
                                        if not os.path.exists(
                                            session_info["out_dir"] + "matched"
                                        ):
                                            os.makedirs(
                                                session_info["out_dir"] + "matched"
                                            )
                                        df_grid.to_csv(
                                            session_info["out_dir"]
                                            + "matched/model_grid.csv",
                                            index=False,
                                        )
                                        # save ds_grid
                                        if not os.path.exists(
                                            session_info["out_dir"] + "matched"
                                        ):
                                            os.makedirs(
                                                session_info["out_dir"] + "matched"
                                            )
                                        if os.path.exists(
                                            session_info["out_dir"]
                                            + "matched/model_grid.nc"
                                        ):
                                            os.remove(
                                                session_info["out_dir"]
                                                + "matched/model_grid.nc"
                                            )
                                        ds_grid.to_nc(
                                            session_info["out_dir"]
                                            + "matched/model_grid.nc",
                                            zip=True,
                                            overwrite=True,
                                        )
                                    for ww in w:
                                        if str(ww.message) not in session_warnings:
                                            session_warnings.append(str(ww.message))

                                grid_setup = True

                                temp = pool.apply_async(
                                    mm_match,
                                    [
                                        ff,
                                        model_variable,
                                        df,
                                        df_times_new,
                                        ds_depths,
                                        point_variable,
                                        df_all,
                                        layer
                                    ],
                                )

                                results[ff] = temp

                            for k, v in results.items():
                                value = v.get()
                                pbar.update(1)

                            df_all = list(df_all)
                            df_all = [x for x in df_all if x is not None]
                            # do nothing when there is no data
                            if len(df_all) == 0:
                                print(f"No data for {variable}")
                                time.sleep(1)
                                return False

                            df_all = pd.concat(df_all)
                            if amm7:
                                df_all = (
                                    df_all.query("lon > -19")
                                    .query("lon < 9")
                                    .query("lat > 41")
                                    .query("lat < 64.3")
                                )
                            change_this = [
                                x
                                for x in df_all.columns
                                if x
                                not in [
                                    "lon",
                                    "lat",
                                    "year",
                                    "month",
                                    "day",
                                    "depth",
                                    "observation",
                                ]
                            ][0]
                            #
                            df_all = df_all.rename(
                                columns={change_this: "model"}
                            ).merge(df)
                                # add model to name column names with frac in them
                            df_all = df_all.dropna().reset_index(drop=True)
                            # read in point_bottom data
                            if len(paths_bottom) > 0 and layer == "all":
                                df_bottom = pd.concat(
                                    [pd.read_feather(x) for x in paths_bottom]
                                )
                                df_bottom = df_bottom.loc[:,["lon", "lat", "year", "month", "day", "depth", "observation"]]
                                # remove based on what's in point_time_res
                                # not benbio
                                if variable != "benbio":
                                    for x in [
                                        x
                                        for x in ["year", "month", "day"]
                                        if x not in point_time_res
                                    ]:
                                        if x in df_bottom.columns:
                                            df_bottom = df_bottom.drop(columns=x)
                                df_bottom = df_bottom.assign(bottom = 1)
                                on_these = [x for x in ["lon", "lat", "year", "month", "day", "depth", "observation"] if x in df_all.columns]
                                df_all = df_all.merge(df_bottom, how="left", on=on_these)
                                # if bottom is nan, set to 0
                                df_all = df_all.assign(bottom = lambda x: x.bottom.fillna(0))

                                # if it exists, coerce year to int

                            grouping = copy.deepcopy(point_time_res)
                            grouping.append("lon")
                            grouping.append("lat")
                            grouping.append("depth")
                            grouping = [x for x in grouping if x in df_all.columns]
                            grouping = list(set(grouping))
                            df_all = df_all.dropna().reset_index(drop=True)
                            df_all = df_all.groupby(grouping).mean().reset_index()

                            if session_info["out_dir"] != "":
                                out = f"{session_info['out_dir']}/matched/point/{layer}/{variable}/{source}_{layer}_{variable}.csv"
                            else:
                                out = f"matched/point/{layer}/{variable}/{source}_{layer}_{variable}.csv"

                            # create directory for out if it does not exists
                            if not os.path.exists(os.path.dirname(out)):
                                os.makedirs(os.path.dirname(out))
                            out1 = out.replace(os.path.basename(out), "paths.csv")
                            pd.DataFrame({"path": paths}).to_csv(out1, index=False)
                            if lon_lim is not None:
                                df_all = df_all.query(
                                    f"lon > {lon_lim[0]} and lon < {lon_lim[1]}"
                                )
                            if lat_lim is not None:
                                df_all = df_all.query(
                                    f"lat > {lat_lim[0]} and lat < {lat_lim[1]}"
                                )


                            if len(df_all) > 0:

                                if "year" not in point_time_res:
                                    try:
                                        df_all = df_all.drop(columns="year")
                                    except:
                                        pass
                                if "day" not in point_time_res:
                                    try:
                                        df_all = df_all.drop(columns="day")
                                    except:
                                        pass
                                if "month" not in point_time_res:
                                    try:
                                        df_all = df_all.drop(columns="month")
                                    except:
                                        pass
                                df_all.to_csv(out, index=False)

                                out1 = out.replace(
                                    os.path.basename(out), "matchup_dict.pkl"
                                )
                                # read in the adhoc dict in mm_match

                                point_start = -5000
                                point_end = 10000
                                try:
                                    point_start = definitions[variable].point_start
                                    point_end = definitions[variable].point_end
                                except:
                                    pass

                                min_year = session_info["min_year"]
                                max_year = session_info["max_year"]

                                if point_start > min_year:
                                    min_year = point_start
                                if point_end < max_year:
                                    max_year = point_end

                                the_dict = {
                                    "start": min_year,
                                    "end": max_year,
                                    "point_time_res": point_time_res,
                                    "model_variable": model_variable,
                                }
                                # remove the adhoc dict
                                # write to pickle
                                with open(out1, "wb") as f:
                                    pickle.dump(the_dict, f)

                                if session_info["out_dir"] != "":
                                    out_unit = f"{session_info['out_dir']}/matched/point/{layer}/{variable}/{source}_{layer}_{variable}_unit.csv"
                                else:
                                    out_unit = f"matched/point/{layer}/{variable}/{source}_{layer}_{variable}_unit.csv"
                                ds = nc.open_data(paths[0], checks=False)
                                ds_contents = ds.contents
                                model_variable = model_variable.split("+")[0]
                                ds_contents = ds_contents.query(
                                    "variable == @model_variable"
                                )
                                ds_contents.to_csv(out_unit, index=False)
                                return None
                            else:
                                print(f"No data for {variable}")
                                time.sleep(1)
                                return False

                    vv_variable = vv
                    if vv == "ph":
                        vv_variable = "pH"

                    if session_info["out_dir"] != "":
                        out = glob.glob(
                            session_info["out_dir"]
                            + "/"
                            + f"matched/point/all/{vv}/**_all_{vv}.csv"
                        )

                    else:
                        out = glob.glob(
                            f"matched/point/all/{vv}/**_all_{vv}.csv"
                        )

                    if len(out) > 0:
                        if session_info["overwrite"] is False:
                            continue

                    if vv_variable != "benbio":
                        print(
                                f"Matching up model {key} {vv_variable} with vertically resolved bottle and CDT {vv_variable}"
                            )
                    else:
                        print(
                                f"Matching up model benthic biomass with North Sea Benthos Survey data"
                            )

                    #try:
                    if True:
                        point_match(vv, ds_depths=ds_depths, df_times=df_times, layer=key)
                    # except:
                    #     pass

                    output_warnings = []
                    for ww in session_warnings:
                        if ww is not None:
                            if ww in output_warnings:
                                continue
                            if "CDO found more than one time variable" in ww:
                                continue
                            if "coordinates variable time" in ww:
                                continue
                            output_warnings.append(str(ww))

                    if len(output_warnings) > 0:
                        output_warnings = list(set(output_warnings))
                        print(f"Warnings for {vv_variable}")
                        for ww in output_warnings:
                            warnings.warn(message=ww)
                    # empty session warnings
        while len(session_warnings) > 0:
            session_warnings.pop()

    gridded_matchup(
        df_mapping=df_mapping,
        folder=sim_dir,
        var_choice=gridded,
        exclude=exclude,
        sim_start=sim_start,
        sim_end=sim_end,
        lon_lim=lon_lim,
        lat_lim=lat_lim,
        times_dict=times_dict
    )

    if len(session_info["end_messages"]) > 0:
        print("########################################")
        print("########################################")
        print("Important messages about matchups:")
        print("*" * 30)
        # write this info to a md report
        with open("matchup_report.md", "w") as f:
            f.write("# Matchup Report\n\n")
            f.write("Important messages about matchups:\n\n")
            for x in session_info["end_messages"]:
                f.write(f"- {x}\n")
        # convert to pdf
        os.system("pandoc matchup_report.md -o matchup_issues.pdf")

        for x in session_info["end_messages"]:
            print(x)
        print("########################################")
        print("########################################")

    # store definitions as a pickle
    ff = session_info["out_dir"] + "matched/definitions.pkl"
    if os.path.exists(ff):
        os.remove(ff)
    import dill

    dill.dump(definitions, file = open(ff, "wb"))
