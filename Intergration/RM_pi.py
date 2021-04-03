"""
JLW Running code
THIS IS ON THE NANO
DATA IN: PI FROM LAPTOP
DATA OUT: PI TO LAPTOP
##HAVE THE PI TRANSMIT SCRIPT be the control for whose data is transmitted
## if the switch is on, and the slowdown has not already been transitted (have a flag)
## which will release the pipe to just pipe and edit keypresses
"""

import usb.core
import jlw_main as jlw
import re
from tensorflow.keras.models import load_model
import socket
from gpiozero import Button
from time import sleep

def main():

	##AISwitch = Button(13)
	##buttonA = Button(19)
	##buttonStart = Button(5)
	isAIOn = False
	indexSent = True

##Data is from CF received by PI may need sockets for the transfer by socket again
	##hostMACAddress = '54:13:79:6D:CE:B6'
	hostMACAddress = 'BC:14:EF:A3:BE:73'
	emulator_port = 8 ##bluetooth port pi to computer
	neural_access_port = 7
	
	backlog = 3
	size = 1024 ##size of the buffer
	
	dev=usb.core.find(idVendor=0x0079,idProduct=0x0006)
	ep=dev[0].interfaces()[0].endpoints()[0]
	i=dev[0].interfaces()[0].bInterfaceNumber
	dev.reset()

	if dev.is_kernel_driver_active(i):
		dev.detach_kernel_driver(i)
	
	dev.set_configuration(1)
	eaddr=ep.bEndpointAddress
	
	s_emulator = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
	##s_blue.bind((hostMACAddress, send_port))
	##s_blue.listen(backlog)
	s_emulator.connect((hostMACAddress,emulator_port))
	
	s_neural = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
	s_neural.connect((hostMACAddress,neural_access_port))
	s_neural.setblocking(0)
	##s_send, address = s_blue.accept()

	model = load_model('jlw_model_saved')

	while True:
		buttonArray=dev.read(eaddr,8,1000)
		buttonData = buttonArray[5]
		if buttonData == 79:
			break
			
		## Check for AI button press to switch modes
		if buttonData == 47 or buttonData == 63:
			isAIOn = ~isAIOn
			if isAIOn:
				AImsg = "t"
			else:
				AImsg = "f"
			s_emulator.sendall(bytes(AImsg, 'UTF-8'))
			sleep(1)
		
		##Receive data from emulator, if any is present	
		while True:
			try:
				data = s_neural.recv(size)
			except:
				break
			data = data.decode()
			data = list(data.split(" "))
			for item in range(len(data)):
				data[item] = float(data[item])
			prediction       = model.predict([data]) 
			prediction_index = jlw.find_index_of_max_element(prediction[0])
			indexSent = False

		##When AI mode is active send prediction index
		if isAIOn:
			if not indexSent:
				s_emulator.sendall(bytes(str(prediction_index), 'UTF-8'))
				indexSent = True
		else:
			if buttonData == 31:
				text = "a"
			else:
				text = ""
			try:
				s_emulator.sendall(bytes(text, 'UTF-8'))
			except Exception as e:
				print(f"Error: {e}")
			sleep(0.02)

	s_emulator.close()
	s_neural.close()

#try:
#    setup_sockets()
main()
#finally:
#   closesocket()#
