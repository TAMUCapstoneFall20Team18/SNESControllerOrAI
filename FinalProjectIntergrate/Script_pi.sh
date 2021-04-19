#!/usr/bin/bash
#Script to run the laptop part of the code

#parts of code running, screenshot, FE,CF, Pipe
python3 ../../../School20Fall/ECEN_403/retro_gym/higan-nightly/higan-nightly/Pi\
pe_socket.py &
python3 CF_PI_SEND.py &
while :; do
    # TASK 1

    read -t 0 -r -N 1 && { read -r; break; }
done
echo "Lock three"
python3 FE_socket1.py &
sleep 3s
python3 Screenshot_socket.py &
##Watchdog for 15 min gameplay?
