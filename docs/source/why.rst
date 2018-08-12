Why this?
=========

Geography is the foundation of almost all civic data. This app models geographic data for U.S. political divisions, including states, congressional districts, counties and townships. It also loads geographic data sourced from U.S. Census cartographic boundary files into that database and builds out a full set of boundary files in TopoJSON format, which we use at POLITICO to create data maps.

In short, politico-civic-geography is a one-stop shop for creating and managing political geography and maps. That's why we use it as the basis for our election rig, dataviz apps and other political projects. With it we keep a consistent source of geographic data from the Census and can easily update across our applications each year when new boundary files are released.

politico-civic-geography borrows heavily from other specifications, especially the `Open Civic Data <https://opencivicdata.readthedocs.io/en/latest/>`_ project. It's also a central part of our larger `politico-civic <http://politico-civic.readthedocs.io/en/latest/>`_ project.
