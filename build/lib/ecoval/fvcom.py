import os
import nctoolkit as nc
import warnings
import xarray as xr
import numpy as np
import subprocess
import pandas as pd
from tqdm import tqdm
from ecoval.session import session_info


def bin_value(x, bin_res):
    return np.floor((x + bin_res / 2) / bin_res + 0.5) * bin_res - bin_res / 2


def extension_of_directory(starting_directory, exclude=[]):
    levels = session_info["levels_down"]

    new_directory = ""
    for i in range(levels):
        new_directory = new_directory + "/**"
    return new_directory + "/"


def is_latlon(ff):

    cdo_result = subprocess.run(
        f"cdo griddes {ff}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return "lonlat" in cdo_result.stdout.decode("utf-8")


def get_extent(ff):
    # add docstring
    """ "
    Get the extent of a netcdf file

    Parameters
    ----------
    ff : str
        The path to the netcdf file

    Returns
    -------
    extent : list
        A list of the form [lon_min, lon_max, lat_min, lat_max]

    """

    ds = nc.open_data(ff)
    ds.subset(variables=ds.variables[0])
    ds.top()
    ds.tmean()
    ds.as_missing(0)
    ds_xr = ds.to_xarray()
    lon_name = [x for x in ds_xr.coords if "lon" in x][0]
    lat_name = [x for x in ds_xr.coords if "lat" in x][0]

    df = ds_xr.to_dataframe().reset_index()
    df = ds.to_dataframe().dropna().reset_index()
    df = df.rename(columns={lon_name: "lon", lat_name: "lat"})
    df = df.dropna()
    max_lon = df["lon"].max()
    if max_lon > 180:
        new_lon = df["lon"].values % 360
        new_lon = new_lon - 180
        lon_min = float(new_lon.min())
        lon_max = float(new_lon.max())
    else:
        lon_min = float(df.lon.min())
        lon_max = float(df.lon.max())
    lat_min = float(df.lat.min())
    lat_max = float(df.lat.max())
    return [lon_min, lon_max, lat_min, lat_max]


def get_resolution(ff):
    ds = nc.open_data(ff, checks=False)
    var = ds.variables[0]
    ds = xr.open_dataset(ff)
    lon_name = [x for x in list(ds.coords) if "lon" in x][0]
    lat_name = [x for x in list(ds.coords) if "lat" in x][0]
    var_dims = ds[var].dims
    extent = get_extent(ff)
    if lon_name in var_dims:
        if lat_name in var_dims:
            n_lon = len(ds[lon_name])
            n_lat = len(ds[lat_name])
            lon_max = float(ds[lon_name].max())
            lon_min = float(ds[lon_name].min())
            lat_max = float(ds[lat_name].max())
            lat_min = float(ds[lat_name].min())
            lon_res = (lon_max - lon_min) / (n_lon - 1)
            lat_res = (lat_max - lat_min) / (n_lat - 1)
            return [lon_res, lat_res]
    else:
        # get the final two var_dims
        var_dims = var_dims[-2:]
        # lat should be the second
        n_lat = len(ds[var_dims[1]])
        n_lon = len(ds[var_dims[0]])
        lon_res = (extent[1] - extent[0]) / n_lon
        lat_res = (extent[3] - extent[2]) / n_lat
        return [lon_res, lat_res]


def fvcom_regrid(ff=None, new_grid=None, vv=None, lons=None, lats=None, res=None):
    # multiple = False
    # if len(vv) > 1:
    #     ds_all = nc.open_data()
    #     multiple = True
    # vars = vv
    # del vv
    # for vv in vars:
    with warnings.catch_warnings(record=True) as w:
        # print(vv)
        drop_variables = ["siglay", "siglev"]
        ds_xr = xr.open_dataset(ff, drop_variables=drop_variables, decode_times=False)
        long_name = ds_xr[vv].attrs["long_name"]
        ds1 = nc.from_xarray(ds_xr[vv])
        lon = ds1.to_xarray().lon.values
        lat = ds1.to_xarray().lat.values

        lon_min = float(lon.min())
        lon_max = float(lon.max())
        lat_min = float(lat.min())
        lat_max = float(lat.max())
        # handle longitudes over 180 appropriately
        if lon_min > 180:
            lon_min = lon_min - 360
        if lon_max > 180:
            lon_max = lon_max - 360
        extent = [lon_min, lon_max, lat_min, lat_max]
        session_info["extent"] = extent

        ds1.run()
        ds1.nco_command("ncks -d siglay,0,0")
        ds_xr = ds1.to_xarray()
        try:
            ds_xr = ds_xr.squeeze("siglay")
        except:
            pass
        ds1 = nc.from_xarray(ds_xr)
        ds1.subset(variable=vv)
        # ds1.tmean(align = "left")
        grid = pd.DataFrame({"lon": lon, "lat": lat})
        lon_max = grid["lon"].max()
        lon_min = grid["lon"].min()
        lat_max = grid["lat"].max()
        lat_min = grid["lat"].min()
        ds1.run()
        out_grid = nc.generate_grid.generate_grid(grid)
        nc.session.append_safe(out_grid)

        ds2 = ds1.copy()
        ds2.run()
        ds2.cdo_command(f"setgrid,{out_grid}")
        if lons is not None:
            ds2.to_latlon(lon=lons, lat=lats, res=res, method="nn")
        else:
            ds2.regrid(new_grid, method="nn")

        ds2.as_missing(0)
        ds2.run()
        df_mask = grid.assign(value=1)
        df_mask["lon"] = bin_value(df_mask["lon"], 0.25)
        df_mask["lat"] = bin_value(df_mask["lat"], 0.25)
        df_mask = df_mask.groupby(["lon", "lat"]).sum().reset_index()
        df_mask = df_mask.set_index(["lat", "lon"])
        ds_mask = nc.from_xarray(df_mask.to_xarray())
        os.system(f"cdo griddes {ds_mask[0]} > /tmp/mygrid")
        # open the text file text.txt and replace the string "generic" with "lonlat"
        with open("/tmp/mygrid", "r") as f:
            lines = f.readlines()

        # write line by line to /tmp/newgrid
        with open("/tmp/newgrid", "w") as f:
            for ll in lines:
                f.write(ll.replace("generic", "lonlat"))

        ds_mask.cdo_command(f"setgrid,/tmp/newgrid")
        # ds_mask.to_nc("/tmp/mask.nc")
        ds_mask.regrid(ds2, method="bil")
        # ds_mask.to_nc("/tmp/mask1.nc")
        ds_mask > 0
        # ds_mask.to_nc("/tmp/mask2.nc")
        os.remove("/tmp/mygrid")
        os.remove("/tmp/newgrid")
        ds_mask.as_missing(0)
        ds_mask.set_fill(-9999)
        ds2 * ds_mask
        ds2.set_longnames({ds2.variables[0]: long_name})
        ds2.subset(lon=[lon_min, lon_max], lat=[lat_min, lat_max])

        # if multiple is False:
        return ds2
    #     else:
    #         ds_all.append(ds2)
    # ds_all.merge("variables")
    # ds_all.run()
    # return ds_all


def fvcom_preprocess(
    variables=None, paths=None, lon_lim=None, lat_lim=None, res=0.05, out_dir=None
):
    """
    Preprocess FVCOM data for gridding and regridding.

    Parameters
    ----------
    variables : list
        List of variable names to process. This must be the names in the netCDF files.
    paths : list
        List of file paths to the FVCOM data files.
    lon_lim : list
        Minimum and maximum longitudes for regridding.
    lat_lim : list
        Minimum and maximum latitudes for regridding.
    res : list or float
        Resolution for regridding. This defaults to 0.05 degrees, which should be fine for point matchups.
    out_dir : str
        Output directory where processed data will be saved. If None, an error is raised.

    """

    # check if out_dir is None
    if out_dir is None:
        raise ValueError("out_dir must be specified")
    # check if out_dir exists
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    # make sure variables is a list
    if not isinstance(variables, list):
        variables = [variables]

    with warnings.catch_warnings(record=True) as w:
        # print(vv)
        ds_all = nc.open_data()
        for vv in variables:
            print(f"Processing variable: {vv}")
            ds_vv = nc.open_data()
            for ff in tqdm(paths):
                ds = xr.open_dataset(
                    ff, drop_variables=["siglay", "siglev"], decode_times=False
                )
                ds_variables = ds.data_vars
                if vv not in ds_variables:
                    continue
                ds2 = fvcom_regrid(
                    ff=ff, new_grid=None, vv=vv, lons=lon_lim, lats=lat_lim, res=res
                )
                ds_vv.append(ds2)
            ds_vv.merge("time")
            ds_all.append(ds_vv)
        ff_out = out_dir + "/" + f"fvcom_values.nc"
        if os.path.exists(ff_out):
            os.remove(ff_out)
        ds_all.merge("variables")
        ds_all.to_nc(ff_out, zip=True)
