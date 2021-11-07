# ASM-rpi-node
Aye-Aye Sleep Monitoring Project Raspberry Pi Node

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