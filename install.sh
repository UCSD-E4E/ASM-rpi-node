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

if [[ ${DEBUG} -eq 1]]; then
    python3 -m pip install -e .
else
    python3 -m pip install .
fi

