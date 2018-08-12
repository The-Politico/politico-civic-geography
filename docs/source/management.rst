.. _management:

Management
==========

:code:`bootstrap_geography`
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This command will download shapefiles from the U.S. Census Bureau, process them and create a complete set of Geography and Geometry fixtures for states, congressional districts, counties and townships in your database.

.. code-block:: none

  usage: manage.py bootstrap_geography [-h] [--year YEAR] [--congress CONGRESS]
                                       [--nationThreshold NATIONTHRESHOLD]
                                       [--stateThreshold STATETHRESHOLD]
                                       [--districtThreshold DISTRICTTHRESHOLD]
                                       [--countyThreshold COUNTYTHRESHOLD]
                                       [--version] [-v {0,1,2,3}]
                                       [--settings SETTINGS]
                                       [--pythonpath PYTHONPATH] [--traceback]
                                       [--no-color]

  Downloads and bootstraps geographic data for states, congressional districts,
  counties and townships from the U.S. Census Bureau simplified cartographic
  boundary files.

  optional arguments:
    -h, --help            show this help message and exit
    --year YEAR           Specify year of shapefile series (default, 2017)
    --congress CONGRESS   Specify congress of district shapefile series
                          (default, 115)
    --nationThreshold NATIONTHRESHOLD
                          Simplification threshold value for nation topojson
                          (default, 0.005)
    --stateThreshold STATETHRESHOLD
                          Simplification threshold value for state topojson
                          (default, 0.05)
    --districtThreshold DISTRICTTHRESHOLD
                          Simplification threshold value for district topojson
                          (default, 0.08)
    --countyThreshold COUNTYTHRESHOLD
                          Simplification threshold value for county topojson
                          (default, 0.075)
    --version             show program's version number and exit
    -v {0,1,2,3}, --verbosity {0,1,2,3}
                          Verbosity level; 0=minimal output, 1=normal output,
                          2=verbose output, 3=very verbose output
    --settings SETTINGS   The Python path to a settings module, e.g.
                          "myproject.settings.main". If this isn't provided, the
                          DJANGO_SETTINGS_MODULE environment variable will be
                          used.
    --pythonpath PYTHONPATH
                          A directory to add to the Python path, e.g.
                          "/home/djangoprojects/myproject".
    --traceback           Raise on CommandError exceptions
    --no-color            Don't colorize the command output.


Overriding bootstrapped geometry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In some cases, we need to overwrite geometry. In those cases, we generally package source shapefiles with this module and write an additional management command to be run *after* bootstrapping geography from the Census.

Those commands are called by the format: :code:`bootstrap_geom_<id>`


:code:`bake_geography`
~~~~~~~~~~~~~~~~~~~~~~

This command will export state and congressional district boundary files in TopoJSON to an AWS S3 bucket.

.. code-block:: none

  usage: manage.py bake_geography [-h] [--year YEAR] [--version] [-v {0,1,2,3}]
                                  [--settings SETTINGS]
                                  [--pythonpath PYTHONPATH] [--traceback]
                                  [--no-color]
                                  states [states ...]

  Uploads topojson files by state and district to an Amazon S3 bucket.

  positional arguments:
    states                States to export by FIPS code. Use 00 to export all
                          geographies.

  optional arguments:
    -h, --help            show this help message and exit
    --year YEAR           Specify year of shapefile series (default, 2017)
    --version             show program's version number and exit
    -v {0,1,2,3}, --verbosity {0,1,2,3}
                          Verbosity level; 0=minimal output, 1=normal output,
                          2=verbose output, 3=very verbose output
    --settings SETTINGS   The Python path to a settings module, e.g.
                          "myproject.settings.main". If this isn't provided, the
                          DJANGO_SETTINGS_MODULE environment variable will be
                          used.
    --pythonpath PYTHONPATH
                          A directory to add to the Python path, e.g.
                          "/home/djangoprojects/myproject".
    --traceback           Raise on CommandError exceptions
    --no-color            Don't colorize the command output.
