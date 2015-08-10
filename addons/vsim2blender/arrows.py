import bpy
from math import pi, atan, sin, cos, asin, acos, sqrt
import mathutils
import os
import time

def add_arrow(loc=[0,0,0], rot_euler=False, scale=1):
    print(os.path.dirname(__file__))
    #bpy.ops.wm.link(directory=os.path.dirname(__file__) + "/arrow_cylinder.blend/Object/", filename="Arrow")
    bpy.ops.wm.link_append(directory=os.path.dirname(__file__)+'/arrow_cylinder.blend/Object/', filepath="arrow_cylinder.blend",  filename="Arrow", link=True)
    arrow = bpy.data.objects['Arrow']
    arrow.location = loc
    if rot_euler:
        arrow.rotation_mode='XYZ'
        arrow.rotation_euler=rot_euler
    arrow.scale = [scale]*3 # Scale uniformly to reflect magnitude
    arrow.name = 'Arrow.{0}'.format(time.time()) # This is a hack to give arrows unique names. There should be a better solution.
        
def vector_to_euler(vector):
    """ Convert eigenvectors to Euler rotation vector for vertical arrow.

        Vector ratios can go infinite so need to check and apply lim(x->infty)[tanx] = pi/2

    """
    if len(vector) != 3:
        raise Exception("Need 3 coordinates")

    if type(vector[0]) == complex:
        a, b, c = (x.real for x in vector)
    else:
        a, b, c = (float(x) for x in vector)

    if a == 0.0:
        theta_z = pi/2.
    else:
        theta_z = atan(b/a)

    if b == 0.0:
        theta_y = 0
    elif b == 0.0 and c == 0.0:
        theta_y = 0 # Hopefully these conditions mean theta_y is arbitrary...
    elif c == 0.0:
        theta_y = pi/2.
    else:
        theta_y = atan(b/(c*sin(theta_z)))
    m = c / cos(theta_y)
    #print([0,theta_y, theta_z])
    return [0, theta_y, theta_z]

def vector_to_euler_v2(vector):
    """
    Find the euler rotation matrix to align (0,0,1) with a vector (a,b,c) in cartesian space

    This is probably not the most efficient way of doing this transformation, but it should be a fairly robust one. 

    """

    if len(vector) != 3:
        raise Exception("Need 3 coordinates")

    # Normalise vector to length 1
    vector = mathutils.Vector(vector)
    vector.normalize()
    a, b, c = vector

    # Rotate in x such that new height in z axis matches normalised vector
    theta_x = pi/2. - asin(c)

    # Calc length of new vector projected onto x-y plane
    p = sqrt(1. + c**2)

    # Calculate angle depending on quadrant of x-y plane
    if a >= 0 and b >= 0:
        theta_z = pi/2. - acos(a/p)
    elif a >=0 and b < 0:
        theta_z = pi - acos(-b/p)
    elif a < 0 and b < 0:
        theta_z = pi + acos(-b/p)
    elif a < 0 and b >= 0:
        theta_z = 2*pi - asin(-a/p)
    else:
        raise Warning('Are you sure these coordinates are real numbers?')
    return (theta_x, 0.0, theta_z)
