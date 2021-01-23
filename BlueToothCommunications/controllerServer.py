import socket

hostMACAddress = '54:13:79:6D:CE:B6'
msg = "5"
port = 5
backlog = 1
size = 1024
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s.bind((hostMACAddress, port))
s.listen(backlog)
try:
	client, address = s.accept()
	while 1:
		data = client.recv(size)
		if data:
			print(data)
			# This can be any data:
			client.send(bytes(msg, 'UTF-8'))
except:
	print("Closing socket")
	client.close()
	s.close()
