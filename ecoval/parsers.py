import nctoolkit as nc
import re
import warnings
from ecoval.session import session_info

bad_conc_vars = ["medium", "pod", "size"]


def generate_mapping(ds):
    """
    Generate mapping of model and observational variables
    """

    candidate_variables = [
        "temperature",
        "salinity",
        "oxygen",
        "chlorophyll",
        "phosphate",
        "silicate",
        "nitrate",
        "ph",
        "ammonium",
        "co2flux",
        "pco2",
        "doc",
        "poc",
        "benbio",
        "alkalinity",
        "micro",
        "nano",
        "pico",
        "mesozoo",
        "spm",
        "kd",
    ]
    ds1 = nc.open_data(ds[0], checks=False)
    ds_contents = ds1.contents

    ds_contents["long_name"] = [str(x) for x in ds_contents["long_name"]]

    ds_contents_top = ds_contents.query("nlevels == 1").reset_index(drop=True)
    ds_contents = ds_contents.query("nlevels > 1").reset_index(drop=True)
    n_levels = ds_contents.nlevels.max()
    if n_levels > session_info["n_levels"]:
        session_info["n_levels"] = n_levels
    # number of rows in ds_contents
    if len(ds_contents) == 0:
        ds_contents = ds_contents_top

    model_dict = {}
    for vv in candidate_variables:
        vv_check = vv

        if vv != "ph":
            the_vars = [
                x
                for x in [str(x) for x in ds_contents.long_name]
                if vv_check.lower() in x.lower()
                and "benthic" not in x.lower()
                and "river" not in x.lower()
            ]
        if vv == "temperature":
            the_vars = [
                x
                for x in [str(x) for x in ds_contents.long_name]
                if vv_check.lower() in x.lower()
                and "benthic" not in x.lower()
                and "air" not in x.lower()
                and "river" not in x.lower()
            ]
        if vv == "spm":
            the_vars = [
                x for x in ds_contents.long_name if "chloroph" in x and ("micro" in x)
            ]
        if vv == "doc":
            # doc = [x for x in ds.contents.long_name if "arbon" in x and "iss" in x and " organic" in x and "benthic" not in x]
            the_vars = [
                x
                for x in ds_contents.long_name
                if "arbon" in x
                and "iss" in x
                and " organic" in x
                and "benthic" not in x
            ]
            vars_2 = [
                x
                for x in ds_contents.long_name
                if "photolabile" in str(x) and "carbon" in str(x)
            ]
            if len(vars_2) > 0:
                the_vars += vars_2

            the_vars = [x for x in the_vars if " loss " not in x]
            the_vars = [x for x in the_vars if "depth" not in x]

        if vv == "benbio":
            the_vars = [
                x
                for x in ds_contents_top.long_name
                if "carbon" in x
                and ("feeder" in x.lower() or "predator" in x.lower())
                and "uptake" not in x.lower()
                and "penetr" not in x.lower()
            ]

        if vv == "ph":
            the_vars = [
                x
                for x in ds_contents.long_name
                if ("pH" in x)
                or (" ph " in x)
                and "benthic" not in x.lower()
                and "river" not in x.lower()
            ]
            if len(the_vars) == 0:
                if len(ds_contents.query("variable == 'ph'")) > 0:
                    the_vars = list(ds_contents.query("variable == 'ph'").long_name)

        if vv == "co2flux":
            the_vars = [
                x
                for x in ds_contents_top.long_name
                if "co2" in x.lower()
                and "flux" in x.lower()
                and "river" not in x.lower()
            ]

        if vv == "pco2":
            the_vars = [
                x
                for x in ds_contents.long_name
                if "carbonate" in x.lower()
                and "partial" in x.lower()
                and "river" not in x.lower()
            ]

        if vv == "silicate":
            the_vars = [
                x
                for x in ds_contents.long_name
                if ("silicate" in x.lower() or "silicic" in x.lower())
                and "benthic" not in x.lower()
                and "river" not in x.lower()
            ]

            if len(the_vars) > 1:
                the_vars_2 = [
                    x
                    for x in ds_contents.long_name
                    if "benthic" not in x.lower() and "river" not in x.lower()
                ]
                the_vars_2 = [
                    x for x in the_vars_2 if re.match(r"silicate.silicate", x)
                ]
                if len(the_vars_2) == 1:
                    the_vars = the_vars_2

        if vv == "oxygen":
            the_vars = [
                x
                for x in ds_contents.long_name
                if "oxygen" in x.lower()
                and "benthic" not in x.lower()
                and "saturation" not in x.lower()
                and "util" not in x.lower()
                and "flux" not in x.lower()
                and "river" not in x.lower()
            ]

        if vv == "micro":
            the_vars = [
                x
                for x in ds_contents.long_name
                if "chloroph" in x and ("micro" in x or "diatom" in x)
            ]

        if vv == "mesozoo":
            the_vars = [
                x
                for x in ds_contents.long_name
                if "mesozoo" in x
                and "ingestion" not in x.lower()
                and "respiration" not in x.lower()
                and "mortality" not in x.lower()
                and "loss" not in x.lower()
            ]
        if vv == "kd":
            the_vars = [
                x
                for x in ds_contents.long_name
                if "atten" in x.lower() and "coeff" in x.lower()
            ]

        if vv == "nano":
            the_vars = [
                x
                for x in ds_contents.long_name
                if "chloroph" in x.lower() and "nano" in x
            ]

        if vv == "pico":
            the_vars = [
                x
                for x in ds_contents.long_name
                if "chloroph" in x.lower() and "pico" in x
            ]

        if vv == "doc":
            if len(the_vars) > 1:
                the_vars = [x for x in the_vars if "total" not in x.lower()]

        if vv == "chlorophyll":
            if len(the_vars) > 1:
                the_vars = [x for x in the_vars if "total" not in x.lower()]

        if vv in [ "benbio"]:
            model_vars = ds_contents_top.query("long_name in @the_vars").variable
        else:
            if vv != "co2flux" and vv != "pco2":
                model_vars = ds_contents.query("long_name in @the_vars").variable
            else:
                if vv == "co2flux":
                    model_vars = ds_contents_top.query(
                        "long_name in @the_vars"
                    ).variable
                else:
                    model_vars = ds_contents.query("long_name in @the_vars").variable

        add = True

        if len(model_vars) > 1 and vv not in [
            "doc",
            "chlorophyll",
            "benbio",
            "micro"
        ]:
            add = False

        if add:
            if len(model_vars) > 0:
                model_dict[vv] = "+".join(model_vars)
            else:

                if "nitrate" not in model_dict.keys() and vv == "nitrate":
                    if "ammonium" not in model_dict.keys():
                        df_nitrogen = (
                            ds_contents.query("long_name.str.contains('nitrogen')")
                            .query("long_name.str.contains('nutrient')")
                            .reset_index(drop=True)
                        )
                        if len(df_nitrogen) == 1:
                            model_dict["nitrate"] = df_nitrogen.variable[0]
                            warnings.warn(
                                "No nitrate variable found, using nitrogen nutrient variable"
                            )

                if vv not in model_dict.keys():
                    model_dict[vv] = None
    return model_dict
