import nctoolkit as nc
import re
import pandas as pd
import os
import glob
import warnings
from oceanval.session import session_info

session_info["keys"] = []


def get_name(obj):
    namespace = globals()
    for name in namespace:
        if namespace[name] is obj:
            return name
    return None

# create a validator class
# create a variable class to hold metadata
class Variable:
    def __init__(self):
        self.long_name = None
        self.gridded = None 



class Validator:
    def __init__(self):
        self.rules = {}

    def validate(self, data):
        errors = {}
        for field, rule in self.rules.items():
            if field not in data:
                errors[field] = "Field is missing"
            elif not rule(data[field]):
                errors[field] = "Validation failed"
        return errors
    # add chlorophyll
    def add_rule(self, field, rule):
        self.rules[field] = rule

    keys = session_info["keys"]


    # ensure self.x = y, adds x to the keys list
    def __setattr__(self, name, value):
        if name != "keys" and "rules" not in name:
            if name not in self.keys:
                self.keys.append(name)
                # ensure this can be accessed via self[name]

        super().__setattr__(name, value)

    # create a [] style accessor
    # make Validator subsettable, so that validator["chlorophyll"] returns the chlorophyll variable
    def __getitem__(self, key):
        # if key == "chlorophyll":
        #     return  
        return getattr(self, key, None)
    
    # add a method that let's user create a new Variable and add it to the definitions
    # 
    def add_gridded_comparison(self, 
                               name, 
                               long_name = None, 
                               short_name = None, 
                               short_title = None, 
                               source = None, 
                               source_info = None, 
                               model_variable = None, 
                               obs_path = None, 
                               obs_variable = "auto", 
                               start = -1000, 
                               end = 3000, 
                               vertical = False, 
                               climatology = None, 
                               obs_multiplier = 1,
                               thredds = False
                                   ): 
        """

        Add a gridded comparison variable to the Validator

        Parameters:

        name (str): Name of the variable

        long_name (str): Long name of the variable

        short_name (str): Short name of the variable

        short_title (str): Short title of the variable

        source (str): Source of the variable

        source_info (str): Source information of the variable

        model_variable (str): Model variable name

        obs_path (str): Directory or path of the observations

        obs_variable (str): Observation variable name

        start (int): Start depth of the variable

        end (int): End depth of the variable

        vertical (bool): Whether the variable is vertical

        climatology (bool): Whether to use climatology

        obs_multiplier (float): Multiplier for the observation

        """

        try:
            point_dir = getattr(self, name).point_dir
            point = getattr(self, name).point
            point_source = getattr(self, name).point_source
            orig_sources = getattr(self, name).sources
            # get point start
            point_start = getattr(self, name).point_start
            point_end = getattr(self, name).point_end
            depths = getattr(self, name).depths
            vertical_point = getattr(self, name).vertical_point
            old_model_variable = getattr(self, name).model_variable
            old_obs_multiplier = getattr(self, name).obs_multiplier_point
            old_binning = getattr(self, name).binning
        except:
            orig_sources = dict()
            point = None,
            point_source = None
            point_dir = None
            point_start = -1000
            point_end = 3000
            depths = None
            vertical_point = None
            old_model_variable = None
            old_obs_multiplier = 1
            old_binning = dict()
            pass

        if old_model_variable is not None and old_model_variable != model_variable:
            if old_model_variable != "auto":
                raise ValueError(f"Model variable for {name} already exists as {old_model_variable}, cannot change to {model_variable}")
        
        var = Variable()
        if source is None:
            raise ValueError("Source must be supplied")
        if model_variable is None:
            raise ValueError("Model variable must be supplied")
        # climatology must be provideded
        if climatology is None:
            raise ValueError("Climatology must be provided for gridded comparison")
        # obs_path is needed
        if obs_path is None:
            raise ValueError("obs_path must be provided for gridded comparison")
        # must be boolean
        if not isinstance(climatology, bool):
            raise ValueError("Climatology must be a boolean value")
        try:
            obs_multiplier  = float(obs_multiplier)
        except:
            raise ValueError("obs_multiplier must be a number")

        assumed = []

        if long_name is None:
            long_name = name
            assumed.append("long_name")
        if short_name is None:
            short_name = name
            assumed.append("short_name")
        if short_title is None:
            short_title = name.title()
            assumed.append("short_title")

        if source_info is None:
            source_info = f"Source for {source}"
            assumed.append("source_info")

        source = {source: source_info}
        if list(source.keys())[0] in orig_sources:
            # ensure the value is the same
            if orig_sources[list(source.keys())[0]] != source[list(source.keys())[0]]:
                raise ValueError(f"Source {list(source.keys())[0]} already exists with a different value")
        # ensure the sourc key does not included "_"
        if "_" in list(source.keys())[0]:
            raise ValueError("Source key cannot contain '_'")
        if not isinstance(obs_variable, str):
            raise ValueError("obs_variable must be a string")

        gridded_dir = obs_path
        if gridded_dir != "auto":
            if thredds is False:
                if not os.path.exists(gridded_dir):
                    raise ValueError(f"Gridded directory {gridded_dir} does not exist")
        # thredds must be boolean
        if not isinstance(thredds, bool):
            raise ValueError("thredds must be a boolean value")

        if name in session_info["short_title"]:
            if short_title is not None:
                if short_title != session_info["short_title"][name]:
                    raise ValueError(f"Short title for {name} already exists as {session_info['short_title'][name]}, cannot change to {short_title}")
        
        var.thredds = thredds
        var.climatology = climatology
        var.obs_multiplier_point = old_obs_multiplier
        var.obs_multiplier_gridded = obs_multiplier
        var.n_levels = 1
        var.vertical_gridded = vertical
        var.vertical_point = vertical_point
        var.depths = depths
        var.gridded_start = start
        var.gridded_end = end
        var.point_start = point_start
        var.point_end = point_end
        var.point = point
        var.point_source = point_source
        var.gridded = True
        var.long_name = long_name
        var.binning = old_binning
        # if this is None set to Name
        var.short_name = short_name
        if var.short_name is None:
            var.short_name = name
            assumed.append("short_name")    
        var.short_title = short_title
        if var.short_title is None:
            var.short_title = name.title()
            assumed.append("short_title")
        # check if this is c
        session_info["short_title"][name] = var.short_title

        source_name = source
        var.sources = orig_sources | source
        var.gridded_source = list(source.keys())[0]
        var.model_variable = model_variable
        var.point_dir = point_dir
        # add obs_variable, ensure it's a string
        var.obs_variable = obs_variable
        # check this exists
        gridded_dir = obs_path
        var.gridded_dir = gridded_dir

        # ensure nothing is None
        for attr in [var.long_name, var.short_name, var.short_title, var.sources, var.model_variable, var.obs_variable, var.gridded_source]:
            if attr is None:
                raise ValueError(f"Attribute {attr} cannot be None")
        setattr(self, name, var)
        # warnings for assumptions
        if len(assumed) > 0:
            print(f"Warning: The following attributes were missing and were assumed for variable {name}: {assumed}")
    # 
    def add_point_comparison(self, 
                             name = None, 
                             long_name = None, 
                             vertical = False, 
                             short_name = None, 
                             short_title = None, 
                             source = None, 
                             source_info = None, 
                             model_variable = None, 
                             start = -1000, 
                             end = 3000, 
                             obs_path = None, 
                             obs_multiplier = 1, 
                             binning = None  ):
        """

        Add a point comparison variable to the Validator

        Parameters:

        name (str): Name of the variable

        long_name (str): Long name of the variable

        vertical (bool): Whether the variable is vertical

        short_name (str): Short name of the variable

        short_title (str): Short title of the variable

        source (str): Source of the variable

        source_info (str): Source information of the variable

        model_variable (str): Model variable name

        start (int): Start depth of the variable

        end (int): End depth of the variable

        obs_path (str): Directory of the observations

        obs_multiplier (float): Multiplier for the observation, if needed to convert units

        binning (list): Binning information [lon_resolution, lat_resolution]

        """

        try:
            gridded_dir = getattr(self, name).gridded_dir   
            obs_variable = getattr(self, name).obs_variable
            gridded = getattr(self, name).gridded
            gridded_source = getattr(self, name).gridded_source
            orig_sources = getattr(self, name).sources
            gridded_start = getattr(self, name).gridded_start
            gridded_end = getattr(self, name).gridded_end
            old_model_variable = getattr(self, name).model_variable 
            # old climatology
            old_climatology = getattr(self, name).climatology
            old_obs_multiplier = getattr(self, name).obs_multiplier_gridded
            vertical_gridded = getattr(self, name).vertical_gridded
            thredds = getattr(self, name).thredds
        except:
            gridded_dir = "auto"
            obs_variable = "auto"
            gridded_source = "auto"
            gridded = False
            orig_sources = dict()
            gridded_start = -1000
            gridded_end = 3000
            old_model_variable = None
            old_climatology = None
            old_obs_multiplier = 1
            vertical_gridded = False
            thredds = False
            pass

        if old_model_variable is not None and old_model_variable != model_variable:
            if old_model_variable != "auto":
                raise ValueError(f"Model variable for {name} already exists as {old_model_variable}, cannot change to {model_variable}")

        var = Variable()

        source_name = source

        try:
            obs_multiplier= float(obs_multiplier)
        except:
            raise ValueError("obs_multiplier must be a number")
        # vertical must be a boolean
        if not isinstance(vertical, bool):
            raise ValueError("vertical must be a boolean value")

        # check these are int or can be cast to int
        try:
            start = int(start)
            end = int(end)
        except:
            raise ValueError("start and end must be integers")


        assumed = []
        if source_info is None:
            source_info = f"Source for {source}"
            assumed.append("source_info")
        if long_name is None:
            long_name = name
            assumed.append("long_name")
        if short_name is None:
            short_name = name
            assumed.append("short_name")
        if short_title is None:
            short_title = name.title()
            assumed.append("short_title")

        if name in session_info["short_title"]:
            if short_title != session_info["short_title"][name]:
                raise ValueError(f"Short title for {name} already exists as {session_info['short_title'][name]}, cannot change to {short_title}")

        source = {source: source_info}
        if list(source.keys())[0] in orig_sources:
            # ensure the value is the same
            if orig_sources[list(source.keys())[0]] != source[list(source.keys())[0]]:
                raise ValueError(f"Source {list(source.keys())[0]} already exists with a different value")
        # ensure the sourc key does not included "_"
        if "_" in list(source.keys())[0]:
            raise ValueError("Source key cannot contain '_'")
        point_files = [f for f in glob.glob(os.path.join(obs_path, "*.csv"))] 
        # if no files exists, raise error
        if len(point_files) == 0:
            raise ValueError(f"No csv files found in point directory {obs_path}")
        valid_vars = ["lon", "lat", "year", "month", "day", "depth", "observation", "source"]
        vertical_option = False
        for vv in point_files:
            # read in the first row
            df = pd.read_csv(vv, nrows=1)
            # throw error something else is in there
            bad_cols = [col for col in df.columns if col not in valid_vars]
            if len(bad_cols) > 0:
                raise ValueError(f"Invalid columns {bad_cols} found in point data file {vv}")
            if "depth" in df.columns:
                vertical = vertical_option
            # lon/lat/observation *must* be in df
            for req_col in ["lon", "lat", "observation"]:
                if req_col not in df.columns:
                    raise ValueError(f"Required column {req_col} not found in point data file {vv}")
        if vertical_option is False:
            if vertical:
                raise ValueError("vertical is set to True but no depth column found in point data files. You cannot vertically validate this data.")
        # if binning is supplied, ensure it is a 2 variable list
        if binning is not None:
            if not isinstance(binning, list) or len(binning) != 2:
                raise ValueError("binning must be a list of two values: [spatial_resolution, depth_resolution]")
        # ensure each element of binning is a number
            for res in binning:
                try:
                    float(res)
                except:
                    raise ValueError("Each element of binning must be a number")
        

        var.climatology = old_climatology
        var.n_levels = 1
        var.gridded_start = gridded_start
        var.gridded_end = gridded_end
        var.obs_multiplier_gridded= old_obs_multiplier
        var.obs_multiplier_point= obs_multiplier
        var.point = True
        var.gridded = gridded
        var.long_name = long_name
        if var.long_name is None:
            var.long_name = name
            assumed.append("long_name")

        var.vertical_point = vertical
        var.vertical_gridded = vertical_gridded 

        var.short_name = short_name
        if var.short_name is None:
            var.short_name = name
            assumed.append("short_name")

        var.short_title = short_title
        if var.short_title is None:
            var.short_title = name.title()
            assumed.append("short_title")
        var.point_start = start
        var.point_end = end
        # append source to the var.source
        # check if source key is in orig_source
        var.sources = orig_sources | source 
        var.gridded_source = gridded_source
        var.point_source = list(source.keys())[0]   
        var.model_variable = model_variable
        var.point_dir = obs_path
        # find csv files in point_dir
        var.thredds = thredds

        var.vertical = vertical

        var.obs_variable = obs_variable
        # check this exists
        point_dir = obs_path
        if point_dir != "auto":
            if not os.path.exists(point_dir):
                raise ValueError(f"Point directory {point_dir} does not exist")
        var.gridded_dir = gridded_dir
        if gridded_dir != "auto":
            if not os.path.exists(gridded_dir):
                raise ValueError(f"Gridded directory {gridded_dir} does not exist")

        # figure out if var.binning exists
        try:
            old_binning = getattr(self, name).binning
            var.binning = old_binning 
        except:
            var.binning = binning 

        # ensure nothing is None
        for attr in [var.long_name, var.short_name, var.short_title, var.sources, var.model_variable]:
            if attr is None:
                raise ValueError(f"Attribute {attr} cannot be None")
        setattr(self, name, var)

        for vv in assumed:
            print(f"Warning: The attribute {vv} was missing and was assumed for variable {name}")
        session_info["short_title"][name] = var.short_title
    # 

definitions = Validator()



def generate_mapping(ds):
    """
    Generate mapping of model and observational variables
    """

    model_dict = {}
    try:
        candidate_variables = definitions.keys
        ds1 = nc.open_data(ds[0], checks=False)
        ds_contents = ds1.contents

        ds_contents["long_name"] = [str(x) for x in ds_contents["long_name"]]

        ds_contents_top = ds_contents.query("nlevels == 1").reset_index(drop=True)
        #ds_contents = ds_contents.query("nlevels > 1").reset_index(drop=True)
        n_levels = int(ds_contents.nlevels.max())
        if n_levels > session_info["n_levels"]:
            session_info["n_levels"] = n_levels
        # number of rows in ds_contents
        if len(ds_contents) == 0:
            ds_contents = ds_contents_top
    except:
        return model_dict

    for vv in candidate_variables:
        variables = definitions[vv].model_variable.split("+")
        include = True
        for var in variables:
            if var not in ds_contents.variable.values:
                include = False
        if include:
            model_dict[vv] = definitions[vv].model_variable
            n_levels = ds_contents.query("variable in @variables")["nlevels"].max()
            if n_levels > definitions[vv].n_levels:
                definitions[vv].n_levels = n_levels 
            continue

    return model_dict


