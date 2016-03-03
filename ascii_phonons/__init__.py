from os import path, remove
from subprocess import call
import tempfile
import re
import itertools

ascii_phonons_path = path.abspath(path.join(
    path.dirname(path.realpath(__file__)), path.pardir))
addons_path = path.join(ascii_phonons_path, 'addons')


def call_blender(**options):
    """Generate a temporary script file and call Blender

    Typically Blender is called in batch mode to render one or a series
    of .png image files.

    :param input_file: Path to .ascii file specifying crystal structure
        and vibrational modes
    :type input_file: str
    """
    blender_osx = "/Applications/Blender/blender.app/Contents/MacOS/blender"
    if not 'input_file' in options:
        raise Exception('No .ascii file provided')
    options['input_file'] = path.abspath(options['input_file'])
    if 'output_file' in options and options['output_file']:
        output_file = path.abspath(options['output_file'])
    handle, python_tmp_file = tempfile.mkstemp(suffix='.py', dir='.')

    if 'blender_bin' in options:
        call_args = [options['blender_bin']]
    else:
        import platform
        if platform.mac_ver()[0] != '':
            call_args = [blender_osx]
        else:
            call_args = ['blender']

    if options.get('static', False):
        n_frames = 1
    else:
        n_frames = options.get('n_frames', 30)

    if options.get('gif', False) and options.get('output_file', False):
        gif_name = options['output_file'] + '.gif'
        handle, image_tmp_filename = tempfile.mkstemp(dir='.')
        output_file = image_tmp_filename
        remove(image_tmp_filename)  # We only needed the name

    if 'config' in options:
        config = options['config']
    else:
        config = ''

    python_txt = """
import sys
from os.path import pathsep

sys.path = ['{add_path}'] + sys.path

import bpy
import vsim2blender
import vsim2blender.plotter

config = vsim2blender.read_config(user_config='{config}')

vsim2blender.plotter.open_mode(**{options})
vsim2blender.plotter.setup_render_freestyle(**{options})
vsim2blender.plotter.render(output_file='{out_file}', preview={preview})
""".format(options=str(options), add_path=addons_path, config=config,
           out_file=options.get('output_file', ''),
           preview=str(options.get('preview', False)))

    with open(python_tmp_file, 'w') as f:
        f.write(python_txt)

    if options.get('output_file', False) and not options.get('gui', False):
        call_args.append("--background")

    call_args = call_args + ["-P", python_tmp_file]
    call(call_args)

    remove(python_tmp_file)

    if options.get('gif', False) and options.get('output_file', False):
        tmp_files = [''.join((options['output_file'],
                              '{0:04.0f}'.format(i),
                              '.png'))
                     for i in range(n_frames)]
        convert_call_args = (['convert', '-delay', '10']
                             + tmp_files
                             + ['-loop', '0', gif_name])
        try:
            call(convert_call_args)
        except OSError as err:
            raise Exception("\n\nCould not run Imagemagick convert to" +
                            " create .gif.\n Error message: {0}\n".format(err)
                            + "Are you sure you have Imagemagick installed?\n")

        for f in tmp_files:
            remove(f)


def montage_static(**options):
    mode_data = list(_qpt_freq_iter(options['input_file']))

    for param, default in (('output_file', 'phonon'),):
        if not options[param]:
            options[param] = default

    call_args = ['montage', '-font', 'Helvetica', '-pointsize', '18']

    # Render smaller image
    options.update({'preview': True})

    output_basename = options['output_file']
    for index, (qpt, freq) in enumerate(mode_data):
        options.update({'output_file': '.'.join((output_basename,
                                                 str(index)))})
        options.update({'mode_index': index})
        call_blender(**options)
        call_args.extend(['-label', _flabelformat(freq),
                         options['output_file'] + '.png'])
    call_args.append(output_basename + '_montage.png')

    call(call_args)

    for index, (qpt, freq) in enumerate(mode_data):
        remove('.'.join((output_basename, str(index), 'png')))


def montage_anim(**options):
    mode_data = list(_qpt_freq_iter(options['input_file']))

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
        options.update({'output_file': '.'.join((output_basename,
                                                 str(index), ''))})
        options.update({'mode_index': index})
        call_blender(**options)
        labels.append(_flabelformat(freq))

    print("Compiling tiled images...")

    frames = range(options['start_frame'], options['end_frame'] + 1)
    for frame in frames:
        montage_call_args = ['montage', '-font', 'Helvetica',
                             '-pointsize', '18']
        for index, label in enumerate(labels):
            montage_call_args.extend(['-label', label,
                                      '.'.join((output_basename,
                                                '{0}'.format(index),
                                                '{0:04d}'.format(frame),
                                                'png'))])

        montage_call_args.append('.'.join((output_basename,
                                           '{0}'.format(frame),
                                           'montage.png')))
        try:
            call(montage_call_args)
        except OSError as err:
            raise Exception("\n\nCould not run Imagemagick convert to create "
                            ".gif.\n Error message: {0}\n".format(err) +
                            "Are you sure you have Imagemagick installed?\n")

    print("Joining images into .gif file")

    convert_call_args = (['convert', '-delay', '10']
                         + ['.'.join((output_basename, '{0}'.format(frame),
                            'montage.png')) for frame in frames]
                         + ['-loop', '0', output_basename + '.gif'])
    call(convert_call_args)
    print("Cleaning up...")
    for frame in frames:
        for index in range(len(labels)):
            remove('.'.join((output_basename, '{0}'.format(index),
                             '{0:04d}'.format(frame), 'png')))
        remove('.'.join((output_basename, '{0}'.format(frame),
                         'montage', 'png')))

    print("Done!")


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
