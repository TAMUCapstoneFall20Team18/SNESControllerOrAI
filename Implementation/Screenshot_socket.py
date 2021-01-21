#!/usr/bin/python3

"""
MUST BE AT STANDARD SCREEN HEIGHT, ALREADY LOADED WITH JPR
    MUST BE IN FRONT OF SCREEN
    
"""

import pyautogui
import time
import socket

"""
SOCKET 1

"""
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT_SEND    = 9081     # Port to listen on (non-privileged ports are > 1023)
DAEMON_NAME  = "Screenshot"

def setup_sockets():
   global s_send
   try:
     s_send    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     s_send.connect((HOST, PORT_SEND))
     print(f"{DAEMON_NAME} has successfully connected s_send")
   except:
     s_send   = ''

   print("Set up daemon {}".format(DAEMON_NAME))

def connect_to_downstream_socket():
  global s_send

  if s_send != '': return

  try:
     s_send    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     s_send.connect((HOST, PORT_SEND))
  except:
     print("Cannot connect to port {}. Quitting...".format(PORT_SEND))
  


# take a screenshot every N interval and sleep between times.
# gotta find a way to terminate and, even better, to turn  screen capture
# on and off from the keyboard. There are ways to do non-blocking keyboard
# reads (eg
# https://stackoverflow.com/questions/2408560/python-nonblocking-console-input
# but they are complicated. We can just use Control C here, or an interrupt
# handler (so we can do "kill -HUP <process ID>" to tell this process to toggle
# screen capture. Or, we can create a GUI with a button.  Or, we can use Control C!!
def start_screenshot_function(left, top, width, height):
##  sleep_interval = 0.3  # seconds when program is fast enough
  sleep_interval = 3
  print("Starting screenshot at intervals of {} seconds".format(sleep_interval))
  while (1):
    screenshot_function(left, top, width, height)
    time.sleep (sleep_interval)

counter = 0
   
def screenshot_function(left, top, width, height):
   global counter
# take a screenshot of the screen and store it in memory, then
# convert the PIL/Pillow image to an OpenCV compatible NumPy array
# and finally write the image to disk
##    image = pyautogui.screenshot()
##    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
##    cv2.imwrite("Test_" + str(counter) +".png", image)
##
   #print(f"{left}, {top}, {width}, {height}")
   #print("{}, {}, {}, {}".format(left, top, width, height))
   # capture screen and write to disk:
   # im = pyautogui.screenshot(("jprScreen"+ str(time.asctime()) +".png"), region=(left, top, width, height)) ##so this changes automaticly, but no
   # capture the entire screen. We'll clip out what we want later
   # im = pyautogui.screenshot("jprScreen_{}.png".format(counter))
   # let's preposition JPR and used fixed coordinates for screen capture
   epoch_time   = time.time()      # returns epoch time with microsecond resolution
   local_time   = time.localtime(epoch_time)
   datetime_str = time.strftime("%Y-%m-%d.%H-%M-%S", local_time);  # defaults to current localtime()
   str          = "{:04d}".format(counter)   # make numbers with leading zeros
   data         = f'screenshots/jprScreen_{str}.{datetime_str}.{epoch_time}.png'
   im           = pyautogui.screenshot(data, region = (left, top, width, height))
   counter      = counter + 1

   global s_send

   if s_send == '': connect_to_downstream_socket()# this daemon ought to exist by now
   print(f'{DAEMON_NAME} sending {data} to FE_Socket')
   data   = data.encode('utf-8')
   s_send.sendall(data)
##   time.sleep(2)
##   reply  = s_send.recv(1024)
##   print(" .. {} got the following: {}".format(DAEMON_NAME, reply.decode()))
    
def main():
    time.sleep(1.5) ##gives time for the user to click on the JPR window from entering command
    try:
        print("Trying to find JPR window...")
        filename        = "StartingScreen1.png"
        screen_location = pyautogui.locateOnScreen(filename, grayscale = False, confidence=0.9)
        # from https://stackoverflow.com/questions/23086383/how-to-test-nonetype-in-python
        if screen_location is not None:
          screen_left   = screen_location.left
          screen_top    = screen_location.top
          screen_width  = screen_location.width
          screen_height = screen_location.height
          print(str(screen_location))
          
          start_screenshot_function(screen_left, screen_top, screen_width, screen_height)
      
        else:
          print("Could not locate window based on image '{}'".format(filename))
          filename         = "JPR_Header1.png"
          screen_location1 = pyautogui.locateOnScreen(filename, grayscale = False)
          if screen_location1 is not None:
            screen_left1   = screen_location1.left
            screen_top1    = screen_location1.top
            screen_width1  = screen_location1.width
            screen_height1 = screen_location1.height + 500
            print(str(screen_location1))
            start_screenshot_function(screen_left1, screen_top1, screen_width1, screen_height1)
          else:
            print("Could not locate window based on image '{}'".format(filename))

    except AttributeError:
        print("Attempting backup image")
        
        try: 
            screen_location1 = pyautogui.locateOnScreen("jpr_alt_header.png", grayscale = True)
            screen_left1   = screen_location1.left
            screen_top1    = screen_location1.top
            screen_width1  = screen_location1.width
            screen_height1 = screen_location1.height + 500
            print(str(screen_location1))
            screenshot_function(screen_left1, screen_top1, screen_width1, screen_height1)
            
        except AttributeError:
            print("Error: Backup failed")
        
    except Exception as e:
        # print("Error: " + e)
        print("Error: {}".format(type(e)))
        print("       {}".format(e.args))
        print("       {}".format(e))
  
   
setup_sockets()
main()
##finally:
##    closesocket()
        


