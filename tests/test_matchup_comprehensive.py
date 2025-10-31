ff = "data/sst.mon.mean.nc"

import ecoval
import pytest
import nctoolkit as nc
import numpy as np
import pandas as pd
import glob
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock


class TestMatchupValidation:
    """Test input validation for matchup function"""
    
    def setup_method(self):
        """Setup test data paths"""
        self.sim_dir = "data/example"
        self.obs_dir = "data/evaldata"
        self.temp_dir = tempfile.gettempdir()
        
    def test_missing_sim_dir(self):
        """Test error when sim_dir is not provided"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                obs_dir=self.obs_dir, 
                start=2000, 
                end=2000,
                cores=1, 
                ask=False, 
                out_dir=self.temp_dir
            )
    
    def test_invalid_sim_dir(self):
        """Test error when sim_dir doesn't exist"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir="nonexistent/path",
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_missing_start_year(self):
        """Test error when start year is not provided"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                end=2000,
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_missing_end_year(self):
        """Test error when end year is not provided"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_invalid_start_year_type(self):
        """Test error when start year is not integer"""
        with pytest.raises(TypeError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start="x",
                end=2000,
                cores=1,
                ask=False,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )
    
    def test_invalid_end_year_type(self):
        """Test error when end year is not integer"""
        with pytest.raises(TypeError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end="2000",
                cores=1,
                ask=False,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )
    
    def test_end_before_start(self):
        """Test error when end year is before start year"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2010,
                end=2005,
                cores=1,
                ask=False,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )


class TestMatchupCoresValidation:
    """Test cores parameter validation"""
    
    def setup_method(self):
        self.sim_dir = "data/example"
        self.obs_dir = "data/evaldata"
        self.temp_dir = tempfile.gettempdir()
        
    def test_zero_cores(self):
        """Test error when cores is 0"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                cores=0,
                ask=False,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )
    
    def test_negative_cores(self):
        """Test error when cores is negative"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                cores=-1,
                ask=False,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )
    
    def test_string_cores(self):
        """Test error when cores is string"""
        with pytest.raises(TypeError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                cores="4",
                ask=False,
                lon_lim = [-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )
    
    def test_float_cores(self):
        """Test error when cores is float"""
        with pytest.raises(TypeError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                cores=4.5,
                ask=False,
                lat_lim= [40, 70],
                lon_lim = [-20, 20],
                out_dir=self.temp_dir
            )


class TestMatchupSurfaceValidation:
    """Test surface parameter validation"""
    
    def setup_method(self):
        self.sim_dir = "data/example"
        self.obs_dir = "data/evaldata"
        self.temp_dir = tempfile.gettempdir()
        
    def test_invalid_surface_string(self):
        """Test error with invalid surface variable"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                surface="invalid_variable",
                cores=1,
                ask=False,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )
    
    def test_invalid_surface_list(self):
        """Test error with invalid surface variable in list"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                surface=["temperature", "invalid_variable"],
                cores=1,
                ask=False,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )
    
    def test_benthic_surface_variable(self):
        """Test error when benthic variable used for surface"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                surface="benbio",
                cores=1,
                ask=False,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )
    
    def test_invalid_surface_dict_keys(self):
        """Test error with invalid dictionary keys for surface"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                surface={"invalid_key": ["temperature"]},
                cores=1,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                ask=False,
                out_dir=self.temp_dir
            )


class TestMatchupBottomValidation:
    """Test bottom parameter validation"""
    
    def setup_method(self):
        self.sim_dir = "data/example"
        self.obs_dir = "data/evaldata"
        self.temp_dir = tempfile.gettempdir()
        
    def test_invalid_bottom_variable(self):
        """Test error with invalid bottom variable"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                bottom=["invalid_variable"],
                cores=1,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_benthic_bottom_variable(self):
        """Test error when benthic variable used for bottom"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                bottom=["carbon"],
                cores=1,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_pco2_bottom_nws_only(self):
        """Test that pco2 bottom only works for NWS"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                bottom=["pco2"],
                cores=1,
                ask=False,
                out_dir=self.temp_dir,
                lon_lim=[-180, 180],  # Global domain
                lat_lim=[-90, 90]
            )


class TestMatchupBenthicValidation:
    """Test benthic parameter validation"""
    
    def setup_method(self):
        self.sim_dir = "data/example"
        self.obs_dir = "data/evaldata" 
        self.temp_dir = tempfile.gettempdir()
        
    def test_invalid_benthic_variable(self):
        """Test error with invalid benthic variable"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                benthic=["invalid_variable"],
                cores=1,
                ask=False,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )
    
    def test_surface_benthic_variable(self):
        """Test error when surface variable used for benthic"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                benthic=["temperature"],
                cores=1,
                ask=False,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )
    
    def test_benthic_string_input(self):
        """Test error when benthic is string instead of list"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                benthic="carbon",
                cores=1,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                ask=False,
                out_dir=self.temp_dir
            )


class TestMatchupCoordinateValidation:
    """Test coordinate limits validation"""
    
    def setup_method(self):
        self.sim_dir = "data/example"
        self.obs_dir = "data/evaldata"
        self.temp_dir = tempfile.gettempdir()
        
    def test_lon_lim_not_list(self):
        """Test error when lon_lim is not a list"""
        with pytest.raises(TypeError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                lon_lim=10,
                lat_lim=[40, 70],
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_lat_lim_not_list(self):
        """Test error when lat_lim is not a list"""
        with pytest.raises(TypeError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                lon_lim=[-20, 20],
                lat_lim=50,
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_lon_lim_wrong_length(self):
        """Test error when lon_lim doesn't have exactly 2 elements"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                lon_lim=[-20, 0, 20],
                lat_lim=[40, 70],
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_lat_lim_wrong_length(self):
        """Test error when lat_lim doesn't have exactly 2 elements"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                lon_lim=[-20, 20],
                lat_lim=[40],
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_lon_lim_invalid_range(self):
        """Test error when longitude range is invalid"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                lon_lim=[20, -20],  # max < min
                lat_lim=[40, 70],
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_lat_lim_invalid_range(self):
        """Test error when latitude range is invalid"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                lon_lim=[-20, 20],
                lat_lim=[70, 40],  # max < min
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_lat_lim_out_of_bounds(self):
        """Test error when latitude is out of valid range"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                lon_lim=[-20, 20],
                lat_lim=[-100, 70],  # -100 is invalid
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )


