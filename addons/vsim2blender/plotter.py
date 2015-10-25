import bpy
import yaml
import os
import random
# import sys
from mathutils import Vector, Matrix
import math
import cmath
import itertools

# # Modify path to import stuff from other file

# sys.path.insert(0, os.path.abspath(script_directory)+'/..')
from vsim2blender.ascii_importer import import_vsim, cell_vsim_to_vectors
from vsim2blender.arrows import add_arrow, vector_to_euler
from vsim2blender.masses import mass_dict

script_directory = os.path.dirname(__file__)
defaults_table_file = script_directory + '/periodic_table.yaml'

def draw_bounding_box(cell, offset=(0,0,0)):
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

    Arguments:
        col: 3-tuple or list containing RGB color. If False, use a random colour.
        shadeless: Boolean; Enable set_shadeless parameter. Informally known as "lights out".
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

    Arguments:
        position: 3-tuple, list or vector containing atom coordinates. Units same as unit cell unless reduced=True
        lattice_vectors: 3-tuple or list containing Vectors specifying lattice bounding box/repeating unit
        cell_id: 3-tuple of integers, indexing position of cell in supercell. (0,0,0) is the
            origin cell. Negative values are ok.
        reduced: Boolean. If true, positions are taken to be in units of lattice vectors;
            if false, positions are taken to be Cartesian.
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
             yaml_file=False,periodic_table=False, name=False):
    """
    Add atom to scene

    Arguments:
        position: 3-tuple, list or vector containing atom coordinates. Units same as unit cell unless reduced=True
        lattice_vectors: 3-tuple or list containing Vectors specifying lattice bounding box/repeating unit
        symbol: chemical symbol. Used for colour and size lookup.
        cell_id: 3-tuple of integers, indexing position of cell in supercell. (0,0,0) is the
            origin cell. Negative values are ok.
        scale_factor: master scale factor for atomic spheres
        reduced: Boolean. If true, positions are taken to be in units of lattice vectors;
            if false, positions are taken to be Cartesian.
        yaml_file: If False, use colours and sizes from default periodic_table.yaml file.
            If a string is provided, this is taken to be a YAML file in same format, values clobber defaults.
        periodic_table: dict containing atomic radii and colours in format
            {'H':{'r': 0.31, 'col': [0.8, 0.8, 0.8]}, ...}. Takes
            priority over yaml_file and default table.
        name: Label for atom object
    """

    cartesian_position = absolute_position(position, lattice_vectors=lattice_vectors, cell_id=cell_id, reduced=reduced)

    # Get colour. Priority order is 1. periodic_table dict 2. yaml_file 3. defaults_table
    if yaml_file:
        yaml_file_data = yaml.load(open(yaml_file))
    else:
        yaml_file_data = False

    defaults_table = yaml.load(open(defaults_table_file))

    if periodic_table and symbol in periodic_table and 'col' in periodic_table[symbol]:
        col = periodic_table[symbol]['col']
    elif yaml_file_data and symbol in yaml_file_data and 'col' in yaml_file_data[symbol]:
        col = yaml_file_data[symbol]['col']
    else:
        if symbol in defaults_table and 'col' in defaults_table[symbol]:
            col = defaults_table[symbol]['col']
        else:
            col=False        

    # Get atomic radius. Priority order is 1. periodic_table dict 2. yaml_file 3. defaults_table
    if periodic_table and symbol in periodic_table and 'r' in periodic_table[symbol]:
        radius = periodic_table[symbol]['r']
    elif yaml_file_data and symbol in yaml_file_data and 'r' in yaml_file_data[symbol]:
        radius = yaml_file_data[symbol]['r']
    elif symbol in defaults_table and 'r' in defaults_table[symbol]:
        radius = defaults_table[symbol]['r']
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

def animate_atom_vibs(atom, qpt, displacement_vector, n_frames=30, magnitude=1., mass=1):
    """
    Apply vibrations as series of LOC keyframes

    Arguments:
        atom: bpy atom object
        qpt: wave vector of mode in CARTESIAN COORDINATES
        displacement_vector: complex vector describing relative displacement of atom
        n_frames: total number of animation frames. Animation will run from frame 0 to n_frames-1.
        magnitude: Scale factor for vibrations.
        mass: Relative atomic mass (inverse sqrt is used to scale vibration magnitude.)
    """

    r = atom.location
    for frame in range(n_frames):
        bpy.context.scene.frame_set(frame)
        exponent = cmath.exp( complex(0,1) * (r.dot(qpt) - 2 * math.pi*frame/n_frames))
        atom.location = r + mass**-.5 * magnitude * Vector([x.real for x in [x * exponent for x in displacement_vector]])
        atom.keyframe_insert(data_path="location",index=-1)

