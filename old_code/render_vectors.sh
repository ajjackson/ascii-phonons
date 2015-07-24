#! /bin/bash

#$HOME/blender-2.70a-linux-glibc211-x86_64/blender --background "cube.blend" --python test2.py -o //output/test### -s 0 -e 30 --render-format AVIRAW --render-anim
case $(hostname) in
    chpc-aw6.bath.ac.uk)
    BLENDER_BIN="/Applications/Blender/blender.app/Contents/MacOS/blender" ;;
    chmc-chlorine)
    BLENDER_BIN="$HOME/blender-2.70a-linux-glibc211-x86_64/blender" ;;    
esac

for MODENUM in {1..24}
do
sed "s/MODENUM/${MODENUM}/" vector_source.py > tmp_bpy.py

${BLENDER_BIN} --background "cube.blend" --python tmp_bpy.py -o //output/mode_${MODENUM}_vectors# --render-format PNG -f 0

done
