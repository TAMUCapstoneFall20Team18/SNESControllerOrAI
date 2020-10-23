"""
This is the key pressing file, hopefully this one will be eaiser to implement
than the screenshot one.

      Switch statements are faster than if else statements, where speed may be
      key.
      decided that delay can be implemented later.
      Will need delay controlled by AI as an input for CC or JPR
      
Necessary output Key Translation Number

Up = Key.up = 1
Down = Key.down = 2
Left = Key.left = 3
Right = Key.right = 4

A = 'a' =  5
B = 'b' =  6
X = 'x' =  7
Y = 'y' =  8

L trigger = 'l'  = 9
R trigger = 'r'  = 10

Start = Key.space = 11      
Select =  Key.enter = 12

TODO
   See if Higan allows for manual input  -- should, but need to prove.
      -ACTION NEEDED: Call Simon Next Week to get command line tips and test
         SNES controller. 
   have a user delay for pressing. Will have to change depending
      on NN processing
"""

import time ##to input delays into key presses if necessary
from pynput.keyboard import Key, Controller
keyboard = Controller()


#testing info

##keyboard.press('a')
##time.sleep(0)
##keyboard.release('a')

##class KeyPress:  ##class to have switch

try:
    ##make sure to have an option for delay later DK is first game so ok
##    def switch(self, ai_output, delay = 0): ##initailize default case
##        default = "No Op"
##        return getattr(self, 'case_' + str(ai_output), lambda: default) ()
    def switch(case):
        return {
            1: case_1,
            2: case_2,
            3: case_3,
            4: case_4,
            5: case_5,
            6: case_6,
            7: case_7,
            8: case_8,
            9: case_9,
            10: case_10,
            11: case_11,
            12: case_12,
            }.get(case, f_default)

    def f_default(delay):
        return None

    def case_1(delay): ##Up
        keyboard.press(Key.up)
        time.sleep(delay)
        keyboard.release(Key.up)
        

    def case_2(delay): ##Down
        keyboard.press(Key.down)
        time.sleep(delay)
        keyboard.release(Key.down)
        
    def case_3(delay): #Left
        keyboard.press(Key.left)
        time.sleep(delay)
        keyboard.release(Key.left)

    def case_4(delay): #Right
        keyboard.press(Key.right)
        time.sleep(delay)
        keyboard.release(Key.right)

    def case_5(delay): ##A
        keyboard.press('a')
        time.sleep(delay)
        keyboard.release('a')

    def case_6(delay): ##B
        keyboard.press('b')
        time.sleep(delay)
        keyboard.release('b')
        
    def case_7(delay): #X
        keyboard.press('x')
        time.sleep(delay)
        keyboard.release('x')

    def case_8(delay): #Y
        keyboard.press('y')
        time.sleep(delay)
        keyboard.release('y')

    def case_9(delay): ##L
        keyboard.press('l')
        time.sleep(delay)
        keyboard.release('l')

    def case_10(delay): ##R
        keyboard.press('r')
        time.sleep(delay)
        keyboard.release('r')
        
    def case_11(delay): #select (space)
        keyboard.press(Key.space)
        time.sleep(delay)
        keyboard.release(Key.space)

    def case_12(delay): #start (enter)
        keyboard.press(Key.enter)
        time.sleep(delay)
        keyboard.release(Key.enter)

except:
    print(e)
        
    