class TestMatchupPointTimeResValidation:
    """Test point_time_res parameter validation"""
    
    def setup_method(self):
        self.sim_dir = "data/example"
        self.obs_dir = "data/evaldata"
        self.temp_dir = tempfile.gettempdir()
        
    def test_point_time_res_invalid_type(self):
        """Test error when point_time_res is invalid type"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                point_time_res=1,
                cores=1,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_point_time_res_invalid_list_elements(self):
        """Test error when point_time_res list contains invalid elements"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                point_time_res=[1],
                cores=1,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_point_time_res_invalid_time_unit(self):
        """Test error when point_time_res contains invalid time units"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                point_time_res=["year", "month", "invalid_unit"],
                cores=1,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                ask=False,
                out_dir=self.temp_dir
            )


class TestMatchupFileValidation:
    """Test file and directory validation"""
    
    def setup_method(self):
        self.sim_dir = "data/example"
        self.obs_dir = "data/evaldata"
        self.temp_dir = tempfile.gettempdir()
        
    def test_invalid_mapping_file(self):
        """Test error when mapping file doesn't exist"""
        # raise file not found error
        with pytest.raises(FileNotFoundError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                mapping="nonexistent_mapping.csv",
                cores=1,
                ask=False,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )
    
    def test_invalid_thickness_file(self):
        """Test error when thickness file doesn't exist"""
        with pytest.raises(FileNotFoundError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                thickness="nonexistent_thickness.nc",
                surface = {"gridded": None, "point":["nitrate", "temperature"]},
                bottom = None, 
                benthic = None,
                point_all = "temperature",
                cores=1,
                ask=False,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )
    
    def test_invalid_obs_dir(self):
        """Test error when obs_dir doesn't exist and is not 'default'"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir="nonexistent/obs/dir",
                start=2000,
                end=2000,
                cores=1,
                ask=False,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )


class TestMatchupBooleanValidation:
    """Test boolean parameter validation"""
    
    def setup_method(self):
        self.sim_dir = "data/example"
        self.obs_dir = "data/evaldata"
        self.temp_dir = tempfile.gettempdir()
        
    def test_pft_not_boolean(self):
        """Test error when pft is not boolean"""
        with pytest.raises(TypeError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                pft="true",
                cores=1,
                ask=False,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )
    
    
    def test_everything_not_boolean(self):
        """Test error when everything is not boolean"""
        with pytest.raises(TypeError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                everything="false",
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_ask_not_boolean(self):
        """Test error when ask is not boolean"""
        with pytest.raises(TypeError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                ask=0,
                cores=1,
                out_dir=self.temp_dir
            )
    
    def test_overwrite_not_boolean(self):
        """Test error when overwrite is not boolean"""
        with pytest.raises(TypeError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                overwrite="yes",
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )


class TestMatchupIntegerValidation:
    """Test integer parameter validation"""
    
    def setup_method(self):
        self.sim_dir = "data/example"
        self.obs_dir = "data/evaldata"
        self.temp_dir = tempfile.gettempdir()
        
    def test_n_dirs_down_not_integer(self):
        """Test error when n_dirs_down is not integer"""
        with pytest.raises(TypeError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                n_dirs_down="2",
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_n_dirs_down_negative(self):
        """Test error when n_dirs_down is negative"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                n_dirs_down=-1,
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_n_check_not_integer(self):
        """Test error when n_check is not integer or None"""
        with pytest.raises(TypeError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                n_check="10",
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_n_check_negative(self):
        """Test error when n_check is negative"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                n_check=-5,
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )


class TestMatchupListValidation:
    """Test list parameter validation"""
    
    def setup_method(self):
        self.sim_dir = "data/example"
        self.obs_dir = "data/evaldata"
        self.temp_dir = tempfile.gettempdir()
        
    def test_exclude_not_list(self):
        """Test error when exclude is not a list"""
        with pytest.raises(TypeError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                exclude= 1,
                cores=1,
                ask=False,
                lon_lim =[-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )
    
    def test_point_all_not_list(self):
        """Test error when point_all is not a list"""
        with pytest.raises(TypeError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                point_all=1,
                cores=1,
                ask=False,
                out_dir=self.temp_dir
            )
    
    def test_point_years_not_list(self):
        """Test error when point_years is not a list"""
        with pytest.raises(TypeError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                point_years="2000",
                cores=1,
                ask=False,
                lon_lim=[-20, 20],
                lat_lim=[40, 70],
                out_dir=self.temp_dir
            )
    
    def test_point_years_wrong_length(self):
        """Test error when point_years doesn't have exactly 2 elements"""
        with pytest.raises(ValueError):
            ecoval.matchup(
                sim_dir=self.sim_dir,
                obs_dir=self.obs_dir,
                start=2000,
                end=2000,
                point_years=[1990, 2000, 2010],
                cores=1,
                ask=False,
                lon_lim = [-20, 20],
                lat_lim =[40, 70],
                out_dir=self.temp_dir
            )
