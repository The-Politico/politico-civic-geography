Why this?
=========

Geography is the foundation of almost all civic data. This app models geographic data for U.S. political divisions, including states, congressional districts, counties and townships. It also includes loaders to bootstrap your database, sourced from U.S. Census cartographic boundary files, and exporters to build out a full set of boundary files in TopoJSON format, which we use at POLITICO to create data maps.

In short, politico-civic-geography is a one-stop shop for creating and managing political geography and maps. That's why we use it as the basis for our election rig, dataviz apps and other political projects. With it we keep a consistent source of geographic data from the Census and can easily update across our applications each year when new boundary files are released.

While politico-civic-geography is focused primarily on U.S. political divisions, its data model borrows heavily from more generic specifications, especially the `Open Civic Data <https://opencivicdata.readthedocs.io/en/latest/>`_ project. (We welcome contributions of loaders for other political contexts!)

This app is part of our larger `politico-civic <http://politico-civic.readthedocs.io/en/latest/>`_ project. `Read the docs <http://politico-civic.readthedocs.io/en/latest/why.html>`_ for more information.
