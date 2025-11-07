import pandas as pd
import importlib
import re
import warnings
import calendar
import copy
import ecoval
ff  = "../../matched/definitions.pkl"
import pickle
with open(ff, "rb") as f:
    definitions = pickle.load(f)

import glob
import geopandas as gpd
import jellyfish
import nctoolkit as nc
nc.options(parallel=True)
import os
import pickle
import numpy as np
import xarray as xr
from IPython.display import Markdown as md_markdown
import cmocean as cm
from tqdm import tqdm
import hvplot.pandas
from plotnine import *
from IPython.core.interactiveshell import InteractiveShell
from ecoval.tidiers import tidy_info
InteractiveShell.ast_node_interactivity = "all"

try:
    lon_lim = the_lon_lim
    lat_lim = the_lat_lim
except:
    lon_lim = None
    lat_lim = None
if lon_lim is None:
    lon_lim = [-180, 180]
if lat_lim is None:
    lat_lim = [-90, 90]

try:
    concise = concise_value
except:
    concise = False

# from ecoval.tidiers import fix_basenay_paths
# in one line
#from ecoval.tidiers import fix_basename, fix_unit, fix_variable_name, df_display, tidy_summary_paths, md, md_basic
from ecoval.tidiers import fix_basename, fix_unit, df_display, tidy_summary_paths, md, md_basic

warnings.filterwarnings('ignore')

%load_ext rpy2.ipython

test_status = the_test_status


i_figure = 1
i_table = 1
stamp = nc.session_info["stamp"]
out = ".trackers/" + stamp
fast_plot = fast_plot_value
if not os.path.exists(".trackers"):
    os.makedirs(".trackers")
# save out as empty file
with open(out, 'w') as f:
    f.write("")
nws = False

def bin_value(x, bin_res):
    return np.floor((x + bin_res / 2) / bin_res + 0.5) * bin_res - bin_res / 2

try:
    vv_name = variable
except:
    vv_name = "summary"
    variable = "summary"
Variable = variable.title()
if vv_name in ["benbio"]:
    compact = True
try:
    vv_name = definitions[variable].long_name 
except:
    pass
