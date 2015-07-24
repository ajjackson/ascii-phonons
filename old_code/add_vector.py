import bpy
from math import pi, atan, sin, cos, asin, acos, sqrt
import mathutils

def add_arrow(loc=[0,0,0], rot_euler=False, scale=1):
    bpy.ops.wm.append(filepath="//arrow_cylinder.blend/Object/", directory="/Users/adamjackson/Documents/Blender/vectors/arrow_cylinder.blend/Object/", filename="Arrow")
    arrow = bpy.context.selected_objects[0]
    arrow.location = loc
    if rot_euler:
        arrow.rotation_mode='XYZ'
        arrow.rotation_euler=rot_euler
    arrow.scale = [scale]*3 # Scale uniformly to reflect magnitude
        
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
    A simpler, more intuitive method for finding the euler rotation matrix to align (0,0,1) with a vector (a,b,c) in cartesian space

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
    
def vector_to_string(vector):
    string_list = [ '{0:6.3f}'.format(x) for x in vector]
    string = ' '.join(string_list)
    return string

if __name__ == '__main__':
    print("Comparing methods")
    print('|'+' '*8+'Vector'+' '*8+'|'+' '*10+'v1'+' '*10+'|'+' '*10+'v2'+' '*10+'|')
    print('|'+('-'*22+'|')*3)
    for vector in ([0,0,1], [1,0,0], [2,2,2], [1,2,3],[1,-1,-1],[-2,1,-1]):
        print('| {0} | {1} | {2} |'.format(vector_to_string(vector), vector_to_string(vector_to_euler(vector)), vector_to_string(vector_to_euler_v2(vector))))
