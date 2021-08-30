#!/bin/bash
DEBUG=0

if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

usage() {
    echo "${0} usage: "
    echo "    -d    Specify debug"
    echo "    -h    Display this message"
}

while getopts ":d" arg; do
    case $arg in
        d)
            DEBUG=1
            ;;
        *)
            usage
            ;;        
    esac
done

if [[ ${DEBUG} -eq 1 ]]; then
    python3 -m pip install -e .
else
    python3 -m pip install .
fi

if [[ ${DEBUG} -eq 0 ]]
then
    if [ -d /boot ]
    then
        if [ ! -f /boot/asm_config.yaml ]
        then
            cp test_config.yaml /boot/asm_config.yaml
        fi
    fi
    
    cp asm_sensor_node.service /lib/systemd/system/asm_sensor_node.service
    chmod 644 /lib/systemd/system/asm_sensor_node.service
    systemctl daemon-reload
    systemctl enable asm_sensor_node.service
    echo "ASM Sensor Node will start on next reboot"

fi