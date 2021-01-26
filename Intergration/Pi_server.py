###########################
##FOR CF_SOCKET sending data
###########################
hostMACAddress = 'BC:14:EF:A3:39:3C'
msg = "5" ##this is the message sent to the pi
send_port = 5 ##bluetooth port computer comms to pi (CF data)
backlog = 1
size = 1024 ##size of the buffer
s_blue = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s_blue.bind((hostMACAddress, send_port))
s_blue.listen(backlog)
try: 
	s_send, address = s_blue.accept()
	# This can be any data:
	s_send.send(bytes(msg, 'UTF-8'))
        binary_vector = str(feature_vector) ##FEATURE VECTOR FROM CF
        ## making the list into a string, encoding it and sending it to RM_socket
        data = binary_vector.encode('utf-8')
        s_send.sendall(data)
	
except:
	print("Closing socket")
	s_send.close()
	s_blue.close()
	
#######################
##FOR RM_SOCKET to PIPE
######################
hostMACAddress = 'BC:14:EF:A3:39:3C'
msg = "5" ##this is the message sent to the pi
send_port = 6 ##bluetooth port pi to computer
backlog = 1
size = 1024 ##size of the buffer
s_blue = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s_blue.bind((hostMACAddress, send_port))
s_blue.listen(backlog)
try:
	s_receive, address = s_blue.accept()
	# This can be any data:
	s_receive.sendall(bytes(prediction_index, 'UTF-8')) 
    ## making the list into a string, encoding it and sending it to RM_socket

	
except:
	print("Closing socket")
	s_receive.close()
	s_blue.close()

########################	
##FOR Pipe recieving data
########################

hostMACAddress = 'BC:14:EF:A3:39:3C'
recieve_port = 6 ##bluetooth for RM socket
backlog = 1
size = 1024 ##size of the buffer
s_blue = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s_blue.bind((hostMACAddress, recieve_port))
s_blue.listen(backlog)
try: 
        s_receive, address = s_blue.accept()
        while 1:
                data = s_receive.recv(size)
                if data:
                        keypress = data
except:
        print("Closing socket")
        s_receive.close()
        s_blue.close()

##FOR INPUT CONTROL
        if buttonStart.is_pressed:
	    break
	if buttonA.is_pressed:
	    text = "a"
	else:
            text = ""
        s.send(bytes(text, 'UTF-8'))
	# This recv may need to be moved elsewhere
	#response = s.recv(1024)
	#print(response)
##	if buttonB.is_pressed:
##		text = "B Pressed"
##	else:
##		text = "B Released"
##	s.send(bytes(text, 'UTF-8'))
	if buttonAI.is_pressed:
		text = "1"
	else:
		text = "2"
	s.send(bytes(text, 'UTF-8'))
	#sleep(1)#may be necessary, but only for testing
