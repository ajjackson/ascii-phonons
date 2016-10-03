.. _cli:

Command-line interface
======================

A command-line utility, **ascii-phonons** is provided in the
*scripts* folder.  This program generates a temporary Python 3 script,
making use of the :mod:`vsim2blender` module, and calls Blender.  The
only mandatory argument is a ``.ascii`` file containing the crystal
structure and phonon mode data.

::

  ./scripts/ascii-phonons [OPTARGS] my_crystal.ascii [OPTARGS]

The detailed output is controlled with optional arguments, as outlined below.
The list of accepted arguments may also be viewed by calling with the "help" argument ``-h``

::

  ./scripts/ascii-phonons -h

+-----------------------------------+------------------------------------------+
| Syntax                            | Description                              |
+-----------------------------------+------------------------------------------+
|``-B PATH``, ``--blender_bin PATH``|The script will make an educated guess if |
|                                   |this is not provided.                     |
|                                   |                                          |
+-----------------------------------+------------------------------------------+
| ``-m I``, ``--mode_index``        | The index of the phonon mode to use      |
|                                   | (counting from 0).                       |
+-----------------------------------+------------------------------------------+
| ``-d X Y Z``,                     | Make a supercell; three integers X Y Z   |
| ``--supercell_dimensions X Y Z``  | specify multiples of lattice vectors     |
|                                   |                                          |
+-----------------------------------+------------------------------------------+
| ``-s``, ``--static``              |Output a single static image              |
+-----------------------------------+------------------------------------------+
| ``-f``, ``--n_frames``            | Number of frames in animation (default   |
|                                   | 30)                                      |
+-----------------------------------+------------------------------------------+
| ``-o PATH/NAME``, ``--output_file |Filename for output. Format specifier     |
| PATH/NAME``                       |(.png, .gif) is appended automatically. If|
|                                   |-o is specified, the Blender GUI is not   |
|                                   |launched unless -g is also specified.     |
|                                   |                                          |
|                                   |                                          |
+-----------------------------------+------------------------------------------+
| ``-g``, ``--gui``                 |Open full Blender GUI session, even if    |
|                                   |rendering output.                         |
+-----------------------------------+------------------------------------------+
| ``--gif``                         |Create a .gif file using Imagemagick      |
|                                   |convert. This flag is ignored if no output|
|                                   |file is specified.                        |
|                                   |                                          |
+-----------------------------------+------------------------------------------+
| ``-v``, ``--vectors``             | Show eigenvectors with                   |
|                                   | static arrows.                           |
+-----------------------------------+------------------------------------------+
| ``--scale_factor X.Y``            |Floating-point scale factor for atom      |
|                                   |size. 1.0 = covalent radius.  It is       |
|                                   |recommended to reduce this value when     |
|                                   |visualising with arrows, in order to      |
|                                   |prevent arrows from being hidden inside   |
|                                   |atoms.                                    |
+-----------------------------------+------------------------------------------+
| ``--vib_magnitude X.Y``           |Floating-point scale factor applied to    |
|                                   |displacements. The default value of 3 was |
|                                   |selected for Cu2ZnSnS4; this may need to  |
|                                   |be adjusted for different systems.        |
+-----------------------------------+------------------------------------------+
| ``--arrow_magnitude X.Y``         | Floating-point scale factor applied to   |
|                                   | arrows created with the -v flag.         |
+-----------------------------------+------------------------------------------+
| ``--normalise_vectors``           | Rescale arrows such that the maximum for |
|                                   | each mode is a fixed length.             |
+-----------------------------------+------------------------------------------+
| ``--no_box``                      | Hide the unit cell bounding box.         |
|                                   |                                          |
|                                   |                                          |
|                                   |                                          |
+-----------------------------------+------------------------------------------+
| ``--box_position X Y Z``          |Adjust the bounding pox position in the   |
|                                   |supercell with floating-point multiples X |
|                                   |Y Z of the lattice vectors.               |
|                                   |                                          |
+-----------------------------------+------------------------------------------+
| ``--miller X Y Z``                | Miller indices determining camera        |
|                                   | direction. Negative and fractional values|
|                                   | are permitted.                           |
|                                   |                                          |
+-----------------------------------+------------------------------------------+
| ``--montage``                     |Use Imagemagick to create a tiled array   |
|                                   |output of all modes. The `-m` flag is     |
|                                   |ignored. An animated .gif will be output  |
|                                   |unless ``--static`` is specified.         |
+-----------------------------------+------------------------------------------|
| ``--montage_args``                | Additional args for montage command e.g. |
|                                   | ``--montage_args='-tile {cols}x{rows}'`` |
|                                   | (Note the use of = and single quotes)    |
+-----------------------------------+------------------------------------------+
| ``--ncol``                        | Columns in tiled display (default = 6).  |
|                                   | (Not yet implemented for animation.)     |
+-----------------------------------+------------------------------------------|
| ``--nrow``                        | Rows per page in tiled display           |
|                                   | (default = 6).                           |
|                                   | (Not yet implemented for animation.)     |
+-----------------------------------+------------------------------------------+
| ``--camera_rot ROT``              | Rotated camera position in degrees.      |
|                                   |                                          |
|                                   |                                          |
|                                   |                                          |
+-----------------------------------+------------------------------------------+
| ``--zoom X.Y``                    | Floating-point zoom adjustment. A        |
|                                   | sensible starting point is calculated    |
|                                   | automatically and corresponds to the     |
|                                   | value 1.0, but this factor can be        |
|                                   | used for further adjustment.             |
+-----------------------------------+------------------------------------------+
| ``--config PATH/FILE.conf``       | Path to user configuration file.         |
|                                   |                                          |
|                                   |                                          |
|                                   |                                          |
+-----------------------------------+------------------------------------------+
| ``--do_mass_weighting``           | Apply mass weighting to atom movements.  |
|                                   | This has usually already been done in the|
|                                   | construction of the .ascii file, and     |
|                                   | should not be repeated.                  |
+-----------------------------------+------------------------------------------+
| ``--orthographic``                | Use orthographic projection              |
|                                   | (i.e. no perspective effect)             |
+-----------------------------------+------------------------------------------+
