ecoval recipes for NECCTON
============


Validating the new NECCTON products
---------------------------

NECCTON needs to produce DOC, POC, mesozooplankton, near-bottom pH and oxygen, as well as benthic biomass and carbon.

These are best validated as follows:

    - POC and DOC are best validated with point data from ICES for the sea surface
    - Mesozooplankton is best validated with CPR data for the surface
    - Near-bottom pH and oxygen are best validated with point data from ICES for the bottom
    - Benthic biomass and carbon are best validated with point data from NSBS and Diesing 

Modify the following script to do this. 


.. code:: ipython3

   import ecoval
   surface = {"gridded":None, "point":["mesozoo", "doc", "poc"]}
   bottom = ["ph", "oxygen"]
   benthic = ["benbio", "carbon"]
   ecoval.matchup("/data/proteus2/scratch/hpo/NECCTON_tests/new_baseline",
       cores = 6, start = 1998, end = 2000,
       bottom=bottom,
       benthic = None,
       overwrite=True, n_dirs_down=2,
       surface = surface,
       point_time_res = ["month"])
   ecoval.validate()

Once the full simulation is available `point_time_res` should be set to `["year","month", "day"]` to get the full time series of validation data.

Doing a comprehensive validation
---------------------------

If you want to do the most comprehensive validation possible, you can set `everything = True` in the default matchup function.
Note: this might take a long time to run as it will need to do 3D validation for all available ICES matchups.

.. code:: ipython3

   import ecoval
   surface = {"gridded":None, "point":["mesozoo", "doc", "poc"]}
   bottom = ["ph", "oxygen"]
   ecoval.matchup("/data/proteus2/scratch/hpo/NECCTON_tests/new_baseline",
       cores = 6, start = 1998, end = 2000,
       overwrite=True, n_dirs_down=2,
       everything = True,
       point_time_res = ["year","month", "day"])
   ecoval.validate()

