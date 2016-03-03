import os
from subprocess import call
import tempfile
import re
import itertools

ascii_phonons_path = os.path.abspath(os.path.join(
     os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
addons_path = os.path.join(ascii_phonons_path, 'addons')

def call_blender(input_file, **options):
    """Generate a temporary script file and call Blender

    Typically Blender is called in batch mode to render one or a series
    of .png image files.

    :param input_file: Path to .ascii file specifying crystal structure and vibrational modes
    :type input_file: str
    """
    input_file = os.path.abspath(input_file)
    if options['output_file']:
        output_file = os.path.abspath(output_file)
    handle, python_tmp_file = tempfile.mkstemp(suffix='.py', dir='.')

    if 'blender_bin' in options:
        call_args = [options['blender_bin']]
    else:
        import platform
        if platform.mac_ver()[0] != '':
            #call_args = ['open','-a','blender','--args']
            call_args=['/Applications/Blender/blender.app/Contents/MacOS/blender']
        else:
            call_args = ['blender']

    if static:
        n_frames=1

    if gif and output_file:
        gif_name = output_file + '.gif'
        handle, image_tmp_filename = tempfile.mkstemp(dir='.')
        output_file = image_tmp_filename
        os.remove(image_tmp_filename) # We only needed the name

    for frame in start_frame, end_frame:
        if frame == None:
            frame = 'None'

    if preview and type(preview) == str:
        preview = '\'' + preview + '\''
    else:
        preview = 'False'
            
    python_txt = """
import sys
from os.path import pathsep

sys.path = ['{add_path}'] + sys.path

import bpy
import vsim2blender
import vsim2blender.plotter

config = vsim2blender.read_config(user_config='{config}')

vsim2blender.plotter.open_mode('{0}', {1}, static={2}, n_frames={3},
                                vectors={4}, scale_factor={5}, vib_magnitude={6},
                                arrow_magnitude={7}, supercell=({8},{9},{10}),
                                bbox={11}, bbox_offset={12}, config=config,
                                start_frame={start_frame}, end_frame={end_frame},
                                preview={preview}, do_mass_weighting={do_mass_weighting},
                                camera_rot={camera_rot}, miller={miller}, zoom={zoom})
vsim2blender.plotter.setup_render_freestyle(n_frames={3}, start_frame={start_frame}, end_frame={end_frame}, preview={preview}, config=config)
vsim2blender.plotter.render(output_file='{out_file}', preview={preview})
""".format(input_file, mode_index, static, n_frames, vectors,
           scale_factor, vib_magnitude, arrow_magnitude,
           supercell[0], supercell[1], supercell[2], bbox, bbox_offset,
           out_file=output_file, add_path=addons_path, miller=miller, camera_rot=camera_rot, zoom=zoom,
           config=user_config, start_frame=start_frame, end_frame=end_frame,
           preview=preview, do_mass_weighting=do_mass_weighting)

    with open(python_tmp_file, 'w') as f:
        f.write(python_txt)

    if output_file and not gui:
        call_args.append("--background")

    call_args = call_args + ["-P", python_tmp_file]

    call(call_args)

    os.remove(python_tmp_file)

    if gif and output_file:
        tmp_files = [image_tmp_filename + '{0:04.0f}'.format(i) + '.png' for i in range(n_frames)]
        convert_call_args = ['convert', '-delay', '10'] + tmp_files + ['-loop', '0', gif_name]
        try:
            call(convert_call_args)
        except OSError as err:
            raise Exception("\n\nCould not run Imagemagick convert to create .gif.\n" +
                            "Error message: {0}\n".format(err) +
                            "Are you sure you have Imagemagick installed?\n")

        for f in tmp_files:
            os.remove(f)
        
def montage_static(input_file, **options):
    mode_data = list(_qpt_freq_iter(input_file))

    for param, default in (('output_file', 'phonon'),):
        if not options[param]:
            options[param] = default

    call_args = ['montage', '-font', 'Helvetica', '-pointsize', '18']

    # Render smaller image
    options.update({'preview': True})

    output_basename = options['output_file']
    for index, (qpt, freq) in enumerate(mode_data):
        options.update({'output_file': '.'.join((output_basename, str(index)))})
        options.update({'mode_index':index})
        call_blender(input_file, **options)
        call_args.extend(['-label', _flabelformat(freq),
                         options['output_file'] + '.png'])
    call_args.append(output_basename + '_montage.png')

    call(call_args)

    for index, (qpt, freq) in enumerate(mode_data):
        os.remove('.'.join((output_basename, str(index), 'png')))

def montage_anim(input_file, **options):
    mode_data = list(_qpt_freq_iter(input_file))

    for param, default in (('output_file', 'phonon'),
                               ('start_frame', 0),
                               ('n_frames', 30)):
        if not param in options or not options[param]:
            options[param] = default

    if not 'end_frame' in options or not options['end_frame']:
        options['end_frame'] = options['start_frame'] + options['n_frames'] - 1

    # Render smaller image, take over gif generation
    options.update({'preview': True, 'gif': False})
    output_basename = options['output_file']
    labels = []
    for index, (qpt, freq) in enumerate(mode_data):
        options.update({'output_file': '.'.join((output_basename, str(index), ''))})
        options.update({'mode_index':index})
        call_blender(input_file, **options)
        labels.append(_flabelformat(freq))

    print("Compiling tiled images...")

    frames = range(options['start_frame'], options['end_frame'] + 1)
    for frame in frames:
        montage_call_args = ['montage', '-font', 'Helvetica', '-pointsize', '18']
        for index, label in enumerate(labels):
            montage_call_args.extend(['-label', label, 
                                      '.'.join((output_basename,
                                                '{0}'.format(index),
                                                '{0:04d}'.format(frame),
                                                'png'))])

        montage_call_args.append('.'.join((output_basename, '{0}'.format(frame),
                                          'montage.png')))
        try:
            call(montage_call_args)
        except OSError as err:
            raise Exception("\n\nCould not run Imagemagick convert to create .gif.\n" +
                            "Error message: {0}\n".format(err) +
                            "Are you sure you have Imagemagick installed?\n")

    print("Joining images into .gif file")

    convert_call_args = (['convert', '-delay', '10'] +
                             ['.'.join((output_basename, '{0}'.format(frame), 'montage.png')) 
                                  for frame in frames]
                             + ['-loop', '0', output_basename + '.gif'])
    call(convert_call_args)
    print("Cleaning up...")
    for frame in frames:
        for index in range(len(labels)):
            os.remove('.'.join((output_basename, '{0}'.format(index),
                                    '{0:04d}'.format(frame), 'png')))
        os.remove('.'.join((output_basename, '{0}'.format(frame), 
                                'montage', 'png')))

    print("Done!")

    # if gif and output_file:
    #     tmp_files = [image_tmp_filename + '{0:04.0f}'.format(i) + '.png' for i in range(n_frames)]
    #     convert_call_args = ['convert', '-delay', '10'] + tmp_files + ['-loop', '0', gif_name]
    

    # for index, (qpt, freq) in enumerate(mode_data):
    #     for frame in range(options['start_frame'], options['end_frame'] + 1):
    #         os.remove(output_basename + str(index) + '.png')



def _flabelformat(freq):
    """Formatted frequency labels"""
    label = '{0:5.2f}'.format(freq)
    if label in (' 0.00', '-0.00'):
        return ' '
    else:
        return label

def _qpt_freq_iter(ascii_file):
    """Generate tuples of qpt (as list) and frequency"""
    for txtline in _qpt_string_iter(ascii_file):
        listline = [float(x) for x in txtline.split(';')]
        yield(listline[0:3], listline[3])

def _qpt_string_iter(ascii_file):
    for match in _qpt_regex_iter(ascii_file):
        if match:
            yield match.group()
        

def _qpt_regex_iter(ascii_file):
    with open(ascii_file, 'r') as f:
        for line in f:         
            yield re.search('(?<=#metaData: qpt=\[).*(?= \\\\)', line)
