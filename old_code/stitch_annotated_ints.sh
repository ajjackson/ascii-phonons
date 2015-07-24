NMODES=24

FREQUENCIES=( index_placeholder 0.057495   0.050280   0.031286   76.120793   76.131193   88.634752   97.495547   97.501471  100.243743  158.305476  158.307024  171.169670  252.216924  263.185162  263.204227  290.870561  295.372198  299.064820  299.074485  316.703611  317.196958  325.331911  325.355006  340.058731 )

montage $(
for MODE in $(seq 1 ${NMODES})
do
    printf "%s %5.0f " "-label " ${FREQUENCIES[$MODE]}
    echo "annotated/mode_${MODE}_vectors0.png"
done
echo "-label key lighter_key.png"
) montage_annotated_vectors.png

