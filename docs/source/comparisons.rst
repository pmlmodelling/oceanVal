Comparing simulation performance
================================

If you have validated two simulations, you can compare them using the `oceanval.compare` function.

This is a simple function that just requires a dicationary with names of the simulations and the directories containing their validation output.

You would set this up as follows:

.. code-block:: python

    import oceanval 

    oceanval.compare({
        "sim1": "/path/to/validation/sim1",
        "sim2": "/path/to/validation/sim2"
    })

This will carry out a comparison for the surface only, using gridded and point observations.

**Note**: This function requires that you have only validated each variable with a single observational data source.


