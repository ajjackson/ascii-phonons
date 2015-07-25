import bpy
import os
import sys
from mathutils import Vector

# Modify path to import stuff from other file
script_directory = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(script_directory)+'/..')
from vsim2blender.ascii_importer import import_vsim cell_vsim_to_vectors

def draw_bounding_box(cell):
    a, b, c = Vector(cell[0]), Vector(cell[1]), Vector(cell[2])
    verts = [tuple(x) for x in [(0,0,0), a, a+b, b, c, c+a, c+a+b, c+b]]
    faces = [(0,1,2,3), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7), (4,5,6,7)]
    box_mesh = bpy.data.meshes.new("Bounding Box")
    box_object = bpy.data.objects.new("Bounding Box", box_mesh)
    box_object.location = (0,0,0)
    bpy.context.scene.objects.link(box_object)
    box_mesh.from_pydata(verts,[],faces)
    box_mesh.update(calc_edges=True)

    box_material = bpy.data.materials.new("Bounding Box")
    box_object.data.materials.append(box_material)
    box_material.type = "WIRE"
    box_material.diffuse_color=(0,0,0)
    box_material.use_shadeless = True


# Computing the positions
#
# Key equation is:
# _u_(jl,t) = Sum over _k_, nu: _U_(j,_k_,nu) exp(i[_k_ _r_(jl) - w(_k_,nu)t])
# [M. T. Dove, Introduction to Lattice Dynamics (1993) Eqn 6.18]
#
# Where nu is the mode identity, w is frequency, _U_ is the
# displacement vector, and _u_ is the displacement of atom j in unit
# cell l. We can break this down to a per-mode displacement and so the
# up-to-date position of atom j in cell l in a given mode visualisation
#
# _r'_(jl,t,nu) = _r_(jl) +  _U_(j,_k_,nu) exp(i[_k_ _r_(jl) - w(_k_,nu) t])
#
# Our unit of time should be such that a full cycle elapses over the
# desired number of frames. 
#
# A full cycle usually lasts 2*pi/w, so let t = frame*2*pi/wN;
# -w t becomes -w 2 pi frame/wN = 2 pi frame / N
#
# _r'_(jl,t,nu) = _r_(jl) + _U_(j,_k_,nu) exp(i[_k_ _r_(jl) - 2 pi (frame#)/N])
#
#

def main():
    
    ascii_file='gamma_vibs.ascii'

    vsim_cell, positions, symbols, vibs = import_vsim(ascii_file)
    cell = cell_vsim_to_vectors(vsim_cell)
    
    # Draw bounding box #
    draw_bounding_box(cell)

    # Switch to a new empty scene
    bpy.ops.scene.new(type='EMPTY')