def vector_with_phase(atom, qpt, displacement_vector):
    """
    Calculate cartesian vector associated with atom vibrations

    Arguments:
        atom: bpy atom object
        qpt: wave vector of mode in CARTESIAN COORDINATES
        displacement_vector: complex vector describing relative displacement of atom
        n_frames: total number of animation frames. Animation will run from frame 0 to n_frames-1.
        magnitude: Scale factor for vibrations.
    """
    r = atom.location
    exponent = cmath.exp( complex(0,1) * (r.dot(qpt) - 0.25 * math.pi))
    arrow_end = r + Vector([x.real for x in [x * exponent for x in displacement_vector]])
    return arrow_end - r


def open_mode(ascii_file, mode_index, supercell=[2,2,2], animate=True, n_frames=30, vectors=False, bbox=True, bbox_offset=(0,0,0), scale_factor=1.0, vib_magnitude=1.0, arrow_magnitude=1.0):
    """
    Open v_sim ascii file in Blender

    Arguments:
        ascii_file: Path to file
        mode_index: integer id of mode; 0 corresponds to first mode in ascii file
        supercell: 3-tuple or list of integer supercell dimensions
        animate: Boolean: if True, add animation keyframes
        n_frames: Animation length in frames
        vectors: Boolean; if True, show arrows
        bbox: Boolean; if True, show bounding box
        bbox_loc: Vector or 3-tuple in lattice vector coordinates; position of bbox. Default (0,0,0) (Left front bottom)

    """

    vsim_cell, positions, symbols, vibs = import_vsim(ascii_file)
    lattice_vectors = cell_vsim_to_vectors(vsim_cell)

    masses = [mass_dict[symbol] for symbol in symbols]
        
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
            atom = add_atom(position,lattice_vectors,symbol,cell_id=cell_id, name = '{0}_{1}_{2}{3}{4}'.format(atom_index,symbol,*cell_id_tuple), scale_factor=scale_factor)
            displacement_vector = vibs[mode_index].vectors[atom_index]
            qpt = vibs[mode_index].qpt
            B = 2 * math.pi * Matrix(lattice_vectors).inverted().transposed()
            qpt_cartesian = Vector(qpt) * B
            
            if animate:
                animate_atom_vibs(atom, qpt_cartesian, displacement_vector,
                                  n_frames=n_frames, magnitude=vib_magnitude, mass=mass)
            if vectors:
                arrow_vector=vector_with_phase(atom, qpt_cartesian, displacement_vector)

                add_arrow(loc=absolute_position(position, lattice_vectors=lattice_vectors,
                                                cell_id=cell_id, mass=mass),
                          rot_euler=vector_to_euler(arrow_vector),
                          scale=arrow_vector.length*arrow_magnitude)
            
    # Position camera and colour world
    # Note that cameras as objects and cameras as 'cameras' have different attributes,
    # so need to look up camera in bpy.data.cameras to set field of view.

    field_of_view = 0.5 # Camera field of view in radians

    camera_x = (lattice_vectors[0][0]/2. + lattice_vectors[2][0]/2.) * supercell[0]
    camera_y = max(((abs(lattice_vectors[0][0]) + abs(lattice_vectors[2][0]) + 2) * supercell[0],
                    abs(lattice_vectors[2][2]) * supercell[2] + 2)) / (-2. * math.tan(field_of_view/2.))
    camera_z = lattice_vectors[2][2]/2. * supercell[2]
    camera_loc=( camera_x,
                 1.05 * camera_y,
                camera_z)
    bpy.ops.object.camera_add(location=camera_loc,rotation=(math.pi/2,0,0))
    camera = bpy.context.object
    bpy.context.scene.camera = camera
    bpy.data.cameras[camera.name].angle = field_of_view

    bpy.context.scene.world = bpy.data.worlds['World']
    bpy.data.worlds['World'].horizon_color = [0.5, 0.5, 0.5]

def setup_render(n_frames=30):
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.resolution_percentage = 50
    bpy.context.scene.render.use_edge_enhance = True
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = (n_frames-1)

def render(scene=False,output_file=False):
    """
    Render the scene

    Arguments:
        scene: Name of scene. If False, render active scene.
        output_file: Blender-formatted output path/filename. If False, do not render.
            This is a useful fall-through as calls to render() can be harmlessly included
            in boilerplate.

    """

    if (not output_file) or output_file=='False':
        pass

    else:
        if not scene:
            scene = bpy.context.scene.name

    # Set output path (No sanitising or absolutising at this stage)
    bpy.data.scenes[scene].render.filepath=output_file

    # Work out if animation or still is required

    animate = (bpy.data.scenes[scene].frame_start != bpy.data.scenes[scene].frame_end)

    # Render!
    bpy.ops.render.render(animation=animate, write_still=(not animate), scene=scene)
