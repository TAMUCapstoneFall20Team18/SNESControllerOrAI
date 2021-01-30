"""
This is the key pressing file, hopefully this one will be eaiser to implement

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

    
