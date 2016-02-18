import bpy
import math

def setup_camera(lattice_vectors, supercell, camera_rot=0,
                 field_of_view=0.5, scene=bpy.context.scene):
    field_of_view = 0.5 # Camera field of view in radians

    camera_x = (lattice_vectors[0][0]/2. + lattice_vectors[2][0]/2.) * supercell[0]
    camera_y = max(((abs(lattice_vectors[0][0]) + abs(lattice_vectors[2][0]) + 2) * supercell[0],
                    abs(lattice_vectors[2][2]) * supercell[2] + 2)) / (-2. * math.tan(field_of_view/2.))
    camera_z = lattice_vectors[2][2]/2. * supercell[2]
    camera_loc=( camera_x,
                 1.05 * camera_y,
                camera_z)
    bpy.ops.object.camera_add(location=camera_loc,
                              rotation=(math.pi/2,(2*math.pi/360.)*camera_rot,0))
    camera = bpy.context.object
    bpy.context.scene.camera = camera
    bpy.data.cameras[camera.name].angle = field_of_view
