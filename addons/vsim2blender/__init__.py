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
    "version": (0,4,1),
    "blender": (2, 65, 0),
    "location": "",
    "category": "Import-Export",
    "tracker_url": "https://github.com/ajjackson/ascii-phonons/issues"
    }

def read_config(user_config=''):
    """
    Read configuration files elements.conf, settings.conf and optional user conf

    :param user_config: Path to a user-specified configuration file
    :type user_config: str

    :returns: config
    :rtype: configparser.ConfigParser
    """
    import os
    import configparser
    config = configparser.ConfigParser()

    # Suppress default conversion to lower case as it makes periodic
    # table hard to read
    config.optionxform = lambda option: option

    config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'elements.conf'))
    config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'settings.conf'))
    if user_config == '':
        pass
    else:
        config.read(user_config)

    return config
