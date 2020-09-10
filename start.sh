#!/bin/bash


TMPFOLDER="/dev/shm/ropship"
echo "$TMPFOLDER"

#rm -r "$TMPFOLDER" # we don't want to delete /dev/shm/ropship/inputs

#these 2 should be already existing
mkdir "$TMPFOLDER"
INPUTSFOLDER="$TMPFOLDER/inputs"
mkdir "$INPUTSFOLDER"




echo "==="
if [[ "$1" == "simulated" ]]; then
    echo "$INPUTSFOLDER"
    rm "$INPUTSFOLDER/team*"
    cp inputs/team* "$INPUTSFOLDER/"
    DEFCONROUND="134"
    TEAMS="1-412a302a45_2-2f62696e2f7477_3-43796b6f72_4-484954434f4ee29a9442464b696e65736953_5-6b6f7265616e626164617373_6-6d6861636b65726f6e69_7-4d6f7265204275736820536d6f6b656420576861636b657273_8-4e6f727365636f6465_9-70617374656e_10-506c616964205061726c69616d656e74206f662050776e696e67_11-72336b61706967_12-727069736563_13-53616d75726169_14-5368656c6c7068697368_15-537461722d42756773_16-5465612044656c69766572657273"
    NROUNDS=200
    echo "==="
    #sleep 10

elif [[ "$1" == "simulated2" ]]; then
    echo "$INPUTSFOLDER"

    DEFCONROUND="137"
    TEAMS="1-412a302a45_2-2f62696e2f7477_3-43796b6f72_4-484954434f4ee29a9442464b696e65736953_5-6b6f7265616e626164617373_6-6d6861636b65726f6e69_7-4d6f7265204275736820536d6f6b656420576861636b657273_8-4e6f727365636f6465_9-70617374656e_10-506c616964205061726c69616d656e74206f662050776e696e67_11-72336b61706967_12-727069736563_13-53616d75726169_14-5368656c6c7068697368_15-537461722d42756773_16-5465612044656c69766572657273"
    NROUNDS=1000
    echo "==="
    #sleep 10


else
    DEFCONROUND="$1"
    TEAMS="$2"
    NROUNDS=1000
fi


python3 -u simulatoraiparallel.py "$DEFCONROUND" "$TEAMS" "$NROUNDS" 2>&1 | tee -a "/var/tmp/ropship.log"

