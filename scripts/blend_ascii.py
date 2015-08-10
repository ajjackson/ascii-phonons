#! /usr/bin/env python

import argparse
import os
from subprocess import call
import tempfile

def main(input_file, blender_bin, mode_index=0, animate=True, n_frames=30):
    input_file = os.path.abspath(input_file)
    handle, python_tmp_file = tempfile.mkstemp(suffix='.py', dir='.')

    if not animate:
        n_frames=1
    
    python_txt = """
import bpy
import vsim2blender.plotter

vsim2blender.plotter.open_mode('{0}', {1}, animate={2}, n_frames={3})
vsim2blender.plotter.setup_render(n_frames={3})
""".format(input_file, mode_index, animate, n_frames)

    with open(python_tmp_file, 'w') as f:
        f.write(python_txt)
        
    call((blender_bin, "-P", python_tmp_file))

    os.remove(python_tmp_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to input file. ASCII formatted for v_sim.")
    parser.add_argument("-b", "--blender_bin", help="Path to Blender binary",
                        default="blender")
    parser.add_argument("-m","--mode_index", help="Zero-based position of mode in ASCII file")
    parser.add_argument("-s","--static", action="store_true",
                        help="Static image (disable animation)")
    parser.add_argument("-f","--n_frames", help="Number of frames in animation")

    args = parser.parse_args()

    main(args.input_file, args.blender_bin, mode_index=args.mode_index,
         animate=(not args.static), n_frames=args.n_frames)

    
