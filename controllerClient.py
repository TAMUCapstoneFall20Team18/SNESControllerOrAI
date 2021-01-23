import socket
from gpiozero import Button
from time import sleep

buttonA = Button(19)
buttonB = Button(26)
buttonStart = Button(5)

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
	response = s.recv(1024)
	print(response)
	if buttonB.is_pressed:
		text = "B Pressed"
	else:
		text = "B Released"
	s.send(bytes(text, 'UTF-8'))
	sleep(1)
s.close()
