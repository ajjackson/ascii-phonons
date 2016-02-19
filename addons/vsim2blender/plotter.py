import bpy
import os
import random
# import sys
from mathutils import Vector, Matrix
import math
import cmath
import itertools
import vsim2blender
# # Modify path to import stuff from other file

# sys.path.insert(0, os.path.abspath(script_directory)+'/..')
from vsim2blender.ascii_importer import import_vsim, cell_vsim_to_vectors
from vsim2blender.arrows import add_arrow, vector_to_euler
import vsim2blender.camera as camera

script_directory = os.path.dirname(__file__)

def draw_bounding_box(cell, offset=(0,0,0)):
    """
    Draw unit cell bounding box

    :param cell: Lattice vectors
    :type cell: 3-tuple of 3-Vectors
    :param offset: Location offset from origin
    :type offset: 3-tuple in lattice coordinates
    """
    a, b, c = cell
    verts = [tuple(x) for x in [(0,0,0), a, a+b, b, c, c+a, c+a+b, c+b]]
    faces = [(0,1,2,3), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7), (4,5,6,7)]
    box_mesh = bpy.data.meshes.new("Bounding Box")
    box_object = bpy.data.objects.new("Bounding Box", box_mesh)

    offset=Vector(offset)
    cart_offset = offset * Matrix(cell)
    box_object.location = (cart_offset)
    bpy.context.scene.objects.link(box_object)
    box_mesh.from_pydata(verts,[],faces)
    box_mesh.update(calc_edges=True)

    box_material = bpy.data.materials.new("Bounding Box")
    box_object.data.materials.append(box_material)
    box_material.type = "WIRE"
    box_material.diffuse_color=(0,0,0)
    box_material.use_shadeless = True

def init_material(symbol, col=False, shadeless=True):
    """
    Create material if non-existent. Assign a random colour if none is specified.

    :param col: RGB color. If False, use a random colour.
    :type col: 3-tuple, list or Boolean False
    :param shadeless: Enable set_shadeless material parameter. Informally known as "lights out".
    :type shadeless: Boolean

    :returns: bpy material object
    """

    if symbol in bpy.data.materials.keys():
        return bpy.data.materials[symbol]
    elif not col:
        col = (random.random(), random.random(), random.random())

    material = bpy.data.materials.new(name=symbol)
    material.diffuse_color = col
    material.use_shadeless = shadeless
    return material

def absolute_position(position, lattice_vectors=[1.,1.,1.], cell_id=[0,0,0], reduced=False):
    """
    Calculate the absolute position of an atom in a supercell array

    :param position: atom coordinates. Units same as unit cell unless reduced=True
    :type position: 3-tuple, list or vector
    :param lattice_vectors: lattice bounding box/repeating unit
    :type lattice_vectors: 3-tuple or list containing 3-Vectors
    :param cell_id: position index of cell in supercell. (0,0,0) is the
            origin cell. Negative values are ok.
    :type cell_id: 3-tuple of integers
    :param reduced: If true, positions are taken to be in units of lattice vectors;
            if false, positions are taken to be Cartesian.
    :type reduced: Boolean

    :returns: cartesian_position
    :rtype: 3-Vector
    """
    
    if reduced:
        cartesian_position = Vector((0.,0.,0.))
        for i, (position_i, vector) in enumerate(zip(position, lattice_vectors)):
            cartesian_position += (position_i + cell_id[i]) * vector
    else:
        cartesian_position = Vector(position)
        for i, vector in enumerate(lattice_vectors):
            cartesian_position += (cell_id[i] * vector)

    return cartesian_position

def add_atom(position,lattice_vectors,symbol,cell_id=(0,0,0), scale_factor=1.0, reduced=False,
             name=False, config=False):
    """
    Add atom to scene

    :param position: Atom coordinates. Units same as unit cell unless reduced=True
    :type position: 3-tuple, list or Vector
    :param lattice_vectors: Vectors specifying lattice bounding box/repeating unit
    :type  lattice_vectors: 3-tuple or list
    :param symbol: Chemical symbol used for colour and size lookup.
    :type symbol: String
    :param cell_id: position index of cell in supercell. (0,0,0) is the
            origin cell. Negative values are ok.
    :type cell_id: 3-tuple of ints
    :param scale_factor: master scale factor for atomic spheres
    :type scale_factor: float
    :param reduced: If true, positions are taken to be in units of lattice vectors;
            if false, positions are taken to be Cartesian.
    :type reduced: Boolean
    :param name: Label for atom object
    :type name: String
    :param config: Settings from configuration files (incl. atom colours and radii)
    :type config: configparser.ConfigParser


    :returns: bpy object
    """

    if not config:
        config = vsim2blender.read_config()

    cartesian_position = absolute_position(position, lattice_vectors=lattice_vectors, cell_id=cell_id, reduced=reduced)

    # Get colour and atomic radius. Priority order is 1. User conf file 2. elements.conf
    if symbol in config['colours']:
        col=[float(x) for x in config['colours'][symbol].split()]
    else:
        col=False        
    if symbol in config['radii']:
        radius = float(config['radii'][symbol])
    else:
        radius = 1.0

    bpy.ops.mesh.primitive_uv_sphere_add(location=cartesian_position, size=radius * scale_factor)
    atom = bpy.context.object
    if name:
        atom.name = name

    material = init_material(symbol, col=col)
    atom.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    
    return atom

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
# The arrows for static images are defined as the vectors from the
# initial (average) positions to one quarter of the vibrational period (i.e. max displacement)

