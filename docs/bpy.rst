
Blender Interface
=================

The interface with Blender is managed as a Python add-on module :mod:`~vsim2blender`.
See the `module index <py-modindex.html>`_ for the documentation of these modules.
The :ref:`cli` works by generating a temporary script file and executing the script with Blender.
Advanced Blender users may prefer to directly import the ``vsim2blender`` module and use it with Blender's scripting tools.
The key plotting tools are all in :mod:`~vsim2blender.plotter`, with supporting functions in the other modules.

Top-level functions
-------------------

.. automodule:: vsim2blender
   :members:                


List of modules
---------------
.. toctree::
   :maxdepth: 2

   vsim2blender/arrows
   vsim2blender/ascii_importer
   vsim2blender/plotter
   vsim2blender/camera
