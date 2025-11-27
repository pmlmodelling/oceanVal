Data Recipes
=============

Overview
--------

The ``find_recipe`` function provides pre-configured data sources for common oceanographic variables. Recipes simplify the process of adding gridded comparisons by automatically configuring data sources, metadata, and access parameters.

Function Usage
--------------

.. code-block:: python

   from oceanval.parsers import definitions
   
   # Using a recipe in add_gridded_comparison
   definitions.add_gridded_comparison(
       model_variable="temp",
       recipe={"temperature": "cobe2"}
   )

The recipe dictionary must contain exactly one key-value pair, where:

* **Key**: Variable name (e.g., "temperature", "nitrate")
* **Value**: Data source identifier (e.g., "cobe2", "woa23", "nsbc")

Available Recipes
-----------------

COBE2 - Sea Surface Temperature
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Source**: COBE-SST 2 (NOAA Physical Sciences Laboratory)

**Variables**: temperature

**Configuration**:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Parameter
     - Value
   * - Source
     - COBE2
   * - Data Type
     - Sea surface temperature
   * - Climatology
     - False (time series data)
   * - Vertical
     - False (surface only)
   * - Access Method
     - THREDDS
   * - URL
     - https://psl.noaa.gov/thredds/dodsC/Datasets/COBE2/sst.mon.mean.nc

**Citation**:

   COBE-SST 2 and Sea Ice data provided by the NOAA PSL, Boulder, Colorado, USA, from their website at https://psl.noaa.gov/data/gridded/data.cobe2.html.

**Usage Example**:

.. code-block:: python

   definitions.add_gridded_comparison(
       model_variable="temp",
       recipe={"temperature": "cobe2"}
   )


WOA23 - World Ocean Atlas 2023
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Source**: NOAA World Ocean Atlas 2023

**Variables**: nitrate

**Configuration**:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Parameter
     - Value
   * - Source
     - WOA23
   * - Data Type
     - Dissolved inorganic nutrients
   * - Climatology
     - True (monthly climatology)
   * - Vertical
     - Automatic detection
   * - Access Method
     - THREDDS
   * - URL Pattern
     - Monthly files: woa23_all_n{MM}_01.nc (MM = 01-12)

**Citation**:

   Garcia, H.E., C. Bouchard, S.L. Cross, C.R. Paver, Z. Wang, J.R. Reagan, T.P. Boyer, R.A. Locarnini, A.V. Mishonov, O. Baranova, D. Seidov, and D. Dukhovskoy. World Ocean Atlas 2023, Volume 4: Dissolved Inorganic Nutrients (phosphate, nitrate, silicate). A. Mishonov, Tech. Ed. NOAA Atlas NESDIS 92, doi.org/10.25923/39qw-7j08

**Usage Example**:

.. code-block:: python

   definitions.add_gridded_comparison(
       model_variable="no3",
       recipe={"nitrate": "woa23"}
   )


NSBC - North Sea Biogeochemical Climatology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Source**: North Sea Biogeochemical Climatology (University of Hamburg)

**Variables**: ammonium, nitrate, phosphate, silicate, chlorophyll, oxygen, temperature, salinity

**Configuration**:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Parameter
     - Value
   * - Source
     - NSBC
   * - Data Type
     - Biogeochemical variables
   * - Climatology
     - True (climatological monthly mean, 1960-2014)
   * - Vertical
     - Automatic detection
   * - Access Method
     - THREDDS
   * - Resolution
     - 0.25° x 0.25°
   * - URL Pattern
     - NSBC_Level3_{variable}__UHAM_ICDC__v1.1__0.25x0.25deg__OAN_1960_2014.nc

**Citation**:

   Hinrichs, Iris; Gouretski, Viktor; Paetsch, Johannes; Emeis, Kay; Stammer, Detlef (2017). North Sea Biogeochemical Climatology (Version 1.1).

**Usage Example**:

.. code-block:: python

   # Any of the 8 supported variables
   definitions.add_gridded_comparison(
       model_variable="chl",
       recipe={"chlorophyll": "nsbc"}
   )
   
   definitions.add_gridded_comparison(
       model_variable="no3",
       recipe={"nitrate": "nsbc"}
   )


Variable Metadata
-----------------

When using recipes, the following metadata is automatically assigned based on the variable name:

Temperature
~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Value
   * - short_name
     - sea temperature
   * - long_name
     - sea water temperature
   * - short_title
     - Temperature

Salinity
~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Value
   * - short_name
     - salinity
   * - long_name
     - sea water salinity
   * - short_title
     - Salinity

Chlorophyll
~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Value
   * - short_name
     - chlorophyll concentration
   * - long_name
     - chlorophyll a concentration
   * - short_title
     - Chlorophyll

Oxygen
~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Value
   * - short_name
     - dissolved oxygen
   * - long_name
     - dissolved oxygen concentration
   * - short_title
     - Oxygen

