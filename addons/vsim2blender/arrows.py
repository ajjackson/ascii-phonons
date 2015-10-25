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

def vector_to_euler(vector):
    """ Workings are in my ipython notebooks!

        Vector ratios can go infinite so need to check and apply lim(x->infty)[tanx] = pi/2

    """
    if len(vector) != 3:
        raise Exception("Need 3 coordinates")
    a, b, c = (float(x) for x in vector)

    if a == 0.0:
        theta_z = pi/2.
    else:
        theta_z = atan2(b,a)

    if b == 0.0:
        theta_y = 0
    elif b == 0.0 and c == 0.0:
        theta_y = 0 # Hopefully these conditions mean theta_y is arbitrary...
    elif c == 0.0:
        theta_y = pi/2.
    else:
        theta_y = atan2(b,(c*sin(theta_z)))
    m = c / cos(theta_y)
    #print([0,theta_y, theta_z])
    return [0, theta_y, theta_z]
