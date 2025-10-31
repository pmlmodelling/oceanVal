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

from ecoval.fixers import tidy_warnings
from ecoval.utils import extension_of_directory, get_extent, is_latlon, get_resolution
from ecoval.session import session_info


def gridded_matchup(
    df_mapping=None,
    folder=None,
    var_choice=None,
    exclude=None,
    sim_start=None,
    sim_end=None,
    domain="nws",
    lon_lim=None,
    lat_lim=None,
    times_dict=None,
    ds_thickness=None,
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
    start : int
        Start year for matchups
    sim_start : int
        Start year for model simulations
    sim_end : int
        End year for model simulations
    domain : str
        Domain to use for matchups. Either "NWS" or "global"
        This indicates whether the matchups use northwest European shelf data or global data
    ds_thickness : str or nctoolkit DataSet
        File path to thickness file

    """
    obs_dir = session_info["obs_dir"]

    all_df = df_mapping
    # if model_variable is None remove from all_df
    good_model_vars = [x for x in all_df.model_variable if x is not None]

    all_df = all_df.query("model_variable in @good_model_vars").reset_index(drop=True)

    all_df = all_df.dropna()

    vars = [
        "ammonium",
        "chlorophyll",
        "nitrate",
        "phosphate",
        "oxygen",
        "silicate",
        "salinity",
        "temperature",
        "co2flux",
        "pco2",
        "ph",
        "alkalinity",
        "spm",
        "kd",
    ]
    vars = [x for x in vars if x in var_choice]
    vars.sort()

    if len(vars) > 0:
        # first up, do the top

        mapping = dict()


        for vv in vars:
                # if global is not selected, stop
            # a dictionary for summarizing things
            var_dict = {}
            out_dir = session_info["out_dir"]
            out = glob.glob(
                out_dir + f"matched/gridded/{domain}/{vv}/*_{vv}_surface.nc"
            )
            if len(out) > 0:
                if session_info["overwrite"] is False:
                    continue
            # figure out the data source
            #
            dir_var = f"{obs_dir}/gridded/user/{vv}"
            # check if this directory is empty
            if len(glob.glob(dir_var + "/*")) == 0:
                dir_var = f"{obs_dir}/gridded/{domain}/{vv}"
                dirs = glob.glob(f"{obs_dir}/gridded/**/{vv}", recursive=True)
                if len(dirs) == 0:
                    raise ValueError(f"No data found for {vv}")
                # get directory names for dirs
                dir_names = dirs

                non_globals = [
                    x for x in dir_names if "global" not in x.split("/")[-2]
                ]
                non_globals = [x for x in dir_names if domain in x.split("/")[-2]]
                if len(non_globals) > 1:
                    raise ValueError(
                        f"Multiple directories found for {vv}. Please specify the correct directory"
                    )

                if len(non_globals) == 0:
                    dir_var = [x for x in dir_names if "global" in x][0]
                else:
                    dir_var = non_globals[0]

            try:
                vv_source = [
                    os.path.basename(x).replace(".txt", "")
                    for x in glob.glob(dir_var + "/*")
                    if ".txt" in x
                ][0]
            except:
                continue

            if vv in ["pco2",  "temperature"]:
                vv_file = nc.create_ensemble(dir_var)
                vv_file = [x for x in vv_file if "annual" not in x]
                ds_obs = nc.open_data(
                    vv_file,
                    checks=False,
                )
                min_obs_year = min(ds_obs.years)
                max_obs_year = max(ds_obs.years)
                if sim_start > max_obs_year or sim_end < min_obs_year:
                    session_info["end_messages"] += [f"No observation years found for gridded {vv}. Please check start and end args!"]
                    return None
            #
            vv_name = vv
            if vv == "co2flux":
                vv_name = "air-sea CO2 flux"
            if vv == "ph":
                vv_name = "pH"

            print(
                f"Matching up surface {vv_name} with {vv_source.upper()} gridded data"
            )
            print("**********************")
            df = df_mapping.query("variable == @vv").reset_index(drop=True)
            if len(df) > 0:
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
                    ds_grid.cdo_command("topvalue")
                    ds_grid.as_missing(0)
                    if max(ds_grid.contents.npoints) == 111375:
                        amm7_out = session_info["out_dir"] + "matched/amm7.txt"
                        # create empty file
                        with open(amm7_out, "w") as f:
                            f.write("")

                        ff_grid = f"{obs_dir}/amm7_val_subdomains.nc"
                        ds_grid.cdo_command(f"setgrid,{ff_grid}")
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

                    ds_surface = nc.open_data(paths, checks=False)

                    ds_surface.subset(variables=selection)
                    ds_surface.cdo_command("topvalue")
                    ds_surface.as_missing(0)
                    ds_surface.tmean(
                        ["year", "month"], align="left"
                    )

                    if vv_source == "glodap":
                        ds_surface.merge("time")
                        ds_surface.tmean(align="left")

                    # the code below needs to be simplifed
                    # essentially anything with a + in the mapping should be split out
                    # and then the command should be run for each variable

                    var_unit = None
                    ignore_later = []
                    for vv in list(df.variable):
                        if "+" in mapping[vv]:
                            command = f"-aexpr,{vv}=" + mapping[vv]
                            ds_surface.cdo_command(command)
                            drop_these = mapping[vv].split("+")
                            ds_contents = ds_surface.contents
                            ds_contents = ds_contents.query(
                                "variable in @drop_these"
                            )
                            var_unit = ds_contents.unit[0]
                            ds_surface.drop(variables=drop_these)
                            ignore_later.append(vv)

                            ds_surface.run()
                            for key in mapping:
                                if key not in ignore_later:
                                    if mapping[key] in ds_surface.variables:
                                        ds_surface.rename({mapping[key]: key})
                            if "chlorophyll" in list(df.variable):
                                if var_unit is not None:
                                    ds_surface.set_units(
                                        {"chlorophyll": var_unit}
                                    )
                                    ds_surface.set_longnames(
                                        {
                                            "chlorophyll": "Total chlorophyll concentration"
                                        }
                                    )

                            ds_surface.run()
                            ds_surface.tmean(["year", "month"], align="left")
                            ds_surface.merge("time")
                            ds_surface.subset(years=sim_years)
                            ds_surface.run()

                tidy_warnings(w)

                # figure out the start and end year
                with warnings.catch_warnings(record=True) as w:
                    start_year = min(ds_surface.years)
                    end_year = max(ds_surface.years)

                    # Read in the monthly observational data
                    vv_file = nc.create_ensemble(dir_var)
                    vv_file = [x for x in vv_file if "annual" not in x]

                    ds_obs = nc.open_data(
                        vv_file,
                        checks=False,
                    )
                    if vv not in ["alkalinity", "ph"]:
                        ds_obs.subset(months=month_sel)

                    if vv_source == "occci" and vv == "chlorophyll":
                        ds_obs.subset(variable="chlor_a")
                        ds_obs.subset(years=range(start_year, end_year + 1))
                        ds_obs.run()
                    if vv_source == "occci" and vv == "kd":
                        ds_obs.subset(variable="kd_490")
                        ds_obs.subset(years=range(start_year, end_year + 1))
                        ds_obs.run()

                    obs_years = ds_obs.years
                    min_obs_year = min(obs_years)
                    max_obs_year = max(obs_years)

                tidy_warnings(w)

                with warnings.catch_warnings(record=True) as w:
                    if len(obs_years) == 1:
                        ds_surface.merge("time")
                        ds_surface.tmean("month", align="left")
                    else:
                        ds_surface.merge("time")
                        ds_surface.tmean(["year", "month"], align="left")

                    if max(ds_surface.contents.npoints) == 111375:
                        try:
                            ds_surface.fix_amm7_grid()
                        except:
                            pass
                        ds_surface.subset(lon=[-19, 9], lat=[41, 64.3])

                    if vv in [ "pco2"]:
                        ds_obs.run()
                        if (
                            len([x for x in ds_obs.years if x in ds_surface.years])
                            == 0
                        ):
                            session_info["end_messages"] += [
                                f"Unable to create matchup for gridded surface {vv}. There were no years in common between model and observation. The observational years are {min_obs_year} to {max_obs_year}."
                            ]
                            print(
                                f"No years in common between model and observation for gridded surface {vv}"
                            )
                            continue
                        ds_obs.subset(years=sim_years)
                        ds_obs.merge("time")
                        ds_obs.tmean("month", align="left")
                        ds_surface.tmean("month", align="left")

                    if vv in ["temperature"]:
                        ds_obs.subset(years=sim_years)
                        ds_obs.tmean(["year", "month"], align="left")
                        ds_obs.merge("time")
                        ds_obs.tmean(["year", "month"], align="left")

                    if vv in ["salinity"] and domain not in ["nws", "europe"]:
                        ds_surface.cdo_command("topvalue")
                        sub_years = [
                            x for x in ds_surface.years if x in ds_obs.years
                        ]
                        ds_obs.subset(years=sub_years)
                        ds_surface.subset(years=sub_years)
                        ds_obs.merge("time")
                        ds_obs.tmean("month")
                        ds_surface.merge("time")
                        ds_surface.tmean("month", align="left")
                        #ds_obs_annual.subset(years=sub_years)
                        #ds_obs_annual.tmean(align="left")
                    if vv in ["chlorophyll"] and domain not in ["nws", "europe"]:
                        ds_obs.top()
                        sub_years = [
                            x for x in ds_surface.years if x in ds_obs.years
                        ]
                        ds_obs.subset(years=sub_years)
                        ds_surface.subset(years=sub_years)
                        ds_obs.merge("time")
                        ds_obs.tmean("month")
                        ds_surface.merge("time")
                        ds_surface.tmean("month", align="left")

                    if vv not in [ "temperature"]:
                        if len(ds_obs.times) > 12:
                            ds_obs.subset(years=sim_years)

                    if vv_source == "occci" and vv == "chlor_a":
                        ds_obs.subset(variable="chlor_a")
                    if vv_source == "occci" and vv == "kd":
                        ds_obs.subset(variable="kd_490")

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

                    if domain != "global":
                        ds_surface.subset(lon=lons, lat=lats)
                        ds_obs.subset(lon=lons, lat=lats)

                    if domain == "global":
                        obs_extent = get_extent(ds_obs[0])
                        lon_min = max(session_info["lon_lim"][0], obs_extent[0])
                        lon_max = min(session_info["lon_lim"][1], obs_extent[1])
                        lat_min = max(session_info["lat_lim"][0], obs_extent[2])
                        lat_max = min(session_info["lat_lim"][1], obs_extent[3])

                        # make sure lon_min is greater than -180
                        if lon_min < -180:
                            lon_min = -180
                        if lon_max > 180:
                            lon_max = 180
                        if lat_min < -90:
                            lat_min = -90
                        if lat_max > 90:
                            lat_max = 90

                        lons = [lon_min, lon_max]
                        lats = [lat_min, lat_max]
                        ds_surface.subset(lon=lons, lat=lats)
                        ds_obs.subset(lon=lons, lat=lats)

                    n1 = ds_obs.contents.npoints[0]
                    n2 = ds_surface.contents.npoints[0]

                    if n1 >= n2:
                        ds_obs.regrid(ds_surface, method="bil")
                    else:
                        ds_surface.regrid(ds_obs, method="bil")

                    ds_obs.rename({ds_obs.variables[0]: "observation"})
                    ds_surface.merge("time")
                    ds_surface.rename({ds_surface.variables[0]: "model"})
                    ds_surface.run()
                    ds_obs.run()

                    # it is possible the years do not overlap, e.g. with satellite Chl
                    if len(ds_surface.times) > 12:
                        years1 = ds_surface.years
                        years2 = ds_obs.years
                        all_years = [x for x in years1 if x in years2]
                        if len(all_years) != len(years1):
                            if len(all_years) != len(years2):
                                ds_obs.subset(years=all_years)
                                ds_surface.subset(years=all_years)
                                ds_obs.run()
                                ds_surface.run()
                    if len(ds_obs) > 1:
                        ds_obs.merge("time")

                    ds_obs.run()
                    ds_surface.run()

                    ds_obs.top()

                    if vv_source == "occci":
                        years = [x for x in ds_obs.years if x in ds_surface.years]
                        years = list(set(years))

                        ds_obs.subset(years=years)
                        ds_obs.tmean(["year", "month"])
                        ds_obs.merge("time")
                        ds_obs.tmean(["year", "month"])
                        ds_surface.subset(years=years)
                        ds_surface.tmean(["year", "month"])

                    ds_obs.run()
                    ds_surface.run()
                    ds2 = ds_surface.copy()
                    if len(ds_surface.times) == 12:
                        ds_surface.set_year(2000)

                    if len(ds_surface.times) > 12:
                        # at this point, we need to identify the years that are common to both
                        ds_times = ds_surface.times
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
                        ds_surface.subset(years=sel_years)
                        if vv not in ["alkalinity", "ph"]:
                            ds_obs.subset(years=sel_years)

                    if len(ds_surface.times) < 12:
                        sel_months = list(set(ds_surface.months))
                        sel_months.sort()
                        if vv not in ["alkalinity", "ph"]:
                            ds_obs.subset(months=sel_months)

                    ds_obs.append(ds_surface)

                    if len(ds_surface.times) > 12:
                        ds_obs.merge("variable", match=["year", "month"])
                    else:
                        ds_obs.merge("variable", match="month")
                    ds_obs.nco_command(
                        f"ncatted -O -a start_year,global,o,c,{start_year}"
                    )
                    ds_obs.nco_command(
                        f"ncatted -O -a end_year,global,o,c,{end_year}"
                    )
                    ds_obs.set_fill(-9999)
                    ds_mask = ds_obs.copy()
                    ds_mask.assign( mask_these=lambda x: -1e30 * ((isnan(x.observation) + isnan(x.model)) > 0), drop=True,)
                    ds_mask.as_missing([-1e40, -1e20])
                    ds_mask.run()
                    ds_obs + ds_mask

                    # fix the co2 flux units
                    if vv == "co2flux":
                        ds_obs.assign(model=lambda x: x.model * -0.365)
                        ds_obs.set_units({"model": "mol/m2/yr"})
                        ds_obs.set_units({"observation": "mol/m2/yr"})

                    # figure out if the temperature is in degrees C
                    if vv == "temperature":
                        if ds_obs.to_xarray().model.max() > 100:
                            ds_obs.assign(model=lambda x: x.model - 273.15)
                        if ds_obs.to_xarray().observation.max() > 100:
                            ds_obs.assign( observation=lambda x: x.observation - 273.15)
                        # set the units
                        ds_obs.set_units({"model": "degrees C"})
                        ds_obs.set_units({"observation": "degrees C"})
                    # # now, we need to exclude data outside the lon/lat range with data

                    out_file = (
                        session_info["out_dir"]
                        + f"matched/gridded/{domain}/{vv}/{vv_source}_{vv}_surface.nc"
                    )

                    # check directory exists for out_file
                    if not os.path.exists(os.path.dirname(out_file)):
                        os.makedirs(os.path.dirname(out_file))
                    # remove the file if it exists
                    if os.path.exists(out_file):
                        os.remove(out_file)
                    ds_obs.set_precision("F32")
                    if vv == "salinity" and domain not in ["nws" "europe"]:
                        ds_obs.tmean("month")
                    ds_surface = ds_obs.copy()

                    if lon_lim is not None and lat_lim is not None:
                        ds_surface.subset(lon=lon_lim, lat=lat_lim)

                    ds_surface.run()
                    if (
                        list(
                            ds_surface.contents.query(
                                "variable == 'model'"
                            ).long_name
                        )[0]
                        is None
                    ):
                        ds_surface.set_longnames({"model": f"Model {vv_name}"})

                    regrid_later = False
                    if is_latlon(ds_surface[0]) is False:
                        lons = session_info["lon_lim"]
                        lats = session_info["lat_lim"]
                        resolution = get_resolution(ds_surface[0])
                        lon_res = resolution[0]
                        lat_res = resolution[1]
                        ds_surface.to_latlon(
                            lon=lons, lat=lats, res=[lon_res, lat_res], method="bil"
                        )

                    # unit may need some fiddling
                    out1 = out_file.replace(
                        os.path.basename(out_file), "matchup_dict.pkl"
                    )
                    the_dict = {"start": min_year, "end": max_year}
                    # write to pickle
                    with open(out1, "wb") as f:
                        pickle.dump(the_dict, f)

                    ds_surface.to_nc(out_file, zip=True, overwrite=True)

                tidy_warnings(w)

                out = (
                    session_info["out_dir"]
                    + f"matched/gridded/{domain}/{vv}/{vv}_summary.pkl"
                )
                if not os.path.exists(os.path.dirname(out)):
                    os.makedirs(os.path.dirname(out))
                with open(out, "wb") as f:
                    pickle.dump(var_dict, f)

        return None
