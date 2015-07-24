import bpy
import math
from mathutils import Vector

mode=MODENUM - 1

for item in ['Cube', 'Lamp','Camera']:
    try:
        bpy.data.objects[item].select = True
        bpy.ops.object.delete()
    except:
        pass

lattice_vectors =      [[5.38316679,  -0.00125204, -0.00253438],
                       [0.00198560,    5.38337088,  -0.00176447],
                       [-2.68928790,  -2.68789816,  5.36568880]]
lattice_vector_names = ['a_vector','b_vector','c_vector']
lattice_images = [1,1,2]

# bpy.ops.wm.addon_enable(module="io_mesh_xyz")
# If there is trouble, the .zip file can be installed with
# bpy.ops.wm.addon_install(filepath="/home/adam/Documents/kesterite_batch/io_mesh_xyz.zip")    
bpy.ops.import_mesh.xyz(filepath=("//gamma_mode_11.xyz"), use_frames=False,
use_center=False, use_center_all=False, scale_distances=1, scale_ballradius=0.4)

for element in ['Copper','Sulfur','Zinc','Tin']:
    ob = bpy.data.objects[element]
    for lattice_vector, vector_name, repeats in zip(lattice_vectors, lattice_vector_names, lattice_images):
        ob.modifiers.new(vector_name,"ARRAY")
        array = ob.modifiers[vector_name]
        array.count=repeats
        array.use_relative_offset=False
        array.use_constant_offset=True
        array.constant_offset_displace = lattice_vector

for material in bpy.data.materials:
    material.use_shadeless = True

bpy.data.materials['Tin'].diffuse_color=(0.04,0.5,0.15)
bpy.data.materials['Zinc'].diffuse_color=(0.3,0.2,0.7)
bpy.data.materials['Copper'].diffuse_color=(0.8,0.3,0.1)

##### Create bounding box for unit cell #####

a, b, c = Vector(lattice_vectors[0]), Vector(lattice_vectors[1]), Vector(lattice_vectors[2])
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

#### Add vectors ####
from add_vector import add_arrow, vector_to_euler_v2
from ascii_importer import import_vsim
cell_vsim, positions, symbols, vibs = import_vsim('gamma_vibs.ascii')
magnitudes = [
    (v[0]**2. + v[1]**2. + v[2]**2.)**0.5 for v in vibs[mode].vectors
    ]
scale_factor = 1. / max(magnitudes)
for i in range (len(positions)):
    add_arrow(loc=positions[i],rot_euler=vector_to_euler_v2(vibs[mode].vectors[i]), scale=magnitudes[i]*scale_factor)

##### Position camera and render #####

camera_loc=(( max(lattice_vectors[:][0])/2.) -3, -20, ( max(lattice_vectors[:][2])/2.)+3.5)
bpy.ops.object.camera_add(location=camera_loc,rotation=(math.pi/2,0,0))
bpy.context.scene.camera = bpy.data.objects['Camera']

bpy.data.worlds['World'].horizon_color = [0.5, 0.5, 0.5]

bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 50
bpy.context.scene.render.use_edge_enhance = True
