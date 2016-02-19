import bpy
import math
from mathutils import Vector

def setup_camera(lattice_vectors, supercell, camera_rot=0,
                        zoom=1., miller=(0,1,0), field_of_view=0.5,
                        scene=bpy.context.scene):
    """
    Set up a camera looking along the y axis

    :param lattice_vectors: Lattice vectors of unit cell
    :type lattice_vectors: 3-tuple of 3-Vectors
    :param supercell: Supercell dimensions
    :type supercell: 3-tuple of ints
    :param miller: Miller indices of target view. Floating-point values may be
                   used for fine adjustments if desired.
    :type miller: 3-tuple
    :param camera_rot: Camera tilt adjustment in degrees
    :type camera_rot: float
    :param zoom: Camera zoom adjustment
    :type zoom: float
    :param field_of_view: Camera field of view in radians
    :type field_of_view: float
    :param scene: Scene in which to insert camera object
    :type scene: bpy Scene
    """

    a, b, c = [n * x for n, x in zip(supercell, lattice_vectors)]
    supercell_centre = 0.5 * sum([a,b,c], Vector((0.,0.,0.)))
    vertices = [x for x in [Vector((0,0,0)), a, a+b, b, c, c+a, c+a+b, c+b]]    

    # Create an empty at the centre of the model for the camera to target
    bpy.ops.object.add(type='EMPTY', location=supercell_centre)
    empty_center = bpy.context.object

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

    bpy.ops.object.camera_add(location=camera_position)
    camera = bpy.context.object
    bpy.context.scene.camera = camera
    bpy.data.cameras[camera.name].angle = field_of_view
    bpy.data.cameras[camera.name].clip_end = 1e8
    
    
    # Use tracking to point camera at center of structure
    bpy.ops.object.constraint_add(type='TRACK_TO')
    camera.constraints['Track To'].target = empty_center
    camera.constraints['Track To'].track_axis = 'TRACK_NEGATIVE_Z'
    camera.constraints['Track To'].up_axis = 'UP_Y'

    # Rotate camera by mapping to empty and rotating empty
    camera.constraints['Track To'].use_target_z = True
    empty_center.select = True
    bpy.ops.transform.rotate(value=(camera_rot * 2 * math.pi/360),
                             axis = camera_direction_vector)

    # Tweak zoom level
    bpy.data.cameras[camera.name].lens = zoom * 75
    
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

