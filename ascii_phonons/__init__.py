from os import path, remove
from subprocess import call
import tempfile
import re
import platform
from json import loads

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

ascii_phonons_path = path.abspath(path.join(
    path.dirname(path.realpath(__file__)), path.pardir))
addons_path = path.join(ascii_phonons_path, 'addons')


class Opts(object):
    def __init__(self, options, parser=False):
        """Robust option-handling for ascii-phonons GUI and CLI

        Prioritises named options over config files.
        If a configparser object is not explicitly provided, looks for
        file in 'config' option.

        Note that Opts objects use the original dictionary object rather
        than a copy, and hence tracks the state of the options as they
        are updated.

        :param options: Collection of named options. Typically obtained
            by defining an outer function as fun(**options).
        :type options: dict
        :param parser: Optionally provide a ConfigParser object which
            has already been instantiated. If not provided, a new one
            will be created if there is a 'config' item in ``options``.
        :type parser: configparser.ConfigParser

        """
        self.options = options
        self.config = parser

        if not parser and 'config' in options:
            self.config = configparser.ConfigParser()
            self.config.read(options['config'])

        self.bool_keys = (
            'do_mass_weighting',
            'gif',
            'gui',
            'montage',
            'show_box',
            'static')

        self.float_keys = (
            'box_thickness',
            'camera_rot',
            'outline_thickness'
            'scale_arrow',
            'scale_atom',
            'scale_vib',
            'zoom')

        self.int_keys = (
            'end_frame',
            'mode_index',
            'n_frames',
            'start_frame')

        self.tuple_keys = (
            'offset_box',
            'supercell')

    def get(self, key, fallback):
        """Get parameter, prioritising named options over config file

        :param key: Name of option
        :type key: str
        :param fallback: Fallback value if key is not found in options
            or config
        :type fallback: any

        """
        if key in self.options:
            return self.options[key]
        elif self.config and self.config.has_option('general', key):
            if key in self.bool_keys:
                return self.config.getboolean('general', key)
            elif key in self.float_keys:
                return self.config.getfloat('general', key)
            elif key in self.int_keys:
                return self.config.getint('general', key)
            elif key in self.tuple_keys:
                return tuple(map(float,
                                 self.config.get('general, key').split()
                                 ))
            else:
                return self.config.get('general', key)
        else:
            return fallback


def call_blender(**options):
    """Generate a temporary script file and call Blender

    Typically Blender is called in batch mode to render one or a series
    of .png image files.

    """
    blender_osx = ("/Applications/Blender/blender.app" +
                   "/Contents/MacOS/blender")

    opts = Opts(options)

    input_file = opts.get('input_file', False)
    output_file = opts.get('output_file', False)

    for f in input_file, output_file:
        if f:
            f = path.abspath(f)

    handle, python_tmp_file = tempfile.mkstemp(suffix='.py', dir='.')

    if platform.mac_ver()[0] != '':
        blender_default = blender_osx
    else:
        blender_default = 'blender'

    call_args = [opts.get('blender_bin', blender_default)]

    if opts.get('static', False):
        n_frames = 1
    else:
        n_frames = opts.get('n_frames', 30)

    if opts.get('gif', False) and output_file:
        gif_name = output_file + '.gif'
        handle, image_tmp_filename = tempfile.mkstemp(dir='.')
        output_file = image_tmp_filename
        remove(image_tmp_filename)  # We only needed the name

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
vsim2blender.plotter.render(output_file='{out_file}',
                            preview='{preview}')
