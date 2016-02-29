
Installation
============

Will be outlined in more detail.
For now, see the `README file <https://github.com/ajjackson/ascii-phonons/blob/master/README.md>`_.

Paths
-----

Ascii-phonons relies on the script files **scripts/ascii-phonons** and **scripts/ascii-phonons-gui** finding core functionality in the module init file **ascii_phonons/__init__.py**.
In previous versions of ascii-phonons, this required the top-level folder (i.e. the folder produced by `git clone` or by unzipping a downloaded file) to be included in the user's PYTHONPATH.
In the most recent versions, this is not necessary; as long as the folder structure is left intact, the scripts should be able to find what they need.

Blender
-------

A recent version of `Blender <https://www.blender.org/download>`_ is required; 
development is currently based on Blender 2.76 and later. 
At least version 2.70 is needed, which provides the wireframe modifier used to draw the bounding box. 

Linux
~~~~~

Note that the versions of Blender available in package managers such as apt-get are often quite dated.
Installing the latest version for Linux is easy, however; just download the .tar.gz file, untar it and add the directory to your PATH.::

    mv /some/blender/download.tar.bz2 /some/directory && cd /some/directory
    tar -xf /my-blender-download.tar.bz2
    echo "export PATH="${PWD}/my-blender-folder:${PATH}" >> ${HOME}/.bashrc
    source ${HOME}/.bashrc


Documentation dependencies
--------------------------

* Sphinx
* Mock
