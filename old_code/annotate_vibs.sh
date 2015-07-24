#! /bin/bash

for ACOUSTIC_MODE in 1 2 3
do
    for FILE in ../output/mode_${ACOUSTIC_MODE}_*.png
    do
        cp ${FILE} $(basename ${FILE})
    done
done

for A_MODE in 16 17 20
do 
    for FILE in ../output/mode_${A_MODE}_*.png
    do
        convert ${FILE} -fill black -pointsize 80 -font Times -gravity southwest -annotate +60+60 A $(basename ${FILE})
    done
done

for B_MODE in 6 9 12 13 21 24
do 
    for FILE in ../output/mode_${B_MODE}_*.png
    do
        convert ${FILE} -fill black -pointsize 80 -font Times -gravity southwest -annotate +60+60 B $(basename ${FILE})
    done
done

 
for E_MODE in 4 5 7 8 10 11 14 15 18 19 22 23
do 
    for FILE in ../output/mode_${E_MODE}_*.png
    do
        convert ${FILE} -fill black -pointsize 80 -font Times -gravity southwest -annotate +60+60 E $(basename ${FILE})
    done
done
