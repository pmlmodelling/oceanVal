
import ecoval
import nctoolkit as nc
import numpy as np
import pandas as pd
import glob
import os
import shutil


class TestFinal:
    def test_point(self):
        import tempfile

        print(tempfile.gettempdir())
        assert tempfile.gettempdir() == "/tmp"
        surface = {"gridded": None, "point":["nitrate", "temperature"]}
        # get the name of the temporary directory

        directory = "matched/point/nws/surface/nitrate/"
        # create the directory, recursively
        os.makedirs(directory, exist_ok = True)
        directory = "matched/point/nws/surface/temperature/"
        # create the directory, recursively
        os.makedirs(directory, exist_ok = True)

        if os.path.exists("matched/point/nws/surface/nitrate/model_surface_nitrate.csv"):
            os.remove("matched/point/nws/surface/nitrate/model_surface_nitrate.csv")
        if os.path.exists("matched/point/nws/surface/temperature/model_surface_temperature.csv"):
            os.remove("matched/point/nws/surface/temperature/model_surface_temperature.csv")

        ecoval.matchup(sim_dir = "data/example", obs_dir = "data/evaldata", start = 2000, end = 2000,  surface = surface, bottom = [], benthic = None, cores = 1, ask = False, lon_lim = [-10, 10], lat_lim = [40, 65])
        # list files in /tmp recursively
        # paths = glob.glob("/tmp/matched/*", recursive = True)
        ff =  "matched/point/nws/surface/nitrate/model_surface_nitrate.csv"
        # when was this file modified
        ff_time = os.path.getmtime(ff)
        ecoval.matchup(sim_dir = "data/example", obs_dir = "data/evaldata", start = 2000, end = 2000,  surface = surface, bottom = [], benthic = None, cores = 1, ask = False,  overwrite = False, lon_lim = [-10, 10], lat_lim = [40, 60] )

        ff = "matched/point/nws/surface/nitrate/model_surface_nitrate.csv"
        # when was this file modified
        new_time = os.path.getmtime(ff)
        assert ff_time == new_time

        assert os.path.exists("matched/point/nws/surface/nitrate/model_surface_nitrate.csv")
        assert os.path.exists("matched/point/nws/surface/temperature/model_surface_temperature.csv")


        df = pd.read_csv("matched/point/nws/surface/nitrate/model_surface_nitrate.csv")
        assert np.corrcoef(df["observation"], df["model"])[0,1] > 0.999
        # ensure average abs difference < 0.01
        assert np.mean(np.abs(df["observation"] - df["model"])) < 0.01

        df = pd.read_csv("matched/point/nws/surface/temperature/model_surface_temperature.csv")
        assert np.corrcoef(df["observation"], df["model"])[0,1] > 0.999
        # ensure average abs difference < 0.01
        assert np.mean(np.abs(df["observation"] - df["model"])) < 0.01

        if os.path.exists("book"):
            shutil.rmtree("book")
        # remove results directory if it exists
        if os.path.exists("results"):
            shutil.rmtree("results")

        ecoval.validate(test = True)

        ff = [x for x in glob.glob("book/_build/html/notebooks/*") if "nitrate" in x]
        assert len(ff) == 1
        ff = ff[0]
        line = "This is getting to the end!"
        #read in and  identify if line is in the file
        with open(ff, 'r') as file:
            filedata = file.read()
            assert line in filedata

        ff = [x for x in glob.glob("book/_build/html/notebooks/*") if "temperature" in x]
        assert len(ff) == 1
        ff = ff[0]
        line = "This is getting to the end!"
        #read in and  identify if line is in the file
        with open(ff, 'r') as file:
            filedata = file.read()
            assert line in filedata

        shutil.rmtree("book")
        # results directory
        shutil.rmtree("results")

        shutil.rmtree("matched")
        #os.removedirs("/tmp/matched")

