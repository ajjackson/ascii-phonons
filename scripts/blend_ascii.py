import argparse
import os
from subprocess import call
import tempfile

def main(input_file, blender_bin):
    input_file = os.path.abspath(input_file)
    handle, python_tmp_file = tempfile.mkstemp(suffix='.py', dir='.')

    python_txt = """
import bpy
import vsim2blender.plotter
vsim2blender.plotter.main('{0}')""".format(input_file)

    with open(python_tmp_file, 'w') as f:
        f.write(python_txt)
        
    call((blender_bin, "-P", python_tmp_file))

    os.remove(python_tmp_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to input file. ASCII formatted for v_sim.")
    parser.add_argument("--blender_bin", help="Path to Blender binary",
                        default="blender")

    args = parser.parse_args()

    main(args.input_file, args.blender_bin)

    
