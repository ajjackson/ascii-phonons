import bpy
import math
from mathutils import Vector
from vsim2blender.arrows import vector_to_euler

def setup_camera(lattice_vectors, supercell, camera_rot=0,
                 field_of_view=0.5, scene=bpy.context.scene):
    """
    Set up a camera looking along the y axis

    :param lattice_vectors: Lattice vectors of unit cell
    :type lattice_vectors: 3-tuple of 3-Vectors
    :param supercell: Supercell dimensions
    :type supercell: 3-tuple of ints
    :param camera_rot: Rotation of camera about y axis (i.e. tilt) in degrees
    :type camera_rot: Float
    :param field_of_view: Camera field of view in radians
    :type field_of_view: float
    :param scene: Scene in which to insert camera object
    :type scene: bpy Scene
    """

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

def setup_camera_miller(lattice_vectors, supercell, camera_rot=0,
                        miller=(1,1,0), field_of_view=0.5,
                        scene=bpy.context.scene):
    """
    Set up a camera looking along the y axis

    :param lattice_vectors: Lattice vectors of unit cell
    :type lattice_vectors: 3-tuple of 3-Vectors
    :param supercell: Supercell dimensions
    :type supercell: 3-tuple of ints
    :param camera_rot: Rotation of camera about viewing axis
                       (i.e. tilt) in degrees
    :type camera_rot: Float
    :param miller: Miller indices of target view. Floating-point values may be
                   used for fine adjustments if desired.
    :type miller: 3-tuple
    :param field_of_view: Camera field of view in radians
    :type field_of_view: float
    :param scene: Scene in which to insert camera object
    :type scene: bpy Scene
    """

    a, b, c = [n * x for n, x in zip(supercell, lattice_vectors)]
    supercell_centre = 0.5 * sum([a,b,c], Vector((0.,0.,0.)))
    vertices = [x for x in [Vector((0,0,0)), a, a+b, b, c, c+a, c+a+b, c+b]]    

    # Use Miller index to create a vector to the camera
    # with arbitrary magnitude. Distances perpendicular to this vector
    # determine required camera distance
    
    camera_direction_vector = sum([i * x for i, x in zip(miller, lattice_vectors)],
                                  Vector((0,0,0)))

    vertices_from_center = [v - supercell_centre for v in vertices]

    camera_distance = max([dist_to_view_point(
        vertex, camera_direction_vector, field_of_view
        ) for vertex in vertices_from_center])

    # Re-scale position vector
    camera_direction_vector.length = camera_distance
    camera_position = supercell_centre + camera_direction_vector

    camera_rotation = (Vector((math.pi/2, 0, +math.pi/2)) + 
        Vector(vector_to_euler(camera_direction_vector)))

    bpy.ops.object.camera_add(location=camera_position,
                              rotation=camera_rotation)

    camera = bpy.context.object
    bpy.context.scene.camera = camera
    bpy.data.cameras[camera.name].angle = field_of_view

    # Not entirely sure why this works but it does
    bpy.data.cameras[camera.name].lens = 1.5 * camera_distance
    
def dist_to_view_point(point, camera_direction_vector, field_of_view):
    """
    Calculate the required camera distance along a vector to keep a
    point in view.

    :param point: Target vertex
    :type point: 3-Vector
    :param camera_direction_vector: Vector of arbitrary length pointing
                                    towards to camera
    :type camera_direction_vector: 3-Vector
    :param field_of_view: The camera field of view in radians
    :type field_of_view: Float
    
    """
    projection = point.project(camera_direction_vector)
    rejection = point - projection
    cone_width = rejection.length
    distance = cone_width / math.sin(field_of_view)
    return distance

