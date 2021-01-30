#!/usr/bin/python3


##TODO Get switch working so the log only works when the AI is on
#Perhaps in a later model, the log can be read right back into the system, making it
#more general

##This manual may need a secondary port to listen to. This will complicate things
##   as I will need the manual to send a message when changed and have listening to that
##This will be fun.
##for later more general uses, screenshot function, RM stays, but everything else
#chagne

##2021-01-23
##CHANGES Changed to allow for a random amout of change to the keypress
import time
import socket
import random
import re

##HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
##PORT_RECEIVE = 9084     # Port to listen on (non-privileged ports are > 1023)
##DAEMON_NAME  = "Pipe_socket"
### f = open("./byuu.simulated_keypresses.txt","ab")
##
##def setup_sockets():
##    global s_receive
##    s_receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##    print("Daemon {} binding to {}".format(DAEMON_NAME, PORT_RECEIVE))
##    s_receive.bind((HOST, PORT_RECEIVE))
##
##    print("{} set".format(DAEMON_NAME))
##
##def closesocket():
##    global s_receive
##    if s_receive != '':
##     s_receive.shutdown(socket.SHUT_RDWR)
##     s_receive.close()
##    print(f"Closed sockets {DAEMON_NAME}")
##
hostMACAddress = 'BC:14:EF:A3:39:3C'
recieve_port = 6 ##bluetooth for RM socket
backlog = 1
size = 1024 ##size of the buffer

def socket_setup():
    global s_blue
    s_blue = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s_blue.bind((hostMACAddress, recieve_port))

def close_socket():
    global s_blue
    s_receive.shutdown(socket.SHUT_RDWR)
    s_receive.close()
    print(f"Closed sockets {PORT_RECEIVE}")

def generate_rand_pulse():
    rand_selector = random.randint(0, 1000)
    #print(rand_selector)
    if rand_selector >=600:
        return True
    return False

def main():
    #global s_receive, s_send
    global s_blue
    f = open("/home/widman/Documents/School20Fall/ECEN_403/retro_gym/higan-nightly/higan-nightly/myfifo","wb")
    ##Will need to be edited in 404   
    #if ai_selector == 1:
    
    #at full speed this indicator could be the logging function
##    f.write(b'1') ## to initiate switch to AI from manual play (Changes speed)
##    f.flush()
    
    while True:
##        s_receive.listen()
##        conn, addr = s_receive.accept()
##        print('Connected by', addr)
##        while True:
##            data = conn.recv(1024)
##            if not data:
##                keypress = ''
##                break
        p1 = re.compile("^\d{3}") #assuming that the 16 vector is longer than 3 digits
        p2 = re.compile("^\[atf]{1}")
        p3 = re.compile("^\d{1,2}")
        ##button press for manual
        #key; a is button press, t is AI on, f is AI off
        
        s_receive, address = s_blue.accept()
        s_blue.listen(backlog)
        
        try:
            while True:
                    data = s_receive.recv(size)
                    if not data:
                        keypress = ''
                        break
                    m1 = p1.match(data)
                    m2 = p2.match(data)
                    m3 = p3.match(data)
                    if m1: #this is if 16 bit vector
                        keypress = ''
                        break
                    if m2:
                        if data == 't':
                            f.write(b'1')
                            f.flush()
                        if data == 'f':
                            f.write(b'2')
                            f.flush()
                        elif data == 'a':
                            f.write(b'a')
                            f.flush()                          

                    if m3:
                        keypress = int(data.decode())
                        add_pulse = generate_rand_pulse()
                        if add_pulse == True:
                            keypress += 1
                        print(f"Input to pipe is {keypress} presses")
                        
                        while keypress > 0: ##This needs the delay pulse
                            f.write(b'a')
                            f.flush()
                            time.sleep(0.1)
                            keypress -= 1

                    
                    
    
        except:
            print("Closing socket")
            s_receive.close()
            s_blue.close()
        
    f.close()

try:
    socket_setup()
    main()
finally:
    #f = open("/home/widman/Documents/School20Fall/ECEN_403/retro_gym/higan-nightly/higan-nightly/myfifo","wb")
    #f.write(b'2')
    #f.flush()
    #f.close()
    closesocket()
