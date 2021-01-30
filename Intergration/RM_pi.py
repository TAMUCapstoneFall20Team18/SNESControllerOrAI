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


   ##Data is from CF received by PI may need sockets for the transfer by socket again
   hostMACAddress = 'BC:14:EF:A3:39:3C'
   send_port = 6 ##bluetooth port pi to computer
   backlog = 1
   size = 1024 ##size of the buffer
   s_blue = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
   s_blue.bind((hostMACAddress, send_port))
   s_blue.listen(backlog)
  
   model = load_model('jlw_model_saved')
   prediction       = model.predict([data]) 
   prediction_index = jlw.find_index_of_max_element(prediction[0])

   try:
           s_send, address = s_blue.accept()
           # This can be any data:
           s_send.sendall(bytes(prediction_index, 'UTF-8')) 
       ## making the list into a string, encoding it and sending it to RM_socket

           
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
