"""
.. module:: vsim2blender
   :platform: Blender add-on
   :synopsis: A module which interfaces with Blender to illustrate phonon modes.
              Includes importer from v_sim ascii files, and routines to build and render a model.

.. moduleauthor:: Adam J. Jackson

"""

bl_info = {
    "name": "ascii phonons",
    "description": "Generate phonon mode visualisations from ASCII input files",
    "author": "Adam J. Jackson",
    "version": (0,2,1),
    "blender": (2, 65, 0),
    "location": "",
    "category": "Import-Export",
    "tracker_url": "https://github.com/ajjackson/ascii-phonons/issues"
    }
