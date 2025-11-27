Data Recipes
=============

To make life easier, oceanVal provides a number of built in recipes, which will allow you to easily validate common oceanic varibles from data that is downloadable.

**Note**: recipes are only available for gridded data at present.


Overview
--------

This is carried out using the ``recipe`` parameter in the ``add_gridded_comparison`` function, as follows:


.. code-block:: python

   from oceanval.parsers import definitions
   
   # Using a recipe in add_gridded_comparison
   definitions.add_gridded_comparison(
       model_variable="votemper",
       recipe={"temperature": "cobe2"}
   )

This is a minimalist example, where you have said you want to matchup temperature from the [COBE2](https://psl.noaa.gov/thredds/dodsC/Datasets/COBE2/sst.mon.mean.nc) sea surface temperature dataset with the model temperature, with variable name "votemper".

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

**Variables**: nitrate, phosphate, oxygen, silicate, temperature, salinity

**Recipes**: {"nitrate": "woa23"}, {"phosphate": "woa23"}, {"oxygen": "woa23"}, {"silicate": "woa23"}, {"temperature": "woa23"}, {"salinity
.. Units

Data is stored in the following units:

    **Nitrate**: micromoles per kg (µmol/kg)

    **Phosphate**: micromoles per kg (µmol/kg)

    **Oxygen**: micromoles per kilogram (µmol/kg)

    **Silicate**: micromoles per kg (µmol/kg)

    **Temperature**: degrees Celsius (°C)

    **Salinity**: practical salinity units (PSU)

**URL**: https://www.ncei.noaa.gov/products/world-ocean-atlas 

**Note**: temperature and salinity are available for different decadal climatologies. You must therefore specify start and end years when using these recipes to ensure the correct data is downloaded. 

The climatological periods available are:

* 1955-1964

* 1965-1974

* 1975-1984

* 1985-1994

* 1995-2004

* 2005-2014

* 2015-2022

The start and end provided must fall within one of these periods. 
For example, if you want to validate against the 1995-2004 climatology, you would set start = 1995 and end = 2004 when calling the ``add_gridded_comparison`` function, as follows:

.. code-block:: python

   definitions.add_gridded_comparison(
       model_variable="temp",
       recipe={"temperature": "woa23"},
       start = 1995,
       end = 2004
   )






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

    **Phosphate**: millimoles per liter (mmol/L)

    **Nitrate**: millimoles per liter (mmol/L)

    **Ammonium**: millimoles per liter (mmol/L)

    **Silicate**: millimoles per liter (mmol/L)

    **Chlorophyll**: milligrams per cubic meter (mg/m³)

    **Oxygen**: milliliters per liter (ml/L)

    **Temperature**: degrees Celsius (°C)

    **Salinity**: practical salinity units (PSU)