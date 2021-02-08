"""
JLW Running code
THIS IS ON THE NANO
DATA IN: PI FROM LAPTOP
DATA OUT: PI TO LAPTOP
##HAVE THE PI TRANSMIT SCRIPT be the control for whose data is transmitted
## if the switch is on, and the slowdown has not already been transitted (have a flag)
## which will release the pipe to just pipe and edit keypresses
"""

import jlw_main as jlw
import re
from tensorflow.keras.models import load_model
import socket
from gpiozero import Button
from time import sleep

def main():
# Put receiving here
##    global s_receive, s_send
##
##    while True:
##        s_receive.listen()
##        conn, addr = s_receive.accept()
##        print('Connected by RM', addr)
##        model = load_model('jlw_model_saved') ## loads pretrained model this semester
##        while True:
##            data = conn.recv(1024)
##            if not data:
##                break
##            data = data.decode()
##            data = eval(data)
##            print(f"RM_Socket Data {data}")
##        
##            if data:
##                x_input = [int(i) for i in data]
####                print(x_input)

	AISwitch = Button(13)
	buttonA = Button(19)
	isAIOn = False

##Data is from CF received by PI may need sockets for the transfer by socket again
	hostMACAddress = 'BC:14:EF:A3:39:3C'
	send_port = 5 ##bluetooth port pi to computer
	backlog = 1
	size = 1024 ##size of the buffer
	
	try:
		print("Initialized")
		s_blue = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
		s_blue.bind((hostMACAddress, send_port))
		s_blue.listen(backlog)
		s_send, address = s_blue.accept()

		model = load_model('jlw_model_saved')

		while True:
		
			## Check for AI button press to switch modes
			if AISwitch.is_pressed:
				isAIOn = ~isAIOn
				print("Mode switched")
				if isAION:
					AImsg = "On"
				else:
					AImsg = "Off"
				print(AImsg)
				s_send.sendall(bytes(msg, 'UTF-8'))
				sleep(1)
		
			##Receive data from emulator, if any is present	
			while True:
				data = s_send.recv(size)
				if not data:
					break
				data = data.decode()
				data = eval(data)
				print(f"RM_Socket Data {data}")
				## prediction       = model.predict([data]) 
				## prediction_index = jlw.find_index_of_max_element(prediction[0])
				prediction_index = 4

			##When AI mode is active send prediction index
			if isAION:
				s_send.sendall(bytes(prediction_index, 'UTF-8'))
				sleep(1)
			else:
				if buttonA.is_pressed:
					text = "a"
				else:
					text = ""
				s_send.sendall(bytes(text, 'UTF-8'))
				sleep(1)

	except:
		print("Closing socket")
		s_send.close()
		s_blue.close()
#PUTS PREDITION NUMBER INTO THE PI AND SENT TO THE PIPE


##NN transmists houw many times pressed
##            if s_send == '': connect_to_downstream_socket()    # this daemon ought to exist by now
##            data = str(prediction_index)
##            data = data.encode()
##            s_send.sendall(data)
##            print(f"RM_socket sending data {data.decode()} to Pipe_socket ")
##            time.sleep(0.1)



#try:
#    setup_sockets()
main()
#finally:
#   closesocket()#