Nitrate
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Value
   * - short_name
     - nitrate concentration
   * - long_name
     - nitrate concentration
   * - short_title
     - Nitrate

Ammonium
~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Value
   * - short_name
     - ammonium concentration
   * - long_name
     - ammonium concentration
   * - short_title
     - Ammonium

Phosphate
~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Value
   * - short_name
     - phosphate concentration
   * - long_name
     - phosphate concentration
   * - short_title
     - Phosphate

Silicate
~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Value
   * - short_name
     - silicate concentration
   * - long_name
     - silicate concentration
   * - short_title
     - Silicate


Recipe Compatibility Matrix
----------------------------

This table shows which variables are supported by each recipe:

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 20

   * - Variable
     - COBE2
     - WOA23
     - NSBC
   * - temperature
     - ✓
     - 
     - ✓
   * - salinity
     - 
     - 
     - ✓
   * - chlorophyll
     - 
     - 
     - ✓
   * - oxygen
     - 
     - 
     - ✓
   * - nitrate
     - 
     - ✓
     - ✓
   * - ammonium
     - 
     - 
     - ✓
   * - phosphate
     - 
     - 
     - ✓
   * - silicate
     - 
     - 
     - ✓


Complete Usage Example
----------------------

Here's a complete example showing how to use recipes for multiple variables:

.. code-block:: python

   from oceanval.parsers import definitions
   
   # Temperature from COBE2
   definitions.add_gridded_comparison(
       model_variable="temp",
       recipe={"temperature": "cobe2"}
   )
   
   # Nitrate from WOA23
   definitions.add_gridded_comparison(
       model_variable="no3",
       recipe={"nitrate": "woa23"}
   )
   
   # Multiple variables from NSBC
   definitions.add_gridded_comparison(
       model_variable="chl",
       recipe={"chlorophyll": "nsbc"}
   )
   
   definitions.add_gridded_comparison(
       model_variable="oxy",
       recipe={"oxygen": "nsbc"}
   )
   
   definitions.add_gridded_comparison(
       model_variable="sal",
       recipe={"salinity": "nsbc"}
   )


Error Handling
--------------

The ``find_recipe`` function validates inputs and raises errors for invalid configurations:

Invalid Recipe Dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ERROR: Multiple keys
   recipe = {"temperature": "cobe2", "salinity": "nsbc"}
   # Raises: ValueError: Recipe dictionary must have exactly one key

Invalid Variable-Source Combination
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ERROR: COBE2 only supports temperature
   recipe = {"salinity": "cobe2"}
   # Raises: ValueError: Recipe value cobe2 is not valid for recipe name salinity

Case Sensitivity
~~~~~~~~~~~~~~~~

Both variable names and source identifiers are case-insensitive:

.. code-block:: python

   # These are equivalent
   recipe = {"temperature": "cobe2"}
   recipe = {"Temperature": "COBE2"}
   recipe = {"TEMPERATURE": "CoBe2"}


Advanced Features
-----------------

Recipe Output Structure
~~~~~~~~~~~~~~~~~~~~~~~

The ``find_recipe`` function returns a dictionary with the following structure:

.. code-block:: python

   {
       "obs_path": str or list,      # URL(s) to data
       "source": str,                 # Source identifier
       "source_info": str,            # Citation/description
       "name": str,                   # Variable name
       "thredds": bool,               # THREDDS access flag
       "climatology": bool,           # Climatology flag
       "vertical": bool or None,      # Vertical dimension flag
       "short_name": str,             # Short variable name
       "long_name": str,              # Long variable name
       "short_title": str             # Display title
   }

Combining Recipes with Custom Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use a recipe and override specific parameters:

.. code-block:: python

   # Use recipe but customize time range
   definitions.add_gridded_comparison(
       model_variable="temp",
       recipe={"temperature": "cobe2"},
       start=2000,
       end=2020,
       obs_multiplier=1.0,
       obs_adder=273.15  # Convert Celsius to Kelvin
   )


Notes and Best Practices
-------------------------

1. **THREDDS Access**: All recipes use THREDDS for data access, requiring an internet connection during validation.

2. **Climatology**: NSBC and WOA23 provide climatological data, while COBE2 provides time series data. Ensure your validation approach matches the data type.

3. **Regional Coverage**: NSBC data is specifically for the North Sea region. Ensure your model domain overlaps with the data coverage.

4. **Data Updates**: Recipe URLs point to specific data versions. Check data provider websites for newer versions.

5. **Model Variable Names**: The ``model_variable`` parameter must match the actual variable name in your model output files.

6. **Unit Conversion**: Use ``obs_multiplier`` and ``obs_adder`` parameters if your model uses different units than the observational data.


See Also
--------

* :doc:`api` - Full API documentation for ``add_gridded_comparison``
* :doc:`examples` - More detailed usage examples
* :doc:`installing` - Installation instructions
