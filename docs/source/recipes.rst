Data Recipes
=============

To make life easier, oceanVal provides a number of built in recipes, which will allow you to easily validate common oceanic varibles from data that is downloadable.

**Note**: recipes are only available for gridded data at present.


Overview
--------

This is carried out using the ``recipe`` parameter in the ``add_gridded_comparison`` function, as follows:

Function Usag

.. code-block:: python

   from oceanval.parsers import definitions
   
   # Using a recipe in add_gridded_comparison
   definitions.add_gridded_comparison(
       model_variable="votemper",
       recipe={"temperature": "cobe2"}
   )

This is a minimalist example, where you have said you want to matchup temperature from the COBE2 sea surface temperature dataset with the model temperature, with variable name "votemper".

The recipe dictionary must contain exactly one key-value pair, where:

* **Key**: Variable name (e.g., "temperature", "nitrate")
* **Value**: Data source identifier (e.g., "cobe2", "woa23", "nsbc")


Available recipes for global gridded data
-----------------

COBE2 - Sea Surface Temperature
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Recipe**: ["temperature": "cobe2"] 

**Source**: COBE-SST 2 (NOAA Physical Sciences Laboratory)

**URL**: https://psl.noaa.gov/thredds/dodsC/Datasets/COBE2/sst.mon.mean.nc

**Usage Example**:

.. code-block:: python

   definitions.add_gridded_comparison(
       model_variable="temp",
       recipe={"temperature": "cobe2"}
   )

COBE2 data is stored in the following units:

    temperature: degrees Celsius (°C)


WOA23 - World Ocean Atlas 2023
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Source**: NOAA World Ocean Atlas 2023

**Variables**: nitrate, phosphate, oxygen

**Recipes**: {"nitrate": "woa23"}, {"phosphate": "woa23"}, {"oxygen": "woa23"}
.. Units

Data is stored in the following units:

    **nitrate**: micromoles per liter (µmol/L)

    **phosphate**: micromoles per liter (µmol/L)

    **oxygen**: micromoles per kilogram (µmol/kg)

**URL**: https://www.ncei.noaa.gov/products/world-ocean-atlas 


**Usage Example**:

.. code-block:: python

   definitions.add_gridded_comparison(
       model_variable="no3",
       recipe={"nitrate": "woa23"}
   )

This data is vertically resolved, so if you want vertically resolved validation you will need to modify things as follows:

.. code-block:: python

   definitions.add_gridded_comparison(
       model_variable="no3",
       recipe={"nitrate": "woa23"},
       vertical = True
   )


Available recipes for the northwest European shelf
-----------------

NSBC - North Sea Biogeochemical Climatology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Source**: North Sea Biogeochemical Climatology (University of Hamburg)

**Variables**: ammonium, nitrate, phosphate, silicate, chlorophyll, oxygen, temperature, salinity

**URL**: https://www.hereon.de/en/institute/coastal-research/projects/north-sea-biogeochemical-climatology-nsbc.php


**Usage Examples**:

.. code-block:: python

   definitions.add_gridded_comparison(
       model_variable="chl",
       recipe={"chlorophyll": "nsbc"}
   )
   
   definitions.add_gridded_comparison(
       model_variable="no3",
       recipe={"nitrate": "nsbc"}
   )

This data is vertically resolved, so if you want vertically resolved validation you will need to modify things as follows:

.. code-block:: python

   definitions.add_gridded_comparison(
       model_variable="no3",
       recipe={"nitrate": "nsbc"},
       vertical = True
   )


NSBC data is stored in the following units:

    **phosphate**: millimoles per liter (mmol/L)

    **nitrate**: millimoles per liter (mmol/L)

    **ammonium**: millimoles per liter (mmol/L)

    **silicate**: millimoles per liter (mmol/L)

    **chlorophyll**: milligrams per cubic meter (mg/m³)

    **oxygen**: milliliters per liter (ml/L)

    **temperature**: degrees Celsius (°C)

    **salinity**: practical salinity units (PSU)