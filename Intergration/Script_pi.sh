#!/usr/bin/bash
#Script to run the laptop part of the code

#parts of code running, screenshot, FE,CF, Pipe
python3 ../../../School20Fall/ECEN_403/retro_gym/higan-nightly/higan-nightly/Pi\
pe_socket.py &
python3 CF_PI_SEND.py &
sleep 10s
echo "Lock three"
python3 FE_socket1.py &
python3 Screenshot_socket.py &
