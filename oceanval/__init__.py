import pandas as pd
import shutil
import glob
import subprocess
import warnings
import nctoolkit as nc
import copy
from oceanval.matchall import matchup
import dill
from oceanval.fixers import tidy_name
from oceanval.session import session_info
import webbrowser
from oceanval.chunkers import add_chunks
import os
import re
from oceanval.fvcom import fvcom_preprocess
import importlib

from oceanval.parsers import Validator, definitions

add_point_comparison = definitions.add_point_comparison
add_gridded_comparison = definitions.add_gridded_comparison

# loop through the keys and make sure all attributes are set
#for key in definitions.keys:
for key in session_info["keys"]:
    try:
        x = definitions[key].gridded
    except AttributeError:
        raise AttributeError(f"Variable '{key}' is missing 'gridded' attribute")
    try:
        x = definitions[key].point
    except AttributeError:
        raise AttributeError(f"Variable '{key}' is missing 'point' attribute")
    try:
        x = definitions[key].sources
    except AttributeError:
        raise AttributeError(f"Variable '{key}' is missing 'source' attribute")
    try:
        x = definitions[key].short_name
    except AttributeError:
        raise AttributeError(f"Variable '{key}' is missing 'short_name' attribute")
    try:
        x = definitions[key].long_name
    except AttributeError:
        raise AttributeError(f"Variable '{key}' is missing 'long_name' attribute")
# add a test to make sure definitions is complete


def fix_toc(concise = True):
    short_titles = dill.load(open("matched/short_titles.pkl", "rb")) 
    paths = glob.glob(f"book/notebooks/*.ipynb")
    #variables = list(pd.read_csv("matched/mapping.csv").variable)
    variables = dill.load(open("matched/variables_matched.pkl", "rb"))
    variables.sort()

    vv_dict = dict()
    for vv in variables:
        if vv != "ph":
            vv_paths = [os.path.basename(x) for x in paths if vv in x]
            if len(vv_paths) > 0:
                vv_dict[vv] = vv_paths
        else:
            vv_paths = [
                os.path.basename(x)
                for x in paths
                if vv in x and "phos" not in x and "chlo" not in x and "occci" not in x
            ]
            if len(vv_paths) > 0:
                vv_dict[vv] = vv_paths
    # get summary docs
    ss_paths = [os.path.basename(x) for x in paths if "summary" in x]

    out = f"book/_toc.yml"

    # write line by line to out
    i_chapter = 1
    with open(out, "w") as f:
        # "format: jb-book"
        x = f.write("format: jb-book\n")
        x = f.write("root: intro\n")
        x = f.write("parts:\n")
        x = f.write(f"- caption: Introduction\n")
        x = f.write("  chapters:\n")
        x = f.write(f"  - file: notebooks/000_info.ipynb\n")
        x = f.write(f"  - file: notebooks/001_methods.ipynb\n")

        # open notebook and replace book_chapter with i_chapter
        if True:
            with open(f"book/notebooks/000_info.ipynb", "r") as file:
                filedata = file.read()

            # Replace the target string
            filedata = filedata.replace("book_chapter", str(i_chapter))

            # Write the file out again
            with open(f"book/notebooks/000_info.ipynb", "w") as file:
                file.write(filedata)
            i_chapter += 1

        # open notebook and replace book_chapter with i_chapter
        with open(f"book/notebooks/001_methods.ipynb", "r") as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace("book_chapter", str(i_chapter))

        with open(f"book/notebooks/001_methods.ipynb", "w") as file:
            file.write(filedata)
        i_chapter += 1

        x = f.write(f"- caption: Summaries\n")
        x = f.write("  chapters:\n")
        for ff in ss_paths:
            x = f.write(f"  - file: notebooks/{ff}\n")
            # open notebook and replace book_chapter with i_chapter
            with open(f"book/notebooks/{ff}", "r") as file:
                filedata = file.read()

            filedata = filedata.replace("book_chapter", str(i_chapter))

            # Replace the target string
            # Write the file out again
            with open(f"book/notebooks/{ff}", "w") as file:
                file.write(filedata)
            i_chapter += 1

        # loop over variables in each vv_dict
        # value is the file in the chapter section
        # key is the variable name, so is the section
        for vv in vv_dict.keys():
            # capitalize if not ph
            vv_out = short_titles[vv]

            x = f.write(f"- caption: {vv_out}\n")
            x = f.write("  chapters:\n")
            for ff in vv_dict[vv]:
                x = f.write(f"  - file: notebooks/{ff}\n")

                # open notebook and replace book_chapter with i_chapter
                with open(f"book/notebooks/{ff}", "r") as file:
                    filedata = file.read()

                # Replace the target string
                filedata = filedata.replace("book_chapter", str(i_chapter))

                # Write the file out again

                with open(f"book/notebooks/{ff}", "w") as file:
                    file.write(filedata)
                i_chapter += 1