""".format(options=str(options), add_path=addons_path,
           config=opts.get('config', ''),
           out_file=output_file,
           preview=opts.get('preview', ''))

    with open(python_tmp_file, 'w') as f:
        f.write(python_txt)

    if not opts.get('gui', False):
        call_args.append("--background")

    call_args = call_args + ["-P", python_tmp_file]
    call(call_args)

    remove(python_tmp_file)

    if opts.get('gif', False) and output_file and not opts.get('static',
                                                               False):
        frames = range(opts.get('start_frame', 0),
                       opts.get('end_frame',
                                opts.get('n_frames', 30)) + 1)
        tmp_files = [''.join((output_file,
                              '{0:04.0f}'.format(i),
                              '.png'))
                     for i in frames]
        convert_call_args = (['convert', '-delay', '10'] +
                             tmp_files + ['-loop', '0', gif_name])
        try:
            call(convert_call_args)
        except OSError as err:
            raise Exception("\n\nCould not run Imagemagick convert" +
                            " to create .gif.\n Error message:" +
                            " {0}\nAre you sure".format(err) +
                            " you have Imagemagick installed?\n")

        for f in tmp_files:
            remove(f)


def montage_static(**options):
    """Render images for all phonon modes and present as array"""
    opts = Opts(options)
    mode_data = list(_qpt_freq_iter(opts.get('input_file', None)))

    for param, default in (('output_file', 'phonon'),):
        if not opts.get(param, False):
            options[param] = default

    call_args = ['montage', '-font', 'Helvetica', '-pointsize', '18']

    # The output filename is used as the root for temporary images
    # These are requested as "preview" images to reduce rescaling
    output_basename = opts.get('output_file', 'phonon')

    for index, (qpt, freq) in enumerate(mode_data):
        options.update({'preview': '.'.join((output_basename,
                                                 str(index)))})
        options.update({'mode_index': index})
        call_blender(**options)
        call_args.extend(['-label', _flabelformat(freq),
                         options['preview'] + '.png'])
    call_args.append(output_basename + '_montage.png')

    call(call_args)

    for index, (qpt, freq) in enumerate(mode_data):
        remove('.'.join((output_basename, str(index), 'png')))


def montage_anim(**options):
    """Render animations for all phonon modes and present as array"""
    opts = Opts(options)
    mode_data = list(_qpt_freq_iter(opts.get('input_file', None)))

    for param, default in (('output_file', 'phonon'),
                           ('start_frame', 0),
                           ('n_frames', 30)):
        if not opts.get(param, False):
            options[param] = default

    if not opts.get('end_frame', False):
        options['end_frame'] = (opts.get('start_frame', 0) +
                                opts.get('n_frames', 30) - 1)

    # Render smaller image, take over gif generation
    # 'static' is explicitly set to False to override
    # 'preview' defaults
    options.update({'gif': False, 'static': False})
    output_basename = opts.get('output_file', 'phonon')
    labels = []
    for index, (qpt, freq) in enumerate(mode_data):
        options.update({'preview': '.'.join((output_basename,
                                             str(index), ''))})
        options.update({'mode_index': index})
        call_blender(**options)
        labels.append(_flabelformat(freq))

    print("Compiling tiled images...")

    frames = range(opts.get('start_frame', 0),
                   opts.get('end_frame', 29) + 1)

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
            raise Exception("\n\nCould not run Imagemagick convert " +
                            "to create .gif.\n Error message: " +
                            "{0}\nAre you sure you have".format(err) +
                            " Imagemagick installed?\n")

    print("Joining images into .gif file")

    convert_call_args = (['convert', '-delay', '10'] +
                         ['.'.join((output_basename,
                                    '{0}'.format(frame),
                                    'montage.png'))
                          for frame in frames] +
                         ['-loop', '0', output_basename + '.gif'])
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

def parse_tuple(tuple_string, value_type=float):
    """Get a tuple back from string representation

    Three representations are recognised:
    '[1,2,3]' : JSON-style
    '1 2 3' : Simple space-separated
    '1,2,3': Simple comma-separated

    :param tuple_string: Serialised tuple
    :type tuple_string: str
    :param value_type: Type to cast values to
    :type value_type: type
    """
    if '[' in tuple_string:
        return tuple(map(value_type, loads(tuple_string)))
    elif ',' in tuple_string:
        return tuple(map(value_type,
                         tuple_string.split(',')))
    else:
        return tuple(map(value_type,
                         tuple_string.split()))
