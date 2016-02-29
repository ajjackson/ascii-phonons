.. _gui:

Graphical user interface
========================

A simple graphical user interface (GUI) is available, including a "preview" window.
At this time a useful subset of features is implemented.

.. figure:: ../images/gui.png
   :align: center

To launch the GUI, which is compatible with Python 3 and Python 2.7, simply run **scripts/ascii-phonons-gui**.

Dependencies
------------

- Tkinter is used to draw the GUI. This is included in standard Python distributions.

- The "PIL" module is loaded to handle the preview rendering. This dependency is best satisfied by installing "Pillow". On Linux, the tk imaging part of this is often packaged separately, with names like `python-imaging-tk`.