def fix_toc_comparison():
    book_dir = "book"

    out = f"{book_dir}/compare/_toc.yml"
    # write line by line to out
    with open(out, "w") as f:
        # "format: jb-book"
        x = f.write("format: jb-book\n")
        x = f.write("root: intro\n")
        x = f.write("parts:\n")
        x = f.write(f"- caption: Comparisons with gridded surface observations\n")
        x = f.write("  chapters:\n")
        x = f.write(f"  - file: notebooks/comparison_bias.ipynb\n")
        x = f.write(f"  - file: notebooks/comparison_spatial.ipynb\n")
        x = f.write(f"  - file: notebooks/comparison_seasonal.ipynb\n")
        x = f.write(f"  - file: notebooks/comparison_regional.ipynb\n")
        x = f.write(f"- caption: Comparisons with point observations\n")
        x = f.write("  chapters:\n")
        x = f.write(f"  - file: notebooks/comparison_point_surface.ipynb\n")




def validate(
    lon_lim=None,
    lat_lim=None,
    concise = True,
    variables="all",
    fixed_scale = False,
    region = None,
    test=False,
):
    # docstring
    """
    Run the model evaluation for all of the available datasets, and generate a validation report.

    Parameters
    ----------
    lon_lim : list or None
        The longitude limits for the validation. Default is None
    lat_lim : list or None
        The latitude limits for the validation. Default is None
    variables : str or list
        The variables to run the model evaluation for. Default is "all"
    fixed_scale : bool
        Whether to use a fixed scale for the seasonal plots. Default is False. If True, the minimum and maximum values are capped to cover the 2nd and 98th percentiles of both model and observations.
    region : str or None
        The region being validated. Must be either "nwes" (northwest European Shelf) or "global". Default is None.
    test : bool
        Default is False. Ignore, unless you are testing oceanval.

    Returns
    -------
    None
    """
    #  regioncan only be nwes or global
    if region is not None:
        if region not in ["nwes", "global"]:
            raise ValueError("region must be either 'nwes' or 'global'")
    # if lon_lim  is not None, make sure it's a list
    if lon_lim is not None:
        if isinstance(lon_lim, list) == False:
            raise ValueError("lon_lim must be a list")
        else:
            if len(lon_lim) != 2:
                raise ValueError("lon_lim must be a list of length 2")
    if lat_lim is not None:
        if isinstance(lat_lim, list) == False:
            raise ValueError("lat_lim must be a list")
        else:
            if len(lat_lim) != 2:
                raise ValueError("lat_lim must be a list of length 2")

    import os

    path_df = []

    fast_plot = False

    # figure out of "book/notebooks" has ipynb files

    empty = True

    # book directory is book, book1, book2, book10 etc.

    # create a new name if one already exists
    i = 0

    if os.path.exists("book"):
        # get user input to decide if it should be removed
        while True:
                files = glob.glob(f"book/**/**/**", recursive=True)
                # list all files in book, recursively
                for ff in files:
                    if ff.startswith(f"book/"):
                        try:
                            os.remove(ff)
                        except:
                            pass
                files = glob.glob(f"book/**/**/**", recursive=True)
                # only list files
                files = [x for x in files if os.path.isfile(x)]
                if len(files) == 0:
                    break

    # remove the results directory
    x_path = "results"
    if os.path.exists(x_path):
        if x_path == "results":
            shutil.rmtree(x_path)
    import os

    if variables != "all":
        if isinstance(variables, str):
            variables = [variables]

    if empty:
        from shutil import copyfile

        if not os.path.exists("book"):
            os.mkdir("book")
        if not os.path.exists("book/notebooks"):
            os.mkdir("book/notebooks")


        data_path = importlib.resources.files(__name__).joinpath("data/000_info.ipynb")
        if not os.path.exists(f"book/notebooks/000_info.ipynb"):
            copyfile(data_path, f"book/notebooks/000_info.ipynb")

        data_path = importlib.resources.files(__name__).joinpath("data/001_methods.ipynb")
        if not os.path.exists(f"book/notebooks/001_methods.ipynb"):
            copyfile(data_path, f"book/notebooks/001_methods.ipynb")
        # open this file and replace model_name with model


        data_path = importlib.resources.files(__name__).joinpath("data/_toc.yml")

        out = f"book/" + os.path.basename(data_path)
        copyfile(data_path, out)

        data_path = importlib.resources.files(__name__).joinpath("data/requirements.txt")
        out = f"book/" + os.path.basename(data_path)
        copyfile(data_path, out)

        data_path = importlib.resources.files(__name__).joinpath("data/intro.md")
        out = f"book/" + os.path.basename(data_path)
        copyfile(data_path, out)

        # copy config

        data_path = importlib.resources.files(__name__).joinpath("data/_config.yml")
        out = f"book/" + os.path.basename(data_path)

        with open(data_path, "r") as file:
            filedata = file.read()


        # Write the file out again
        with open(out, "w") as file:
            file.write(filedata)

        # copyfile(data_path, out)

        path_df = []

        # loop through the point matchups and generate notebooks

        point_paths = glob.glob("matched/point/**/**/**/**.csv")
        point_paths = [x for x in point_paths if "paths.csv" not in x]
        point_paths = [x for x in point_paths if "unit" not in os.path.basename(x)]
        # loop through the paths
        for pp in point_paths:
            ff_def = pp.replace(".csv", "_definitions.pkl")
            definitions = dill.load(open(ff_def, "rb"))
            vv = os.path.basename(pp).split("_")[2].replace(".csv", "")
            if variables != "all":
                if True:
                    if vv not in variables:
                        continue
            source = os.path.basename(pp).split("_")[0]
            variable = vv
            layer = os.path.basename(pp).split("_")[1].replace(".csv", "")
            Variable = definitions[variable].short_name

            vv_file = pp
            vv_file_find = pp.replace("../../", "")

            if os.path.exists(vv_file_find):
                if (
                    len(
                        glob.glob(
                            f"book/notebooks/*point_{layer}_{variable}.ipynb"
                        )
                    )
                    == 0
                ):
                    file1 = importlib.resources.files(__name__).joinpath("data/point_template.ipynb")
                    with open(file1, "r") as file:
                        filedata = file.read()

                    if layer in [ "all", "surface"]:
                        filedata = filedata.replace(
                            "chunk_point_surface", "chunk_point"
                        )
                    else:
                        filedata = filedata.replace("chunk_point_surface", "")
                    if layer in ["bottom", "all"]:
                        if vv.lower() not in ["pco2"]:
                            filedata = filedata.replace(
                                "chunk_point_bottom", "chunk_point"
                            )
                        else:
                            filedata = filedata.replace("chunk_point_bottom", "")
                    else:
                        filedata = filedata.replace("chunk_point_bottom", "")

                    # Replace the target string
                    out = f"book/notebooks/{source}_{layer}_{variable}.ipynb"
                    filedata = filedata.replace("point_variable", variable)
                    n_levels = definitions[variable].n_levels
                    if layer != "all":
                        if n_levels > 1:
                            filedata = filedata.replace(
                                "Validation of point_layer", f"Validation of {layer}"
                            )
                        else:
                            filedata = filedata.replace(
                                "Validation of point_layer", f"Validation of "
                            )
                    else:
                        filedata = filedata.replace(
                            "Validation of point_layer", f"Validation of "
                        )

                    filedata = filedata.replace("point_layer", layer)
                    filedata = filedata.replace("point_obs_source", source)
                    filedata = filedata.replace("template_title", Variable)

                    # Write the file out again
                    with open(out, "w") as file:
                        file.write(filedata)
                    variable = vv
                    if variable == "pco2":
                        variable = "pCO2"
                    path_df.append(
                        pd.DataFrame(
                            {
                                "variable": [variable],
                                "path": out,
                            }
                        )
                    )

        # Loop through the gridded matchups and generate notebooks
        # identify gridded variables in matched data
        gridded_paths = glob.glob("matched/gridded/**/**.nc")

        if len(gridded_paths) > 0:
            for vv in [
                os.path.basename(x).split("_")[1].replace(".nc", "")
                for x in gridded_paths
            ]:
                for source in [
                    os.path.basename(x).split("_")[0]
                    for x in glob.glob(f"matched/gridded/**/**_{vv}_**.nc")
                ]:

                    variable = vv
                    if variables != "all":
                        if vv not in variables:
                            continue
                    if not os.path.exists(
                        f"book/notebooks/{source}_{variable}.ipynb"
                    ):
                        ff_def = glob.glob(f"matched/gridded/{variable}/*definitions*.pkl")[0]
                        definitions = dill.load(open(ff_def, "rb"))
                        Variable = definitions[variable].short_name
    
                        file1 = importlib.resources.files(__name__).joinpath("data/gridded_template.ipynb")
                        if (
                            len(
                                glob.glob(
                                    f"book/notebooks/*{source}_{variable}.ipynb"
                                )
                            )
                            == 0
                        ):
                            with open(file1, "r") as file:
                                filedata = file.read()

                            # Replace the target string
                            filedata = filedata.replace("template_variable", variable)
                            filedata = filedata.replace("template_title", Variable)
                            filedata = filedata.replace("source_name", source)
                            if region == "nwes":
                                filedata = filedata.replace("zonal_height", "6000" )
                            else:
                                filedata = filedata.replace("zonal_height", "2000" )
                            # make every letter a capital
                            source_capital = source.upper()
                            filedata = filedata.replace("source_title", source_capital)
                            # change sub_regions_value to region
                            if region is not None: 
                                filedata = filedata.replace(
                                    "sub_regions_value", str(region)
                                )

                            # Write the file out again
                            with open(
                                f"book/notebooks/{source}_{variable}.ipynb", "w"
                            ) as file:
                                file.write(filedata)

                            variable = vv
                            path_df.append(
                                pd.DataFrame(
                                    {
                                        "variable": [variable],
                                        "path": [
                                            f"book/notebooks/{source}_{variable}.ipynb"
                                        ],
                                    }
                                )
                            )

        # need to start by figuring out whether anything has already been run...

        i = 0

        for ff in [
            x for x in glob.glob("book/notebooks/*.ipynb") if "info" not in x
        ]:
            try:
                i_ff = int(os.path.basename(ff).split("_")[0])
                if i_ff > i:
                    i = i_ff
            except:
                pass

        i_orig = i

        if len(path_df) > 0:
            path_df = pd.concat(path_df)
            path_df = path_df.sort_values("variable").reset_index(drop=True)

        for i in range(len(path_df)):
            file1 = path_df.path.values[i]
            # pad i with zeros using zfill
            i_pad = str(i + 1).zfill(3)
            new_file = (
                os.path.dirname(file1) + "/" + i_pad + "_" + os.path.basename(file1)
            )
            os.rename(file1, new_file)
            # print(key, value)

        # copy the summary.ipynb notebook and add i_pad to the name

        i = i + 2
        i_pad = str(i).zfill(3)

        # shelf = False
        # # figure out if we need the shelf
        # try:
        #     ds_regions = nc.open_data(f"{data_dir}/amm7_val_subdomains.nc")
        #     ds_xr = ds_regions.to_xarray()
        #     lon_size = len(ds_xr.lon)
        #     lat_size = len(ds_xr.lat)

        #     ensemble = nc.create_ensemble("matched")
        #     ff = ensemble[0]
        #     ds = nc.open_data(ff)
        #     ds_xr = ds.to_xarray()
        #     lon_size_ds = len(ds_xr.lon)
        #     lat_size_ds = len(ds_xr.lat)

        #     if lon_size_ds == lon_size:
        #         if lat_size_ds == lat_size:
        #             shelf = True
        #         else:
        #             shelf = False
        # except:
        #     shelf = False

        # # copy the summary notebook for the full domain

        # if shelf:
        #     file1 = importlib.resources.files(__name__).joinpath("data/summary.ipynb")
        #     if len(glob.glob(f"book/notebooks/*summary.ipynb")) == 0:
        #         copyfile(file1, f"book/notebooks/{i_pad}_summary_shelf.ipynb")
        #         # change domain_title to "Shelf"
        #         with open(
        #             f"book/notebooks/{i_pad}_summary_shelf.ipynb", "r"
        #         ) as file:
        #             filedata = file.read()

        #         # Replace the target string
        #         filedata = filedata.replace("domain_title", "Shelf")

        #         # Write the file out again
        #         with open(
        #             f"book/notebooks/{i_pad}_summary_shelf.ipynb", "w"
        #         ) as file:
        #             file.write(filedata)

        #         i += 1

        #         i_pad = str(i).zfill(3)

        file1 = importlib.resources.files(__name__).joinpath("data/summary.ipynb")
        if len(glob.glob(f"book/notebooks/*summary.ipynb")) == 0:
            copyfile(file1, f"book/notebooks/{i_pad}_summary.ipynb")
        else:
            if i > (i_orig + 1):
                initial = glob.glob(f"book/notebooks/*summary.ipynb")[0]
                copyfile(initial, f"book/notebooks/{i_pad}_summary.ipynb")
                i += 1

        # change domain_title to "Full domain"

        with open(f"book/notebooks/{i_pad}_summary.ipynb", "r") as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace("domain_title", "Full domain")

        # Write the file out again
        with open(f"book/notebooks/{i_pad}_summary.ipynb", "w") as file:
            file.write(filedata)

        # pair the notebooks using jupyter text

        os.system(
            f"jupytext --set-formats ipynb,py:percent book/notebooks/*.ipynb"
        )

        # add the chunks
        add_chunks()

        # loop through the notebooks and set r warnings options
        for ff in glob.glob(f"book/notebooks/*.py"):
            with open(ff, "r") as file:
                filedata = file.read()

            # loop through line by line, and rewrite the original file
            lines = filedata.split("\n")
            new_lines = []
            for line in lines:
                if "%%R" in line:
                    new_lines.append(line)
                    new_lines.append("options(warn=-1)")
                else:
                    new_lines.append(line)
            # loop through all lines in lines and replace the_test_status with True
            for i in range(len(new_lines)):
                new_lines[i] = new_lines[i].replace("latexpagebreak", "")
                if "the_test_status" in new_lines[i]:
                    if test:
                        new_lines[i] = new_lines[i].replace("the_test_status", "True")
                    else:
                        new_lines[i] = new_lines[i].replace("the_test_status", "False")
                if '"gam"' in new_lines[i]:
                    new_lines[i] = new_lines[i].replace('"gam"', '"lm"')

                new_lines[i] = new_lines[i].replace("the_lon_lim", str(lon_lim))
                new_lines[i] = new_lines[i].replace("the_lat_lim", str(lat_lim))
                new_lines[i] = new_lines[i].replace("fixed_scale_value", str(fixed_scale))
                # replace concice_value with concice
                if "concise_value" in new_lines[i]:
                    if concise:
                        new_lines[i] = new_lines[i].replace(
                            "concise_value", "True"
                        )
                    else:
                        new_lines[i] = new_lines[i].replace("concise_value", "False")

            # write the new lines to the file
            with open(ff, "w") as file:
                for line in new_lines:
                    file.write(line + "\n")

        # sync the notebooks
        #
        os.system(f"jupytext --sync book/notebooks/*.ipynb")


    # loop through notebooks and change fast_plot_value to fast_plot

    for ff in glob.glob(f"book/notebooks/*.ipynb"):
        with open(ff, "r") as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace("fast_plot_value", str(fast_plot))

        # fix linees using the above
        def fix_r_magic(x):
            if "%%R" in x:
                x = re.sub(r" -r\s+\d+", "", x)
                x = x.replace("%%R", "%%R -r 120 ")
            return x

        # Write the file out again
        with open(ff, "w") as file:
            file.write(filedata)

    # fix the toc using the function

    fix_toc(concise = concise)

    for ff in glob.glob(f"book/notebooks/*.ipynb"):
        ff_clean = ff.replace(".ipynb", ".py")
        if os.path.exists(ff_clean):
            os.remove(ff_clean)

    # move pml_logo to book directory

    shutil.copyfile(
        importlib.resources.files(__name__).joinpath("data/pml_logo.jpg"), f"pml_logo.jpg"
    )

    os.system(f"jupyter-book build  book/")
    import os

    stamps = [
        os.path.basename(x) for x in glob.glob(f"book/notebooks/.trackers/*")
    ]
    stamps.append("nctoolkit_rwi_uhosarcenctoolkittmp")

    delete = []
    for x in stamps:
        delete += glob.glob("/tmp/*" + x + "*")

    for ff in delete:
        if os.path.exists(ff):
            if "nctoolkit" in x:
                os.remove(ff)

    out_ff = f"book/_build/html/index.html"

    # create a symlink to the html file
    if os.path.exists("validation_report.html"):
        os.remove("validation_report.html")
    os.symlink(f"book/_build/html/index.html", "validation_report.html")
    webbrowser.open(
        "file://" + os.path.abspath(f"book/_build/html/index.html")
    )


