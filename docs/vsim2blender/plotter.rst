Plotter
=======

Commands for adding atoms to the scene and animating them.

Animation
---------

The key equation is: [1]_

.. math::

   \mathbf{u}(jl,t) = \sum_{\mathbf{q},\nu} \mathbf{U}(j,\mathbf{q},\nu) \exp(i[\mathbf{q} \mathbf{r}(jl) - \omega(\mathbf{q},\nu)t])

Where :math:`\nu` is the mode identity, :math:`\omega` is frequency, :math:`\mathbf{U}` is the
displacement vector, and :math:`\mathbf{u}` is the displacement of atom :math:`j` in unit
cell :math:`l`. We can break this down to a per-mode displacement and so the
up-to-date position of atom :math:`j` in cell :math:`l` in a given mode visualisation

.. math::

   \mathbf{r^\prime}(jl,t,\nu) = \mathbf{r}r(jl) + \mathbf{U}(j,\mathbf{q},\nu) \exp(i[\mathbf{q r}(jl) - \omega (\mathbf{k},\nu) t])

Our unit of time should be such that a full cycle elapses over the
desired number of frames. 

A full cycle usually lasts :math:`2\pi/\omega`, so let :math:`t = f*2*\pi/\omega N`;
:math:`-\omega t` becomes :math:`-\omega 2 \pi f/\omega N = 2 pi f / N` where :math:`f` is the frame number.

.. math::

   \mathbf{r^\prime}(jl,t,\nu) = \mathbf{r}(jl) + \mathbf{U}(j,\mathbf{q},\nu) \exp(i[\mathbf{q r}(jl) - 2 \pi f/N])

The arrows for static images are defined as the vectors from the
initial (average) positions to one quarter of the vibrational period (i.e. max displacement)

.. [1] M. T. Dove, Introduction to Lattice Dynamics (1993) Eqn 6.18

Module contents
---------------

.. automodule:: vsim2blender.plotter
   :members:                


