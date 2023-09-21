# ASM-rpi-node
Aye-Aye Sleep Monitoring Project Raspberry Pi Node

This project is currently inactive.  If you are interested in contributing to this project, please contact Engineers for Exploration at e4e@ucsd.edu.

## Installation on a Raspberry Pi
1.  Install RaspiOS on the Raspberry Pi's SD card.
2.  Create the proper `wpa_supplicant.conf` file in the SD Card's boot partition.
3.  Create the `ssh` file in the SD Card's boot partition.
4.  Boot the Pi.
5.  SSH into the Pi.
6.  Change the password
7.  Run `sudo raspi-config`
8.  Under `Advanced Options`, select `Expand Filesystem`
9.  Under `System Optiosn`, select `Change Hostname`
10. Change the hostname to `f'asm-{uuid}'`, where uuid is the UUID assigned to this system.
11. Run `Update`
12. Select `Finish`
13. Allow the Pi to reboot, and SSH back in.
14. Run `sudo apt-get update --allow-releaseinfo-change`
15. Run `sudo apt-get upgrade -y`
16. Run `sudo apt-get install -y git glances htop vim tmux python3-pip ffmpeg`
17. Run `git clone https://github.com/UCSD-E4E/ASM_protocol.git`
18. Run `git clone https://github.com/UCSD-E4E/ASM-rpi-node.git`
19. Navigate into `ASM_protocol`
20. Run `sudo python3 -m pip install .`
21. Navigate into `ASM-rpi-node`
22. Run `sudo ./install.sh`
23. Edit `/boot/asm_config.yaml` as needed.

# Instructions to Run
## Development
1. Open this repository as a VS Code Workspace
2. Use the Run and Debug menu to execute the server.
3. In this mode, the server will log to the user log directory.  On Linux, this is usually `${HOME}/.cache/ASMSensorNode/asm_sensor_node.log`.
## Deployment
1. Run `sudo ./install.sh`
2. Run `sudo service asm_sensor_node restart`
3. In this mode, the server will log to the system log directory.  On Linux, this is usually `/var/log/asm_sensor_node.log`.

# Configuration Files
1. The Data Server will search the following locations for the `asm_config.yaml` configuration file:
    - `/boot/asm_config.yaml`
    - `/usr/local/etc/asm_config.yaml`
    - `${CWD}`
