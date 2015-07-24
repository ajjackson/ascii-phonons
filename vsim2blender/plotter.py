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


def main():
    
    ascii_file='gamma_vibs.ascii'

    vsim_cell, positions, symbols, vibs = import_vsim(ascii_file)
    cell = cell_vsim_to_vectors(vsim_cell)
    
    # Draw bounding box #
    draw_bounding_box(cell)

    # Switch to a new empty scene
    bpy.ops.scene.new(type='EMPTY')

