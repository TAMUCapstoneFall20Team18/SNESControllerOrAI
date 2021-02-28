import socket
import random as rand

import socket

#hostMACAddress = 'BC:14:EF:A3:39:3C'
hostMACAddress = 'BC:14:EF:A3:BE:73'
port = 7
msg = [10,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600]
backlog = 1
size = 1024
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s.bind((hostMACAddress, port))
s.listen(backlog)
try:
        client, address = s.accept()
        listToStr = ' '.join(map(str, msg))
        print(listToStr)
        client.send(bytes(listToStr, 'UTF-8'))
        while 1:
                data = client.recv(size)
                if data:
                        print(data)
			# This can be any data:
                        # client.send(bytes(msg, 'UTF-8'))
except Exception as e:
        print("Closing socket")
        print(f"Error Exception {e}")
        client.close()
        s.close()







##hostMACAddress = 'BC:14:EF:A3:39:3C'
##msg = "5" ##this is the message sent to the pi
##send_port = 5 ##bluetooth port computer comms to pi (CF data)
##receive_port = 6
##
##s_blue = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
##s_blue.bind((hostMACAddress, send_port))
##
###s_red = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
###s_red.connect((hostMACAddress, receive_port))
###s_red  = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
####backlog = 1
####size = 1024 ##size of the buffer
####s_red.listen(backlog)
##
##feature_vector = []
##for i in range(16):
##    feature = rand.randint(0,1000)
##    feature_vector.append(feature)
##try:
##    print("here")
##    s_send, address = s_blue.accept()
##    print("there")
##    # This can be any data:
##    s_send.send(bytes(msg, 'UTF-8'))
##    binary_vector = str(feature_vector) ##FEATURE VECTOR FROM CF
##    ## making the list into a string, encoding it and sending it to RM_socket
##    print("string made {}".format(binary_vector))
##    data = binary_vector.encode('utf-8')
##    s_send.sendall(data)
##    print("sent")
##    
####    s_receive, address = s_red.accept()
####    while 1:
####            data = s_receive.recv(size)
####            if data:
####                   print(f"data {data}")
####    
##
##except:
##    print("Closing socket")
##    s_send.close()
##    s_receive.close()
##    s_red.close()
##    s_blue.close()
