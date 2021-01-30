import socket
from gpiozero import Button
from time import sleep

buttonUp = Button(22)
buttonDown = Button(27)
ButtonLeft = Button(4)
ButtonRight = Button(17)
buttonA = Button(19)
buttonB = Button(26)
buttonStart = Button(5)
buttonSelect = Button(6)
buttonAI = Button(13)

serverMACAddress = '54:13:79:6D:CE:B6'
port = 5
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s.connect((serverMACAddress,port))
while 1:
	if buttonStart.is_pressed:
		break
	if buttonA.is_pressed:
		text = "A Pressed"
	else:
		text = "A Released"
	s.send(bytes(text, 'UTF-8'))
	# This recv may need to be moved elsewhere
	response = s.recv(1024)
	print(response)
	if buttonB.is_pressed:
		text = "B Pressed"
	else:
		text = "B Released"
	s.send(bytes(text, 'UTF-8'))
	if buttonAI.is_pressed:
		text = "AI On"
	else:
		text = "AI Off"
	s.send(bytes(text, 'UTF-8'))
	sleep(1)
s.close()