def animate_atom_vibs(atom, qpt, displacement_vector,
                      n_frames=30, start_frame=0, end_frame=None,
                      magnitude=1., mass=1):
    """
    Apply vibrations as series of LOC keyframes

    :param atom: Target atom
    :type atom: bpy Object
    :param qpt: wave vector of mode in *Cartesian coordinates*
    :type qpt: 3-Vector
    :param displacement_vector: complex vector describing relative displacement of atom
    :type displacement_vector: 3-tuple of Complex numbers
    :param n_frames: total number of animation frames. Animation will run from frame 0 to n_frames-1.
    :type n_frames: int
    :param magnitude: Scale factor for vibrations.
    :type magnitude: float
    :param mass: Relative atomic mass (inverse sqrt is used to scale vibration magnitude.)
    :type mass: float
    """

    r = atom.location

    if type(end_frame) != int:
        end_frame = start_frame + n_frames - 1
    for frame in range(start_frame, end_frame+1):
        bpy.context.scene.frame_set(frame)
        exponent = cmath.exp( complex(0,1) * (r.dot(qpt) - 2 * math.pi*frame/n_frames))
        atom.location = r + mass**-.5 * magnitude * Vector([x.real for x in [x * exponent for x in displacement_vector]])
        atom.keyframe_insert(data_path="location",index=-1)

def vector_with_phase(atom, qpt, displacement_vector):
    """
    Calculate Cartesian vector associated with atom vibrations

    :param atom: Target atom
    :type atom: bpy Object
    :param qpt: wave vector of mode in *Cartesian coordinates*
    :type qpt: 3-Vector
    :param displacement_vector: complex vector describing relative displacement of atom
    :type displacement_vector: 3-tuple of Complex numbers
    :param n_frames: total number of animation frames. Animation will run from frame 0 to n_frames-1.
    :type n_frames: positive int
    :param magnitude: Scale factor for vibrations.
    :type magnitude: float
    """
    r = atom.location
    exponent = cmath.exp( complex(0,1) * (r.dot(qpt) - 0.25 * math.pi))
    arrow_end = r + Vector([x.real for x in [x * exponent for x in displacement_vector]])
    return arrow_end - r


