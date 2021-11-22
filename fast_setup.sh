#!/bin/bash
sudo apt-get update --allow-releaseinfo-change
sudo apt-get upgrade -y
sudo apt-get install -y git glances htop vim tmux python3-pip ffmpeg
git clone https://github.com/UCSD-E4E/ASM_protocol.git
git clone https://github.com/UCSD-E4E/ASM-rpi-node.git
cd ASM_protocol
sudo python3 -m pip install .
cd ..
cd ASM-rpi-node
sudo ./install.sh
sudo vim /boot/asm_config.yaml