def rebuild():
    """
    Rebuild the validation report after modifying notebooks.
    Use this if you have modified the notebooks generated and want to create a new validation report.

    Parameters
    ----------
    build : str
        The type of the existing build. Default is None. Options are "html" or "pdf"
    """
    # add a deprecation notice

    os.system(f"jupyter-book build book/")

    webbrowser.open(
        "file://" + os.path.abspath(f"book/_build/html/index.html")
    )




try:
    from importlib.metadata import version as _version
except ImportError:
    from importlib_metadata import version as _version

try:
    __version__ = _version("oceanval")
except Exception:
    __version__ = "999"


def compare(model_dict=None):
    """
    Compare pre-validated simulations.
    This function will compare the validation output from two simulations.

    Parameters
    ----------
    model_dict : dict
        A dictionary of model names and the paths to the validation output. Default is None.
        Example: {"model1": "/path/to/model1", "model2": "/path/to/model2"}
        If the models have different grids, put the model with the smallest grid first.


    """
    if os.path.exists("book"):
        # get user input to decide if it should be removed
        user_input = input(
            "book directory already exists. This will be emptied and replaced. Do you want to proceed? (y/n): "
        )
        if user_input.lower() == "y":
            while True:
                files = glob.glob("book/**/**/**", recursive=True)
                # list all files in book, recursively
                for ff in files:
                    if ff.startswith("book"):
                        try:
                            os.remove(ff)
                        except:
                            pass
                files = glob.glob("book/**/**/**", recursive=True)
                # only list files
                files = [x for x in files if os.path.isfile(x)]
                if len(files) == 0:
                    break
        else:
            print("Exiting")
            return None

    # make a folder called book/compare

    if not os.path.exists("book/compare"):
        # create directory recursively
        os.makedirs("book/compare")

    # copy the pml logo
    shutil.copyfile(
        importlib.resources.files(__name__).joinpath("data/pml_logo.jpg"),
        "book/pml_logo.jpg",
    )

    # move toc etc to book/compare

    data_path = importlib.resources.files(__name__).joinpath("data/_toc.yml")

    out = "book/compare/" + os.path.basename(data_path)

    shutil.copyfile(data_path, out)

    fix_toc_comparison()

    data_path = importlib.resources.files(__name__).joinpath("data/requirements.txt")

    out = "book/compare/" + os.path.basename(data_path)

    shutil.copyfile(data_path, out)

    data_path = importlib.resources.files(__name__).joinpath("data/intro.md")

    out = "book/compare/" + os.path.basename(data_path)

    shutil.copyfile(data_path, out)

    # copy config

    data_path = importlib.resources.files(__name__).joinpath("data/_config.yml")

    out = "book/compare/" + os.path.basename(data_path)

    shutil.copyfile(data_path, out)

    # copy the comparison_seasonal notebook

    # make sure the directory exists

    if not os.path.exists("book/compare/notebooks"):
        # create directory recursively
        os.makedirs("book/compare/notebooks")

    file1 = importlib.resources.files(__name__).joinpath("data/comparison_seasonal.ipynb")
    if len(glob.glob("book/compare/notebooks/*comparison_seasonal.ipynb")) == 0:
        shutil.copyfile(file1, "book/compare/notebooks/comparison_seasonal.ipynb")

    # copy comparison_overall notebook

    file1 = importlib.resources.files(__name__).joinpath("data/comparison_overall.ipynb")

    if len(glob.glob("book/compare/notebooks/*comparison_overall.ipynb")) == 0:
        shutil.copyfile(file1, "book/compare/notebooks/comparison_overall.ipynb")

    model_dict_str = str(model_dict)

    with open("book/compare/notebooks/comparison_seasonal.ipynb", "r") as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace("model_dict_str", model_dict_str)

    # Write the file out again

    with open("book/compare/notebooks/comparison_seasonal.ipynb", "w") as file:
        file.write(filedata)

    # now sort out the comparison_spatial notebook

    file1 = importlib.resources.files(__name__).joinpath("data/comparison_spatial.ipynb")
    if len(glob.glob("book/compare/notebooks/*comparison_spatial.ipynb")) == 0:
        shutil.copyfile(file1, "book/compare/notebooks/comparison_spatial.ipynb")

    model_dict_str = str(model_dict)

    with open("book/compare/notebooks/comparison_spatial.ipynb", "r") as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace("model_dict_str", model_dict_str)

    # Write the file out again

    with open("book/compare/notebooks/comparison_spatial.ipynb", "w") as file:
        file.write(filedata)

    # move the regional book

    file1 = importlib.resources.files(__name__).joinpath("data/comparison_regional.ipynb")
    if len(glob.glob("book/compare/notebooks/*comparison_regional.ipynb")) == 0:
        shutil.copyfile(file1, "book/compare/notebooks/comparison_regional.ipynb")

    model_dict_str = str(model_dict)

    with open("book/compare/notebooks/comparison_regional.ipynb", "r") as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace("model_dict_str", model_dict_str)

    # Write the file out again

    with open("book/compare/notebooks/comparison_regional.ipynb", "w") as file:
        file.write(filedata)

    # now to comparison_bias

    file1 = importlib.resources.files(__name__).joinpath("data/comparison_bias.ipynb")

    if len(glob.glob("book/compare/notebooks/*comparison_bias.ipynb")) == 0:
        shutil.copyfile(file1, "book/compare/notebooks/comparison_bias.ipynb")

    model_dict_str = str(model_dict)

    with open("book/compare/notebooks/comparison_bias.ipynb", "r") as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace("model_dict_str", model_dict_str)

    # Write the file out again

    with open("book/compare/notebooks/comparison_bias.ipynb", "w") as file:
        file.write(filedata)

    # figure out if both simulations have point data

    i = 0

    if i == 0:
        for ss in [ "bottom"]:
            file1 = importlib.resources.files(__name__).joinpath("data/comparison_point.ipynb")

            if (
                len(glob.glob(f"book/compare/notebooks/*comparison_point_{ss}.ipynb"))
                == 0
            ):
                shutil.copyfile(
                    file1, f"book/compare/notebooks/comparison_point_{ss}.ipynb"
                )

            model_dict_str = str(model_dict)

            with open(
                f"book/compare/notebooks/comparison_point_{ss}.ipynb", "r"
            ) as file:
                filedata = file.read()

            # Replace the target string
            filedata = filedata.replace("model_dict_str", model_dict_str)

            # Write the file out again

            with open(
                f"book/compare/notebooks/comparison_point_{ss}.ipynb", "w"
            ) as file:
                file.write(filedata)
            # replace layer in the notebook with ss
            with open(
                f"book/compare/notebooks/comparison_point_{ss}.ipynb", "r"
            ) as file:
                filedata = file.read()

            # Replace the target string
            filedata = filedata.replace("layer", ss)

            # Write the file out again

            with open(
                f"book/compare/notebooks/comparison_point_{ss}.ipynb", "w"
            ) as file:
                file.write(filedata)


    # sync the notebooks

    os.system("jupytext --set-formats ipynb,py:percent book/compare/notebooks/*.ipynb")

    add_chunks()

    # replace the test status in the notebooks
    books = glob.glob("book/compare/notebooks/*.py")
    for book in books:
        with open(book, "r") as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace("the_test_status", "False")

        # Write the file out again
        with open(book, "w") as file:
            file.write(filedata)

    # fix the chunks
    os.system("jupytext --sync book/compare/notebooks/*.ipynb")

    # loop through notebooks and change fast_plot_value to fast_plot

    for ff in glob.glob("book/compare/notebooks/*.ipynb"):
        with open(ff, "r") as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace("fast_plot_value", "False")

        # Write the file out again
        with open(ff, "w") as file:
            file.write(filedata)

    os.system("jupyter-book build book/compare/")
    import webbrowser


    webbrowser.open("file://" + os.path.abspath("book/compare/_build/html/index.html"))
