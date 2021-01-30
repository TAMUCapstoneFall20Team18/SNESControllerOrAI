#!/usr/bin/python3


##TODO Get switch working so the log only works when the AI is on
#Perhaps in a later model, the log can be read right back into the system, making it
#more general

##for later more general uses, screenshot function, RM stays, but everything else
#chagne
import time
import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT_RECEIVE = 9084     # Port to listen on (non-privileged ports are > 1023)
DAEMON_NAME  = "Pipe_socket"
# f = open("./byuu.simulated_keypresses.txt","ab")

def setup_sockets():
    global s_receive
    s_receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Daemon {} binding to {}".format(DAEMON_NAME, PORT_RECEIVE))
    s_receive.bind((HOST, PORT_RECEIVE))

    print("{} set".format(DAEMON_NAME))

def closesocket():
    global s_receive
    if s_receive != '':
     s_receive.shutdown(socket.SHUT_RDWR)
     s_receive.close()
    print(f"Closed sockets {DAEMON_NAME}")
  

def main():
    global s_receive, s_send

    
    f = open("/home/widman/Documents/School20Fall/ECEN_403/retro_gym/higan-nightly/higan-nightly/myfifo","wb")
    ##Will need to be edited in 404   
    #if ai_selector == 1:

    #at full speed this indicator could be the logging function
    f.write(b'1') ## to initiate switch to AI from manual play (Changes speed)
    f.flush()
    while True:
        s_receive.listen()
        conn, addr = s_receive.accept()
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                keypress = ''
                break
            keypress = int(data.decode())
            
            print(f"Input from NN {keypress} presses")
            ##Have a ignore switch for 
            while keypress > 0:
                f.write(b'a')
                f.flush()
                time.sleep(0.1)
                keypress -= 1
            
    f.close()

try:
    setup_sockets()
    main()
finally:
    f = open("/home/widman/Documents/School20Fall/ECEN_403/retro_gym/higan-nightly/higan-nightly/myfifo","wb")
    f.write(b'2')
    f.flush()
    f.close()
    closesocket()
