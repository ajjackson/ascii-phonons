
Configuration files
===================

Plain-text configuration files are used to provide supporting data and allow per-user tweaking.
In addition to the provided files **settings.conf** and **elements.conf**, which are found in the ``addons/vsim2blender`` folder of the project, the user can maintain their own configuration file in this format. When this file is provided via the ``--config`` flag of the :ref:`CLI` or using the :func:`vsim2blender.read_config` function of the Python library, user settings will take precedent over the defaults.

The format of this files is a typical plain text .ini format and is implemented with `configparser <https://docs.python.org/3.5/library/configparser.html>`_.
Parameters are grouped into *sections* with a header in square brackets; the parameters themselves are separated from their values with ``=`` or ``:`` markers

::

   [header]
   
   Like = this
   Or: this

   # And comments are indicated with a '#'
   ; or a ';'

Parameters and section headers are *case-sensitive*, and are lower-case except for the names of elements, which follow their usual capitalisation rule.

Settings
--------

**settings.conf**, which lies inside the **vsim2blender** package, contains default settings that are not related to specific elements. 

::

   [general]
   box_thickness = 5
   outline_thickness = 3

   [colours]
   background = 0.5 0.5 0.5
   box = 1. 1. 1.
   outline = 0. 0. 0.
  
Elements
--------

Data for each element is included in the ``elements.conf``
configuration file.  Relative atomic masses are drawn from standard
reference data. [1]_ Where this reference gives a range and/or the
relative abundance of isotopes is unknown, a simple mean was taken.

::

    [masses]
    C = 12.0106   # The mass of carbon is a floating-point number in a.m.u.

Atomic radii are drawn from a recent study encompassing elements with atomic numbers up to 96. [2]_

::

    [radii]
    Ac = 2.15  # The covalent radius of Ac is a floating-point number in angstroms

Colours are assigned somewhat arbitrarily for a handful of elements
which have been used in WMD Group publications. Suggestions are
welcome for a more mainstream pallette. The values are RGB tuples, with values ranging from 0 to 1.

::

    [colours]
    Cu = 0.8 0.3 0.1

User configuration
------------------
An example user configuration file, with an alternative colour scheme, is included in the main project directory as **example.conf**. Note that the colour information for elements and for other parts of the image may be mixed freely.

    
.. [1] www.nist.gov/pml/data/comp  J. S. Coursey, D. J. Schwab, J. J. Tsai, and R. A. Dragoset, NIST Physical Measurement Laboratory
.. [2] http://dx.doi.org/10.1039/B801115J B. Cordero *et al.* (2008) *Dalton Trans.* **2008** (21) 2832-2838

