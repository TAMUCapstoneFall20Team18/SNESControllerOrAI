#!/usr/bin/bash 
##MUST RUN BYUU FROM Retro-Gym/higan-nightly/higan-nightly/byuu/out/byuu
##Cannot start ./byuu because it takes a while to load and select jpr, and screenshot currently does not wait that long.
## could have it so that the program activates when something in higan changes or when picture is found. 
## Round 2 need to be able to turn this on and off

##checks for if the switch is on
##if switch in on AI mode:
##Maybe ignore the input to pipesocket unless the AI switch is on? 
## Consider switching host to a different IP bc localhost is not the same for the laptop and the raspberry pi
python3 RM_socket.py &
echo "Lock one"
python3 ../../../School20Fall/ECEN_403/retro_gym/higan-nightly/higan-nightly/Pipe_socket.py &  ##Higan stays
sleep 5s
echo "Lock two"
python3 CF_socket.py &
sleep 1s
echo "Lock three"
python3 FE_socket1.py &
python3 Screenshot_socket.py &

##else: killall python3

##for number in {1..60}
##do
##sleep 5s
#echo $number
##done
##killall python3
#netstat -ap | grep 908
