Camera
======

Camera placement is an interesting problem.  The current method
:func:`vsim2blender.camera.setup_camera` looks along the y axis
and estimates a sensible distance based on the lattice parameters, but
is occasionally thrown off.

The successor in development allows the camera position to be
specified by giving the Miller indices of a plane to view.

.. automodule:: vsim2blender.camera
   :members:                
