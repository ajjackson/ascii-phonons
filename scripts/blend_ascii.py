#! /usr/bin/env python

from __future__ import print_function
import argparse
import os
import sys

pathname = os.path.abspath(sys.argv[0])
project_root = os.path.dirname(os.path.dirname(pathname))
sys.path = [project_root] + sys.path
import ascii_phonons

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to input file. ASCII formatted for v_sim.")
    parser.add_argument("-b", "--blender_bin", help="Path to Blender binary",
                        default=False)
    parser.add_argument("-m","--mode_index", default=0,
                        help="Zero-based position of mode in ASCII file")
    parser.add_argument("-d","--supercell_dimensions", nargs=3, default=(2,2,2),
                        help="Supercell dimensions; set of three integers")
    parser.add_argument("-s","--static", action="store_true",
                        help="Static image (disable animation)")
    parser.add_argument("-f","--n_frames", type=int, default=30,
                        help="Number of frames in a complete cycle (default number of frames for animation)")
    parser.add_argument("--start_frame", type=int, default=None,
                        help="Starting frame number for the animation")
    parser.add_argument("--end_frame", type=int, default=None,
                        help="Ending frame number for the animation")
    parser.add_argument("-o","--output_file", default=False,
                        help="Render to output. GUI will not open for further editing unless -g (--gui) flag is used")
    parser.add_argument("-g", "--gui", action="store_true", help="Open full Blender GUI session, even if rendering output")
    parser.add_argument("--gif", action="store_true", help="Create a .gif file using Imagemagick convert. This flag is ignored if no output file is specified.")
    parser.add_argument("-v","--vectors", action="store_true", help="Indicate eigenvectors with static arrows.")
    parser.add_argument("--scale_factor", type=float, default=1.0,
                        help="Size of atoms, relative to covalent radius")
    parser.add_argument("--vib_magnitude", type=float, default=1.0,
                        help="Normalised magnitude of animated phonons")
    parser.add_argument("--arrow_magnitude", type=float, default=20.0,
                        help="Normalised magnitude of static arrows")
    parser.add_argument("--no_box", default=False, action="store_true",
                        help="Hide bounding box")
    parser.add_argument("--box_position", nargs=3, type=float, default=(0,0,0),
                        help="Bounding box position (lattice coordinates)")
    parser.add_argument("--miller", nargs=3, type=float, default=(0,1,0),
                        help="Miller indices for view")
    parser.add_argument("--camera_rot", type=float, default=0,
                        help="View rotation in degrees")
    parser.add_argument("--zoom", type=float, default=1.,
                        help="Camera zoom adjustment")
    parser.add_argument("--config", type=str, default='',
                        help="User configuration file")
    parser.add_argument("--do_mass_weighting", action="store_true",
                        help="Apply mass weighting to atom movements. This has usually already been done in the construction of the .ascii file, and should not be repeated.")

    args = parser.parse_args()


    user_config = args.config    
    if user_config == '':
        pass
    else:
        user_config == os.path.abspath(user_config)
        
    print(user_config)

    ascii_phonons.call_blender(args.input_file,
         blender_bin=args.blender_bin, mode_index=args.mode_index,
         supercell=args.supercell_dimensions, animate=(not
         args.static), n_frames=args.n_frames,
         start_frame=args.start_frame,
         end_frame=args.end_frame,
         scale_factor=args.scale_factor,
         vib_magnitude=args.vib_magnitude,
         user_config=user_config,
         arrow_magnitude=args.arrow_magnitude, vectors=args.vectors,
         output_file=args.output_file, gif=args.gif, bbox=(not args.no_box),
         bbox_offset=args.box_position, miller=args.miller, zoom=args.zoom,
         camera_rot=args.camera_rot, do_mass_weighting=args.do_mass_weighting)

