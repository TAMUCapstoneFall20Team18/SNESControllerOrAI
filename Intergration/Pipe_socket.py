#!/usr/bin/python3


##TODO Get switch working so the log only works when the AI is on
#Perhaps in a later model, the log can be read right back into the system, making it
#more general


##2021-01-23
##CHANGES Changed to allow for a random amout of change to the keypress
#2021-02-06
#CHANGES: Socket manipulation and begining of implimentation of regex filtering

import time
import socket
import random
import re

#hostMACAddress = 'BC:14:EF:A3:39:3C'
hostMACAddress = 'BC:14:EF:A3:BE:73'
recieve_port = 8 ##bluetooth for RM socket ##This is becuase currently looking at one port
backlog = 3
size = 1024 ##size of the buffer

def socket_setup(): ##Sets up the bluetooth socket
    global s_blue
    s_blue = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s_blue.bind((hostMACAddress, recieve_port))
    s_blue.listen(backlog)
    print("Bluetooth from Emulator up")

def close_socket(): ##final closing socket
    global s_blue, s_receive
    s_receive.shutdown(socket.SHUT_RDWR)
    s_receive.close()
    s_blue.close()
    print(f"Closed sockets pipe_socket")

def generate_rand_pulse():
    rand_selector = random.randint(0, 1000)
    #print(rand_selector)
    if rand_selector >=600:
        return True
    return False

def main():
    #global s_receive, s_send
    global s_blue, s_receive
    f = open("/home/widman/Documents/School20Fall/ECEN_403/retro_gym/higan-nightly/higan-nightly/myfifo","wb")
    count = 0
    while True:

        #p1 = re.compile("^\d{3}") #assuming that the 16 vector is longer than 3 digits
        p2 = re.compile("^[a]+|[tf]{1}")
        p3 = re.compile("^\d{1,2}")
        s_receive, address = s_blue.accept()
        try:
            
            while True:
                data = s_receive.recv(size)
                if not data:
                    keypress = ''
                    break
                keypress = 0
                data_input = data.decode()
                print(f"This is the data receieved {data_input}")
##                if data_input:
##                    f.write(b'a')
##                    f.flush()
                #print(type(data_input))
                #m1 = p1.match(data_input)
                m2 = p2.match(data_input)
                m3 = p3.match(data_input)
##                if m1: #this is if 16 bit vector
##                    keypress = 0
##                    print(f"16 vector")
##                    break
                if m2:
                    print(f"From Pi {data_input}")
                    if data_input == 't': ##AI is ON now
                        f.write(b'1')
                        f.flush()
                    elif data_input == 'f': ## AI is OFF now
                        f.write(b'2')
                        f.flush()
                    else: ##FIX only one input per press, no holding possible per poll
                        keypress_input = re.findall('a', data_input)
                        for i in range(0, len(keypress_input)):
                            print(f"This is press num {i}")
                            f.write(b'a')
                            f.flush()        ##Count A's and print as count
                            #time.sleep(0.01)
                            count += 1

                elif m3:
                    keypress = int(data_input)
                    add_pulse = generate_rand_pulse()
                    if add_pulse == True:
                        keypress += 1
                    print(f"Input to pipe is {keypress} presses")
                    
                    while keypress > 0: ##This needs the delay pulse
                        f.write(b'a')
                        f.flush()
                        time.sleep(0.1)
                        keypress -= 1

                else:
                    break
                    
    
        except Exception as e:
            print(f"Error {e}")
            print(f"The 'a' count is {count}")
            
        
    f.close()

try:
    socket_setup()
    main()
finally:
    close_socket()
