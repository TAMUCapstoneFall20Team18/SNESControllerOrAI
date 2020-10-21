##Widman_First_Shot at screencapture
'''
TODO
For this file:
   -Change variables to turn on photos
   -Change photo path --
       -Somehow get it to ask where once, and then run the shots.
   -Make a trigger, delay timer, and timer between shots
   -Make a def to take multiple pictures per second (100 ms?)

To other files:
    -Crop pictures of full screen to emulator
    -Have a key presser function
    -Have a output function utilizing the key presser and RNN output

    After this the input and output are set, just need
        -Labeling of images automaticly (start with JPR or CC)
        -RNN creation and training
'''

import datetime
import autopy
from pynput.keyboard import Key, Listener




exit_combination = {Key.ctrl_l, Key.print_screen} ##Edit to have a press set
currently_pressed = set()

##path="//home//widman//Training_Data//"+ get_filepath() +"//"+"str(datetime.date.today()"
##Change location to reflect the game bc otherwise 60 pictures is enough to sort with
     
def get_filepath():
    fileString = input("Where to store screenshots? ")
    return fileString


## Change filepath and naming scheme

with Listener(on_press=on_press,on_release=on_release) as listener:

	listener.join()

##Keylogger function

def on_press(key):
    check_key(key)
    if key in exit_combination:
        currently_pressed.add(key)
        if currently_pressed == exit_combination:
            listener.stop()
def on_release(key):  
    try:
        currently_pressed.remove(key)
    except KeyError:
        pass

####Required by keylogger
##
####Check input
##
def check_key(key):
    if key == Key.print_screen:
        shot = autopy.bitmap.capture_screen()
        now = datetime.datetime.now()
        timenow = now.strftime("%H_%M_%S")
        screenshot = open('//home//widman//Training_Data//'+get_filepath+'//'+ str(datetie.date.today(), 'x')
##      Need to get file saving correctly.
        shot.save(path+'//'+timenow+'.png')
        except FileNotFoundError:  
            os.makedirs(path)
            shot.save(path+'//'+timenow+'.png')



##Run again (Y/N), new file line?
