"""
JLW Running code

Assuming trained model

Run input from CF_socket to NN

Get output from NN

Submit output to pipe to emulator

"""

import jlw_main as jlw
import re
from tensorflow.keras.models import load_model
import socket
import time

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT_RECEIVE = 9083     # Port to listen on (non-privileged ports are > 1023)
PORT_SEND    = 9084     # Port to listen on (non-privileged ports are > 1023)
DAEMON_NAME  = "RM_socket"

def setup_sockets():
   global s_receive, s_send ## setting up receive socket so the Consolidate Features can connect

   s_receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   print("{} to bind to port {}".format(DAEMON_NAME, PORT_RECEIVE))
   s_receive.bind((HOST, PORT_RECEIVE))
   s_send    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   setup_sendsocket()

def setup_sendsocket():
   global s_send ## This is the loop to connect without giving broken pipe error
   try:
       print(f"Trying this socket out for {DAEMON_NAME}, {PORT_SEND}")       
       s_send.connect((HOST, PORT_SEND))
       print(f"{DAEMON_NAME} has successfully connected s_send")

   except:
       print(f"{DAEMON_NAME} is waiting to connect")
       time.sleep(0.5)
       setup_sendsocket() ##Recursive

def connect_to_downstream_socket():
  global s_send

  if s_send != '': return

  try:
     s_send    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     s_send.connect((HOST, PORT_SEND))
  except:
     print("Cannot connect to port {}. Quitting...".format(PORT_SEND))

def closesocket(): ## Closes socket as a last ditch effort
   global s_receive, s_send
   if s_receive != '':
     s_receive.shutdown(socket.SHUT_RDWR)
     s_receive.close()
   print(f"Closed sockets {PORT_RECEIVE}")
  

##generates prediction
def main():
    # Put receiving here
    global s_receive, s_send

    while True:
        s_receive.listen()
        conn, addr = s_receive.accept()
        print('Connected by RM', addr)
        model = load_model('jlw_model_saved') ## loads pretrained model this semester
        while True:
            data = conn.recv(1024)
            if not data:
                break
            data = data.decode()
            data = eval(data)
            print(f"RM_Socket Data {data}")
        
            if data:
                x_input = [int(i) for i in data]
##                print(x_input)

            prediction       = model.predict([data]) 
            prediction_index = jlw.find_index_of_max_element(prediction[0])

            ##NN transmists houw many times pressed
            if s_send == '': connect_to_downstream_socket()    # this daemon ought to exist by now
            data = str(prediction_index)
            data = data.encode()
            s_send.sendall(data)
            print(f"RM_socket sending data {data.decode()} to Pipe_socket ")
            time.sleep(0.1)



try:
    setup_sockets()
    main()
finally:
    closesocket()
