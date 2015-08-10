#! /usr/bin/env python

import argparse
import os
from subprocess import call
import tempfile

def main(input_file, blender_bin, mode_index=0, animate=True, n_frames=30,
         vectors=False, output_file=False, gui=False, gif=False, scale_factor=1.0):
    input_file = os.path.abspath(input_file)
    if output_file:
        output_file = os.path.abspath(output_file)
    handle, python_tmp_file = tempfile.mkstemp(suffix='.py', dir='.')

    if not animate:
        n_frames=1

    if gif:
        gif_name = output_file + '.gif'
        handle, image_tmp_filename = tempfile.mkstemp(dir='.')
        output_file = image_tmp_filename
        os.remove(image_tmp_filename) # We only needed the name
    
    python_txt = """
import bpy
import vsim2blender.plotter

vsim2blender.plotter.open_mode('{0}', {1}, animate={2}, n_frames={3}, vectors={4}, scale_factor={5})
vsim2blender.plotter.setup_render(n_frames={3})
vsim2blender.plotter.render(output_file='{6}')
""".format(input_file, mode_index, animate, n_frames, vectors, scale_factor, output_file)

    with open(python_tmp_file, 'w') as f:
        f.write(python_txt)

    if output_file and not gui:
        call((blender_bin, "--background", "-P", python_tmp_file))
    else:
        call((blender_bin, "-P", python_tmp_file))

    os.remove(python_tmp_file)

    if gif:
        tmp_files = [image_tmp_filename + '{0:04.0f}'.format(i) + '.png' for i in range(n_frames)]
        convert_call_args = ['convert', '-delay', '10'] + tmp_files + ['-loop', '0', gif_name]
        call(convert_call_args)
        for f in tmp_files:
            os.remove(f)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to input file. ASCII formatted for v_sim.")
    parser.add_argument("-b", "--blender_bin", help="Path to Blender binary",
                        default="blender")
    parser.add_argument("-m","--mode_index", help="Zero-based position of mode in ASCII file")
    parser.add_argument("-s","--static", action="store_true",
                        help="Static image (disable animation)")
    parser.add_argument("-f","--n_frames", type=int,
                        help="Number of frames in animation")
    parser.add_argument("-o","--output_file", help="Render to output. GUI will not open for further editing unless -g (--gui) flag is used")
    parser.add_argument("-g", "--gui", action="store_true", help="Open full Blender GUI session, even if rendering output")
    parser.add_argument("--gif", action="store_true", help="Create a .gif file using Imagemagick convert")
    parser.add_argument("-v","--vectors", action="store_true", help="Indicate eigenvectors with static arrows.")
    parser.add_argument("--scale_factor", type=float, help="Size of atoms, relative to covalent radius")

    args = parser.parse_args()

    main(args.input_file, args.blender_bin, mode_index=args.mode_index,
         animate=(not args.static), n_frames=args.n_frames, scale_factor=args.scale_factor,
         vectors=args.vectors, output_file=args.output_file, gif=args.gif)

