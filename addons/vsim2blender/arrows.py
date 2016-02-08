import bpy
from math import pi, sin, cos, asin, acos, sqrt, atan2
import mathutils
import os
import time

def add_arrow(loc=[0,0,0], rot_euler=False, scale=1, mass=1):
    # Check Blender version to account for API change
    if bpy.app.version[0] == 2 and bpy.app.version[1] < 70:
        bpy.ops.wm.link_append(directory=os.path.dirname(__file__)+'/arrow_cylinder.blend/Object/', filepath="arrow_cylinder.blend",  filename="Arrow", link=True)
    else:
        bpy.ops.wm.link(directory=os.path.dirname(__file__)+'/arrow_cylinder.blend/Object/', filepath="arrow_cylinder.blend",  filename="Arrow")
    arrow = bpy.data.objects['Arrow']
    arrow.location = loc
    if rot_euler:
        arrow.rotation_mode='XYZ'
        arrow.rotation_euler=rot_euler
    scale = scale * mass**-.5  # Inverse square root of mass gives a physical relative size of motions
    arrow.scale = [scale]*3 # Scale uniformly to reflect magnitude
    arrow.name = 'Arrow.{0}'.format(time.time()) # This is a hack to give arrows unique names. There should be a better solution.

def norm(*args):
    assert len(args) > 0
    sqargs = [x**2 for x in args]
    return sqrt(sum(sqargs))

def vector_to_euler(vector):
    """ Euler rotations to bring arrow along (1,0,0) to line up with vector

    """
    if len(vector) != 3:
        raise Exception("Need 3 coordinates")
    a, b, c = (float(x) for x in vector)

    theta_y = atan2(-c, norm(a,b))
    theta_z = atan2(b,a)

    return [0, theta_y, theta_z]