def open_mode(ascii_file, mode_index, supercell=[2,2,2], animate=True, camera_rot=0,
              n_frames=30, vectors=False, bbox=True, bbox_offset=(0,0,0),
              scale_factor=1.0, vib_magnitude=10.0, arrow_magnitude=1.0,
              miller=(0,1,0), zoom=1., config=False, start_frame=None, end_frame=None,
              preview=False, do_mass_weighting=False):
    """
    Open v_sim ascii file in Blender

    :param ascii_file: Path to file
    :type ascii_file: str
    :param mode_index: id of mode; 0 corresponds to first mode in ascii file
    :type mode_index: int
    :param supercell: supercell dimensions
    :type supercell: 3-tuple or 3-list of ints
    :param animate: if True, add animation keyframes
    :type animate: Boolean 
    :param n_frames: Animation length of a single oscillation cycle in frames
    :type n_frames: Positive int
    :param start_frame: The starting frame number of the rendered animation (default=0)
    :type start_frame: int or None
    :param end_frame: The ending frame number of the rendered animation (default=start_frame+n_frames-1)
    :type end_frame: int or None
    :param vectors: If True, show arrows
    :type vectors: Boolean
    :param bbox: If True, show bounding box
    :type bbox: Boolean
    :param bbox_loc: Position of bbox in lattice vector coordinates. Default (0,0,0) (Left front bottom)
    :type bbox_loc: Vector or 3-tuple
    :param miller: Miller indices of view
    :type miller: 3-tuple of floats
    :param camera_rot: Camera tilt adjustment in degrees
    :type camera_rot: float
    :param zoom: Camera zoom adjustment
    :type zoom: float    
    :param config: Settings from configuration files
    :type config: configparser.ConfigParser
    :param preview: Enable preview mode - single frame, smaller render
    :type preview: boolean
    :param do_mass_weighting: Weight eigenvectors by mass. This is not usually required.
    :type do_mass_weighting: boolean
    """

    if not config:
        config = vsim2blender.read_config()

    if type(start_frame) != int:
        start_frame = 0
    if preview:
        end_frame = start_frame        
    elif type(end_frame) != int:
        end_frame = start_frame + n_frames - 1

    vsim_cell, positions, symbols, vibs = import_vsim(ascii_file)
    lattice_vectors = cell_vsim_to_vectors(vsim_cell)

    if do_mass_weighting:
        masses = [float(config['masses'][symbol]) for symbol in symbols]
    else:
        masses = [1 for symbol in symbols]
        
    # Switch to a new empty scene
    bpy.ops.scene.new(type='EMPTY')
    
    # Draw bounding box #
    if bbox:
        bbox_offset = Vector(bbox_offset)
        draw_bounding_box(lattice_vectors, offset=bbox_offset)

    # Draw atoms
    for cell_id_tuple in itertools.product(range(supercell[0]),range(supercell[1]),range(supercell[2])):
        cell_id = Vector(cell_id_tuple)
        for atom_index, (position, symbol, mass) in enumerate(zip(positions, symbols, masses)):
            atom = add_atom(position,lattice_vectors,symbol,cell_id=cell_id, name = '{0}_{1}_{2}{3}{4}'.format(atom_index,symbol,*cell_id_tuple), scale_factor=scale_factor, config=config)
            if animate or vectors:
                displacement_vector = vibs[mode_index].vectors[atom_index]
                qpt = vibs[mode_index].qpt
                B = 2 * math.pi * Matrix(lattice_vectors).inverted().transposed()
                qpt_cartesian = Vector(qpt) * B
            
            if animate:
                animate_atom_vibs(atom, qpt_cartesian, displacement_vector,
                                  start_frame=start_frame, end_frame=end_frame, n_frames=n_frames,
                                  magnitude=vib_magnitude, mass=mass)
            if vectors:
                arrow_vector=vector_with_phase(atom, qpt_cartesian, displacement_vector)
                add_arrow(loc=absolute_position(position, lattice_vectors=lattice_vectors,
                                                cell_id=cell_id),
                          mass=mass,
                          rot_euler=vector_to_euler(arrow_vector),
                          scale=arrow_vector.length*arrow_magnitude)
            
    # Position camera and colour world
    # Note that cameras as objects and cameras as 'cameras' have different attributes,
    # so need to look up camera in bpy.data.cameras to set field of view.

    camera.setup_camera(lattice_vectors, supercell, camera_rot=camera_rot, zoom=zoom,
                        field_of_view=0.2, miller=miller,  scene=bpy.context.scene)

    bpy.context.scene.world = bpy.data.worlds['World']
    bpy.data.worlds['World'].horizon_color = [float(x) for x in 
                                              config['general']['background'].split()]

def setup_render(start_frame=0, end_frame=None, n_frames=30, preview=False):
    """
    Setup the render setting
    
    :param n_frames: Animation length of a single oscillation cycle in frames
    :type n_frames: Positive int
    :param start_frame: The starting frame number of the rendered animation (default=0)
    :type start_frame: int or None
    :param end_frame: The ending frame number of the rendered animation (default=start_frame+n_frames-1)
    :type end_frame: int or None
    :param preview: Write to a temporary preview file at low resolution instead of the output. Use first frame only.
    :type preview: str or Boolean False    

    """
    if type(start_frame) != int:
        start_frame = 0
    if preview:
        end_frame = start_frame
    elif type(end_frame) != int:
        end_frame = start_frame + n_frames - 1
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1080
    if preview:
        bpy.context.scene.render.resolution_percentage = 20
    else:
        bpy.context.scene.render.resolution_percentage = 50        
    bpy.context.scene.render.use_edge_enhance = True
    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame

def render(scene=False, output_file=False, preview=False):
    """
    Render the scene

    :param scene: Name of scene. If False, render active scene.
    :type scene: String or Boolean False
    :param output_file: Blender-formatted output path/filename. If False, do not render.
            This is a useful fall-through as calls to render() can be harmlessly included
            in boilerplate.
    :type output_file: String or Boolean False
    :param preview: Write to a temporary preview file at low resolution instead of the output
    :type preview: str or Boolean False    

    """

    if (not output_file) or output_file=='False':
        pass

    else:
        if not scene:
            scene = bpy.context.scene.name

        # Set output path (No sanitising or absolutising at this stage)
        if preview:
            output_file = preview        
        bpy.data.scenes[scene].render.filepath=output_file

        # Work out if animation or still is required

        animate = (bpy.data.scenes[scene].frame_start != bpy.data.scenes[scene].frame_end)

        # Render!
        bpy.ops.render.render(animation=animate, write_still=(not animate), scene=scene)
