import glob
import copy
import os
import warnings
import pickle
import pandas as pd
import time
import numpy as np
import nctoolkit as nc
import xarray as xr

from oceanval.fixers import tidy_warnings
from oceanval.utils import extension_of_directory, get_extent, is_latlon, get_resolution
from oceanval.session import session_info
from oceanval.parsers import Validator, definitions


def gridded_matchup(
    df_mapping=None,
    folder=None,
    var_choice=None,
    exclude=None,
    sim_start=None,
    sim_end=None,
    lon_lim=None,
    lat_lim=None,
    times_dict=None
):
    """
    Function to create gridded matchups for a given set of variables

    Parameters
    ----------
    df_mapping : pandas.DataFrame
        DataFrame containing the mapping between model variables and gridded observations
    folder : str
        Path to folder containing model data
    var_choice : list
        List of variables to create matchups for
    exclude : list
        List of strings to exclude from the file search
    sim_start : int
        Start year for model simulations
    sim_end : int
        End year for model simulations
    lon_lim : list
        Longitude limits for subsetting
    lat_lim : list
        Latitude limits for subsetting
    times_dict : dict
        Dictionary with file paths as keys and corresponding time DataFrames as values
    Returns
    -------
    None

    """


    all_df = df_mapping
    # if model_variable is None remove from all_df
    good_model_vars = [x for x in all_df.model_variable if x is not None]

    all_df = all_df.query("model_variable in @good_model_vars").reset_index(drop=True)

    all_df = all_df.dropna()

    vars = []
    for x in definitions.keys:
        if definitions[x].gridded:
            vars.append(x)

    vars = [x for x in vars if x in var_choice]
    vars.sort()

    if len(vars) > 0:
        # first up, do the top

        mapping = dict()

        for vv in vars:
            vertical_gridded = definitions[vv].vertical_gridded
            climatology = definitions[vv].climatology
                # if global is not selected, stop
            # a dictionary for summarizing things
            var_dict = {}
            out_dir = session_info["out_dir"]
            out = glob.glob(
                out_dir + f"matched/gridded/{vv}/*_{vv}_surface.nc"
            )
            if len(out) > 0:
                if session_info["overwrite"] is False:
                    continue
            out_vertical = glob.glob(
                out_dir + f"matched/gridded/{vv}/*_{vv}_vertical.nc"
            )
            if len(out_vertical) > 0:
                if session_info["overwrite"] is False:
                    continue
            # figure out the data source
            #
            # check if this directory is empty
            dir_var = definitions[vv].gridded_dir 

            vv_source = definitions[vv].gridded_source

            #
            vv_name = definitions[vv].long_name

            print(
                f"Matching up surface {vv_name} with {vv_source.upper()} gridded data"
            )
            print("**********************")
            df = df_mapping.query("variable == @vv").reset_index(drop=True)

            if len(df) == 0:
                continue

            mapping[vv] = list(df.query("variable == @vv").model_variable)[0]

            selection = []
            try:
                selection += mapping[vv].split("+")
            except:
                selection = selection

            patterns = set(df.pattern)
            if len(patterns) > 1:
                raise ValueError(
                    "Something strange going on in the string patterns. Unable to handle this. Bug fix time!"
                )
            pattern = list(patterns)[0]

            final_extension = extension_of_directory(folder)
            paths = glob.glob(folder + final_extension + pattern)

            for exc in exclude:
                paths = [
                    x for x in paths if f"{exc}" not in os.path.basename(x)
                ]

            new_paths = []
            # set up model_grid if it doesn't exist

            if not os.path.exists(
                session_info["out_dir"] + "matched/model_grid.csv"
            ):
                ds_grid = nc.open_data(paths[0], checks=False)
                ds_grid.subset(variables=selection[0], time=0)
                ds_grid.top()
                ds_grid.as_missing(0)
                df_grid = ds_grid.to_dataframe().reset_index().dropna()
                columns = [
                    x for x in df_grid.columns if "lon" in x or "lat" in x
                ]
                df_grid = df_grid.loc[:, columns].drop_duplicates()
                if not os.path.exists(session_info["out_dir"] + "matched"):
                    os.makedirs("matched")
                df_grid.to_csv(
                    session_info["out_dir"] + "matched/model_grid.csv",
                    index=False,
                )

            all_years = []
            for ff in paths:
                all_years += list(times_dict[ff].year)

            all_years = list(set(all_years))
            n_years = len(all_years)

            sim_years = range(sim_start, sim_end + 1)
            sim_years = [x for x in all_years if x in sim_years]
            min_year = min(all_years)
            max_year = max(all_years)

            if len(sim_years) == 0:
                # specific error for glodap
                session_info["end_messages"] += [f"No simulation years found for {vv}. Please check start and end args!"]
                return None
            # now simplify paths, so that only the relevant years are used
            new_paths = []
            year_options = list(
                set(
                    pd.concat([x for x in times_dict.values()])
                    .loc[:, ["year", "month"]]
                    .drop_duplicates()
                    .groupby("year")
                    .size()
                    # must be at least 12
                    .pipe(lambda x: x[x >= 12])
                    .reset_index()
                    .year
                )
            )
            old_years = sim_years
            n_years = len(sim_years)
            sim_years = [x for x in sim_years if x in year_options]
            if n_years > 0:
                if len(sim_years) == 0:
                    raise ValueError(
                        f"No years in common between model and observation for {vv}. Please check start and end args!"
                    )
            month_sel = range(1, 13)
            if len(sim_years) == 0:
                sim_years = old_years
                month_sel = list(
                    set(
                        pd.concat([x for x in times_dict.values()])
                        .loc[:, ["year", "month"]]
                        .drop_duplicates()
                        .month
                    )
                )

            for ff in paths:
                if len([x for x in times_dict[ff].year if x in sim_years]) > 0:
                    new_paths.append(ff)

            paths = list(set(new_paths))
            paths.sort()

            var_dict["clim_years"] = [min(sim_years), max(sim_years)]

            # get the number of paths

            n_paths = len(paths)

            with warnings.catch_warnings(record=True) as w:

                new_paths = copy.deepcopy(paths)
                if vv_source == "glodap":
                    for ff in paths:
                        ff_years = times_dict[ff].year
                        if (
                            len([x for x in ff_years if x in range(1971, 2015)])
                            == 0
                        ):
                            new_paths.remove(ff)
                    paths = new_paths

                ds_model = nc.open_data(paths, checks=False)

                ds_model.subset(variables=selection)
                if vertical_gridded is False:
                    ds_model.cdo_command("topvalue")
                ds_model.as_missing(0)
                ds_model.subset(years=sim_years)
                ds_model.tmean(
                    ["year", "month"], align="left"
                )

                if vv_source == "glodap":
                    ds_model.merge("time")
                    ds_model.tmean(align="left")

                # the code below needs to be simplifed
                # essentially anything with a + in the mapping should be split out
                # and then the command should be run for each variable

                var_unit = None
                ignore_later = []
                for vv in list(df.variable):
                    if "+" in mapping[vv]:
                        command = f"-aexpr,{vv}=" + mapping[vv]
                        ds_model.cdo_command(command)
                        drop_these = mapping[vv].split("+")
                        ds_contents = ds_model.contents
                        ds_contents = ds_contents.query(
                            "variable in @drop_these"
                        )
                        var_unit = ds_contents.unit[0]
                        ds_model.drop(variables=drop_these)
                        ignore_later.append(vv)

                        ds_model.run()
                        for key in mapping:
                            if key not in ignore_later:
                                if mapping[key] in ds_model.variables:
                                    ds_model.rename({mapping[key]: key})
                        if var_unit is not None:
                            ds_model.set_units(
                                {vv: var_unit}
                            )

                        ds_model.run()
                        ds_model.tmean(["year", "month"], align="left")
                        ds_model.merge("time")
                        ds_model.subset(years=sim_years)
                        ds_model.run()

            tidy_warnings(w)

            # figure out the start and end year
            with warnings.catch_warnings(record=True) as w:
                start_year = min(ds_model.years)
                end_year = max(ds_model.years)

                # Read in the monthly observational data
                if dir_var.endswith(".nc"):
                    vv_file = dir_var
                else:
                    vv_file = nc.create_ensemble(dir_var)
                    vv_file = [x for x in vv_file if "annual" not in x]

                ds_obs = nc.open_data(
                    vv_file,
                    checks=False,
                )
                bad_clim = False

                try:
                    min_obs_year = min(ds_obs.years)
                    max_obs_year = max(ds_obs.years)
                    if climatology is True:
                        if (min_obs_year < max_obs_year):
                            bad_clim = True
                    if climatology is False:
                        if (min_obs_year < max_obs_year):
                            if sim_start > max_obs_year or sim_end < min_obs_year:
                                session_info["end_messages"] += [f"No observation years found for gridded {vv}. Please check start and end args!"]
                                return None
                    if climatology is False:
                        ds_obs.subset(years=sim_years)
                    ds_obs.tmean(["year", "month"], align="left")
                    ds_obs.merge("time")
                    ds_obs.tmean(["year", "month"], align="left")
                except:
                    pass

                if climatology is False:
                    year_sel = [x for x in ds_model.years if x in ds_obs.years]
                    sim_years = year_sel
                    min_year = min(year_sel)
                    max_year = max(year_sel)
                    ds_obs.subset(years=year_sel)
                    ds_model.subset(years=year_sel)

                obs_unit_multiplier = definitions[vv].obs_multiplier_gridded
                if obs_unit_multiplier != 1:
                    ds_obs *  obs_unit_multiplier
            
                if bad_clim:
                    raise ValueError(f"Observational data for {vv} appears to not be a climatology, but the climatology argument is set to True. Please fix this!") 

                if len(month_sel) < 12:
                    try:
                        months = ds.months
                        if len(months) > 1:
                            ds_obs.subset(months=month_sel)
                    except:
                        pass
                
                if definitions[vv].obs_var != "auto":
                    ds_obs.subset(variables=definitions[vv].obs_var)
                    ds_obs.run()

                obs_years = ds_obs.years
                min_obs_year = min(obs_years)
                max_obs_year = max(obs_years)

            tidy_warnings(w)

            with warnings.catch_warnings(record=True) as w:
                if len(obs_years) == 1:
                    ds_model.merge("time")
                    ds_model.tmean("month", align="left")
                else:
                    ds_model.merge("time")
                    ds_model.tmean(["year", "month"], align="left")

                if len(ds_obs) > 1:
                    ds_obs.merge("time")
                    ds_obs.run()

                lons = session_info["lon_lim"]
                lats = session_info["lat_lim"]

                # # figure out the lon/lat extent in the model

                lon_min_model = lons[0]
                lon_max_model = lons[1]
                lat_min_model = lats[0]
                lat_max_model = lats[1]

                # now do the same for the obs
                extent = get_extent(ds_obs[0])

                lon_max = extent[1]
                lon_min = extent[0]
                lat_max = extent[3]
                lat_min = extent[2]

                extent = get_extent(ds_model[0])
                lon_max_model = extent[1]
                lon_min_model = extent[0]
                lat_max_model = extent[3]
                lat_min_model = extent[2]   

                lon_min = max(lon_min, lon_min_model)
                lon_max = min(lon_max, lon_max_model)
                lat_min = max(lat_min, lat_min_model)
                lat_max = min(lat_max, lat_max_model)

                if lon_min < -180:
                    lon_min = -180
                if lon_max > 180:
                    lon_max = 180
                if lat_min < -90:
                    lat_min = -90
                if lat_max > 90:
                    lat_max = 90
                # coerce to floats
                lon_min = float(lon_min)
                lon_max = float(lon_max)
                lat_min = float(lat_min)
                lat_max = float(lat_max)

                lons = [lon_min, lon_max]
                lats = [lat_min, lat_max]


                n1 = ds_obs.contents.npoints[0]
                n2 = ds_model.contents.npoints[0]

                if n1 >= n2:
                    regridding = "obs_to_model"
                    # ds_obs.regrid(ds_model, method="bil")
                else:
                    regridding = "model_to_obs"
                    # ds_model.regrid(ds_obs, method="bil")

                ds_obs.rename({ds_obs.variables[0]: "observation"})
                ds_model.merge("time")
                ds_model.rename({ds_model.variables[0]: "model"})
                ds_model.run()
                ds_obs.run()

                # it is possible the years do not overlap, e.g. with satellite Chl
                if len(ds_model.times) > 12:
                    years1 = ds_model.years
                    years2 = ds_obs.years
                    all_years = [x for x in years1 if x in years2]
                    if len(all_years) != len(years1):
                        if len(all_years) != len(years2):
                            ds_obs.subset(years=all_years)
                            ds_model.subset(years=all_years)
                            ds_obs.run()
                            ds_model.run()
                if len(ds_obs) > 1:
                    ds_obs.merge("time")

                ds_obs.run()
                ds_model.run()

                if vertical_gridded is False:
                    ds_obs.cdo_command("topvalue")
                try:
                    n_times = len(ds_obs.times)
                except:
                    n_times = 1
                try:
                    n_years = len(ds_obs.years)
                except:
                    n_years = 1

                ds_obs.run()
                ds_model.run()
                ds2 = ds_model.copy()
                if len(ds_model.times) == 12:
                    ds_model.set_year(2000)

                if len(ds_model.times) > 12:
                    # at this point, we need to identify the years that are common to both
                    ds_times = ds_model.times
                    ds_years = [x.year for x in ds_times]
                    ds_months = [x.month for x in ds_times]

                    df_surface = pd.DataFrame(
                        {"year": ds_years, "month": ds_months}
                    )

                    ds_times = ds_obs.times
                    ds_years = [x.year for x in ds_times]
                    ds_months = [x.month for x in ds_times]
                    df_obs = pd.DataFrame(
                        {"year": ds_years, "month": ds_months}
                    )
                    sel_years = list(
                        df_surface.merge(df_obs)
                        .groupby("year")
                        .count()
                        # only 12
                        .query("month == 12")
                        .reset_index()
                        .year.values
                    )
                    ds_model.subset(years=sel_years)
                    if n_years > 1: 
                        ds_obs.subset(years=sel_years)

                if len(ds_model.times) < 12:
                    sel_months = list(set(ds_model.months))
                    sel_months.sort()
                    if n_times > 1: 
                        ds_obs.subset(months=sel_months)

                # now do the surface
                ds_model_surface = ds_model.copy()
                if vertical_gridded:
                    ds_model_surface.cdo_command("topvalue")
                ds_obs_surface = ds_obs.copy()
                if vertical_gridded:
                    ds_obs_surface.cdo_command("topvalue")
                if regridding == "obs_to_model":
                    ds_obs_surface.regrid(ds_model_surface, method="bil")
                else:
                    ds_model_surface.regrid(ds_obs_surface, method="bil")

                ds_obs_surface.append(ds_model_surface)

                if len(ds_model_surface.times) > 12:
                    ds_obs_surface.merge("variable", match=["year", "month"])
                else:
                    ds_obs_surface.merge("variable", match="month")

                ds_obs_surface.set_fill(-9999)
                ds_mask = ds_obs_surface.copy()
                ds_mask.assign( mask_these=lambda x: -1e30 * ((isnan(x.observation) + isnan(x.model)) > 0), drop=True,)
                ds_mask.as_missing([-1e40, -1e20])
                ds_mask.run()
                ds_obs_surface + ds_mask

                out_file = (
                    session_info["out_dir"]
                    + f"matched/gridded/{vv}/{vv_source}_{vv}_surface.nc"
                )
                out_file_vertical = (
                    session_info["out_dir"]
                    + f"matched/gridded/{vv}/{vv_source}_{vv}_vertical.nc"
                )

                # check directory exists for out_file
                if not os.path.exists(os.path.dirname(out_file)):
                    os.makedirs(os.path.dirname(out_file))
                # remove the file if it exists
                if os.path.exists(out_file):
                    os.remove(out_file)
                ds_obs_surface.set_precision("F32")
                ds_model_surface = ds_obs_surface.copy()

                if lon_lim is not None and lat_lim is not None:
                    ds_model_surface.subset(lon=lon_lim, lat=lat_lim)

                ds_model_surface.run()
                if (
                    list(
                        ds_model_surface.contents.query(
                            "variable == 'model'"
                        ).long_name
                    )[0]
                    is None
                ):
                    ds_model_surface.set_longnames({"model": f"Model {vv_name}"})

                regrid_later = False
                #if is_latlon(ds_model_surface[0]) is False:
                #    lons = session_info["lon_lim"]
                #    lats = session_info["lat_lim"]
                #    resolution = get_resolution(ds_model_surface[0])
                #    lon_res = resolution[0]
                #    lat_res = resolution[1]
                #    ds_model_surface.to_latlon(
                #        lon=lons, lat=lats, res=[lon_res, lat_res], method="bil"
                #    )

                # unit may need some fiddling
                out1 = out_file.replace(
                    os.path.basename(out_file), "matchup_dict.pkl"
                )
                the_dict = {"start": min_year, "end": max_year}
                # write to pickle
                with open(out1, "wb") as f:
                    pickle.dump(the_dict, f)

                ds_model_surface.subset(lon=lons, lat=lats)
                ds_model_surface.to_nc(out_file, zip=True, overwrite=True)
                out_file = out_file.replace(".nc", "_definitions.pkl")
                # save definitions
                with open(out_file, "wb") as f:
                    pickle.dump(definitions, f)


                if vertical_gridded:

                    if vertical_gridded is True:
                        levels = ds_obs.levels
                        if session_info["ds_depths"] != "z_level":
                            if os.path.exists("foo2.nc"):
                                os.remove("foo2.nc")
                            ds_model.to_nc("foo2.nc", zip=True)
                            ds_model.vertical_interp(levels, thickness = session_info["ds_thickness"]) 
                        else:
                            ds_model.vertical_interp(levels , fixed = True)

                    if regridding == "obs_to_model":
                        ds_obs.regrid(ds_model, method="bil")
                    else:
                        ds_model.regrid(ds_obs, method="bil")
                    ds_obs.append(ds_model)

                    if len(ds_model.times) > 12:
                        ds_obs.merge("variable", match=["year", "month"])
                    else:
                        ds_obs.merge("variable", match="month")

                    ds_obs.set_fill(-9999)
                    ds_mask = ds_obs.copy()
                    ds_mask.assign( mask_these=lambda x: -1e30 * ((isnan(x.observation) + isnan(x.model)) > 0), drop=True,)
                    ds_mask.as_missing([-1e40, -1e20])
                    ds_mask.run()
                    ds_obs + ds_mask

                    out_file = (
                        session_info["out_dir"]
                        + f"matched/gridded/{vv}/{vv_source}_{vv}_surface.nc"
                    )

                    # check directory exists for out_file
                    if not os.path.exists(os.path.dirname(out_file_vertical)):
                        os.makedirs(os.path.dirname(out_file_vertical))
                    # remove the file if it exists
                    if os.path.exists(out_file_vertical):
                        os.remove(out_file_vertical)
                    ds_obs.set_precision("F32")
                    ds_model = ds_obs.copy()

                    if lon_lim is not None and lat_lim is not None:
                        ds_model.subset(lon=lon_lim, lat=lat_lim)

                    ds_model.run()
                    if (
                        list(
                            ds_model.contents.query(
                                "variable == 'model'"
                            ).long_name
                        )[0]
                        is None
                    ):
                        ds_model.set_longnames({"model": f"Model {vv_name}"})

                    regrid_later = False
                    #if is_latlon(ds_model[0]) is False:
                    #    lons = session_info["lon_lim"]
                    #    lats = session_info["lat_lim"]
                    #    resolution = get_resolution(ds_model[0])
                    #    lon_res = resolution[0]
                    #    lat_res = resolution[1]
                    #    ds_model.to_latlon(
                    #        lon=lons, lat=lats, res=[lon_res, lat_res], method="bil"
                    #    )

                    # unit may need some fiddling
                    out1 = out_file.replace(
                        os.path.basename(out_file), "matchup_dict.pkl"
                    )
                    the_dict = {"start": min_year, "end": max_year}
                    # write to pickle
                    with open(out1, "wb") as f:
                        pickle.dump(the_dict, f)

                    ds_model.subset(lon=lons, lat=lats) 
                    ds_model.to_nc(out_file_vertical, zip=True, overwrite=True)
                out_file = out_file.replace(".nc", "_definitions.pkl")
                # save definitions
                with open(out_file, "wb") as f:
                    pickle.dump(definitions, f)

            tidy_warnings(w)

            out = (
                session_info["out_dir"]
                + f"matched/gridded/{vv}/{vv}_summary.pkl"
            )
            if not os.path.exists(os.path.dirname(out)):
                os.makedirs(os.path.dirname(out))
            var_dict["clim_years"] = [min(sim_years), max(sim_years)]
            with open(out, "wb") as f:
                pickle.dump(var_dict, f)

        return None
