#!/usr/bin/python3

"""
This is for working with the trained neural network
removed setup and keylogger functions
this is meant for one file at a time to be processed
"""

import cv2
import glob
import os
import re
import sys
import socket
import time

"""
This is the pi communication code: It is working with bluetooth only.
"""

#hostMACAddress = 'BC:14:EF:A3:39:3C'
hostMACAddress = 'BC:14:EF:A3:BE:73'
port = 7
backlog = 1
size = 1024 ##size of the buffer


HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT_RECEIVE = 9082     # Port to listen on (non-privileged ports are > 1023)
#PORT_SEND    = 9083     # Port to listen on (non-privileged ports are > 1023)
DAEMON_NAME  = "CF_socket"

def setup_sockets():
   global s_receive, s_send

   s_receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   print("{} to bind to port {}".format(DAEMON_NAME, PORT_RECEIVE))
   s_receive.bind((HOST, PORT_RECEIVE))
   #s_send    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   setup_send_bluetooth()

def setup_send_bluetooth():
   global s_blue
   s_blue = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
   s_blue.bind((hostMACAddress, port))
   s_blue.listen(backlog)
   #b_send, address = s_blue.accept()
   print("Neural Bluetooth up")
##def setup_sendsocket():
##   global s_send
##   try:
##       print(f"Trying this socket out for {DAEMON_NAME}, {PORT_SEND}")       
##       s_send.connect((HOST, PORT_SEND))
##       print(f"{DAEMON_NAME} has successfully connected s_send")
##
##   except:
##       print(f"{DAEMON_NAME} is waiting to connect")
##       time.sleep(0.5)
##       setup_sendsocket()
       

##def connect_to_downstream_socket():
##  global s_send
##
##  if s_send != '': return
##  try:
##     s_send    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##     s_send.connect((HOST, PORT_SEND))
##  except:
##     print("Cannot connect to port {}. Quitting...".format(PORT_SEND))

def closesocket():
   global s_receive, b_send, s_blue
   if s_receive != '':
     s_receive.shutdown(socket.SHUT_RDWR)
     s_receive.close()
   if s_blue != '':
     s_blue.shutdown(socket.SHUT_RDWR)
     s_blue.close()
     
   print(f"Closed sockets {PORT_RECEIVE}")

global_rocket_x = 0

def consolidate_boxes_for_rocket(rocket_body_boxes, rocket_flame_white_boxes, rocket_flame_yellow_boxes):
   global global_rocket_x
   #print("consolidate_boxes_for_rocket():\n body: {}\n flame_white {}\n  flame_yellow {}\n\n".\
   #      format(rocket_body_boxes, rocket_flame_white_boxes, rocket_flame_yellow_boxes))
   
   
   rocket_body_data   = consolidate_subboxes_for_rocket(rocket_body_boxes)
   body_present_p     = len(rocket_body_data)
   rocket_white_data  = consolidate_subboxes_for_rocket(rocket_flame_white_boxes)
   white_present_p    = len(rocket_white_data)
   rocket_yellow_data = consolidate_subboxes_for_rocket(rocket_flame_yellow_boxes)
   yellow_present_p   = len(rocket_yellow_data)

   x_midpoint = y_midpoint = 0

   # by default we assume slope is 0 with respect to horizontal if we have only
   # one determination. However, there are probably conditions under which we
   # lose two of three components and the rocket may be in a characteristic slope then.
   # angle = arctan(); slope == 1 is angle of 45 degrees.
   # But let's try keeping raw slope and normalizing to between +1 and -1 for the NN
   # We'll have to see what the actual limits are; guessing +2 to -2. And we map onto
   # roughly +1000 to -1000 because our NN inputs are divided by 1000. So multiply by 1000
   slope = -1000.0

   #  We need these only if one of the 3 parts is present
   # x0 = x_left, x1 = x_right, y0 = y_left, y1 = y_right.
   if body_present_p and white_present_p and yellow_present_p:
        x_midpoint, y_midpoint, x0, x1, y0, y1 = rocket_white_data
        x_left,     y_left,     x0, x1, y0, y1 = rocket_yellow_data
        x_right,    y_right,    x0, x1, y0, y1 = rocket_body_data
        slope = 1000 * (y_right - y_left)/(x_right - x_left)   
        # print("x left {}, right {}. y left {}, right {}. Slope {}".format(x_left, x_right, y_left, y_right, slope))
   elif not body_present_p and white_present_p and yellow_present_p:
        x_midpoint, y_midpoint,  x0, x1, y0, y1 = rocket_white_data
        x_left,     y_left,      x0, x1, y0, y1 = rocket_yellow_data
        x_right = x_midpoint
        y_right = y_midpoint
        slope = 1000.0 * (y_right - y_left)/(x_right - x_left)   
        # print("x left {}, right {}. y left {}, right {}. Slope {}".format(x_left, x_right, y_left, y_right, slope))
   elif body_present_p and not white_present_p and yellow_present_p:
        x_right, y_right,  x0, x1, y0, y1       = rocket_body_data
        x_left , y_left,   x0, x1, y0, y1       = rocket_yellow_data
        x_midpoint = (x_left + x_right) / 2.0
        y_midpoint = (y_left + y_right) / 2.0
        slope = 1000.0 * (y_right - y_left)/(x_right - x_left)   
        # print("x left {}, right {}. y left {}, right {}. Delta X {}, Y {}. Slope {}".\
        #       format(x_left, x_right, y_left, y_right, x_right-x_left, y_right-y_left, slope))
   elif body_present_p and white_present_p and not yellow_present_p:
        x_right, y_right,  x0, x1, y0, y1       = rocket_body_data
        x_left,  y_left,   x0, x1, y0, y1       = rocket_white_data
        x_midpoint = (x_left + x_right) / 2.0
        y_midpoint = (y_left + y_right) / 2.0
        slope = 1000.0 * (y_right - y_left)/(x_right - x_left)   
        # print("x left {}, right {}. y left {}, right {}. Slope {}".format(x0, x1, y0, y1, slope))
   elif not body_present_p and not white_present_p and yellow_present_p:
        x_midpoint, y_midpoint, x0, x1, y0, y1 = rocket_yellow_data
        slope = 1000.0 * (y1 - y0)/(x1 - x0)
        # print("x left {}, right {}. y left {}, right {}. Delta X {}, Y {}. Slope {}".\
        #      format(x0, x1, y0, y1, x1-x0, y1-y0, slope))
   elif not body_present_p and white_present_p and not yellow_present_p:
        x_midpoint, y_midpoint, x0, x1, y0, y1         = rocket_white_data
        slope = 1000.0 * (y1 - y0)/(x1 - x0)
        # print("x left {}, right {}. y left {}, right {}. Delta X {}, Y {}. Slope {}".\
        #       format(x0, x1, y0, y1, x1-x0, y1-y0, slope))
   elif body_present_p and not white_present_p and not yellow_present_p:
        x_midpoint, y_midpoint, x0, x1, y0, y1         = rocket_body_data
        slope = 1000.0 * (y1 - y0)/(x1 - x0)
        # print("x left {}, right {}. y left {}, right {}. Slope {}".format(x0, x1, y0, y1, slope))

   this_feature = {}
   this_feature['rocket_height'] = y_midpoint
   this_feature['rocket_x']      = x_midpoint
   global_rocket_x               = x_midpoint
   this_feature['rocket_slope']  = slope
   # print("rocket: x {}, y {}, slope {}".format(x_midpoint, y_midpoint, slope))
   return this_feature
   
# we return the center of the enclosing box as well as its corners.
# For rockets, the left/right distinction (vs max/min) lets us figure out the slope
# But we still have to keep track of the max and min Y at each end because we don't know the
# slope of the rocket yet. We can try to figure it out by tracking the max/min Y on the left and the
# right. If the average value is higher on one side, we return the maximum value on that side and
# the minimum value on the other side. If the boxes are horizontal, this still works.
# returns
#   this_feature = [mid_point_x, mid_point_y, x_left, x_right, y_left, y_right]
def consolidate_subboxes_for_rocket(list_of_boxes):

   if len(list_of_boxes) == 0: return []

   x_left = y_left_min = y_left_max = x_right = y_right_min = y_right_max = 0

   for square in list_of_boxes:
      if x_left == 0:
        x_left, x_right, y_left, y_right = square
        y_left_min  = y_right_min = y_left    # each box has x0,y0 lower and x1,y1 higher
        y_left_max  = y_right_max = y_right
      else:
        x0, x1, y0, y1 = square
        if x0 < x_left:
            x_left                  = x0
            y_left_min = y_left_max = y0
        if x0 == x_left:
            y_left_min = min(y0, y1, y_left_min)
            y_left_max = max(y0, y1, y_left_max)
        if x1 > x_right:
            x_right = x1
            y_right_min = y_right_max = y1
        if x1 == x_right:
            y_right_min = min(y0, y1, y_right_min)
            y_right_max = max(y1, y0, y_right_max)

   if (y_right_max + y_right_min) > (y_left_max + y_left_min):
     # the right boxes are above the left boxes, so the item is tilted up (or down, since y=0 is at the top)
     # we will return the upper limit of the right box and the lower limit of the left box
     y_left  = min(y_left_max,  y_left_min)
     y_right = max(y_right_max, y_right_min)
     #print("1. y_left_min {}, y_left_max {} y_right_min {}, y_right_max {}: y_left {}, y_right {}".\
     #      format(y_left_min, y_left_max, y_right_min, y_right_max, y_left, y_right))
   else:
     # otherwise, the reverse. If the box(es) is/are horizontal, it doesn't matter as long as we choose
     # the opposite extrema
     y_left  = max(y_left_max,  y_left_min)
     y_right = min(y_right_max, y_right_min)
     #print("2. y_left_min {}, y_left_max {} y_right_min {}, y_right_max {}: y_left {}, y_right {}".\
     #      format(y_left_min, y_left_max, y_right_min, y_right_max, y_left, y_right))

   mid_point_x = (x_left + x_right) / 2.0
   mid_point_y = (y_left + y_right) / 2.0

   this_feature = [mid_point_x, mid_point_y, x_left, x_right, y_left, y_right]

   #print("list of boxes: {}".format(list_of_boxes))
   #print("  found: X left {}, X right {}, Y left {}, Y right {}\n".format(x_left, x_right, y_left, y_right))

   return this_feature

# we return the center of the enclosing box as well as its corners.  We have to track the min Y and max Y throughout,
# not just at the min X and max X.
# For barriers, the interesting datum is the top of the lower barrier and the bottom of the upper barrier and this will be
# determined at a higher level.   For imps and monsters, there should be only one box in the list.
# returns
#   this_feature = [mid_point_x, mid_point_y, x_left, x_right, y_left, y_right]
def consolidate_boxes_for_non_rocket(list_of_boxes):

   if len(list_of_boxes) == 0: return []

   x_min = x_max = y_min = y_max = 0

   for square in list_of_boxes:
      x0, x1, y0, y1 = square
      if x_min == 0:
        x_min  = x0
        x_max  = x1
        y_min  = y0    # each box has x0,y0 lower and x1,y1 higher
        y_max  = y1
      else:
        x_min = min(x0, x1, x_min)
        x_max = max(x0, x1, x_max)
        y_min = min(y0, y1, y_min)
        y_max = max(y0, y1, y_max)

   mid_point_x = (x_min + x_max) / 2.0
   mid_point_y = (y_min + y_max) / 2.0

   this_feature = [mid_point_x, mid_point_y, x_min, x_max, y_min, y_max]

   #print("list of boxes: {}".format(list_of_boxes))
   #print("  found: X left {}, X right {}, Y min {}, Y max {}\n".format(x_min, x_max, y_min, y_max))

   return this_feature

def process_feature_file(filename):
    global global_rocket_x

    these_boxes = {}  # object_type->x0, x1, y0, y1
    these_boxes['file_info'] = (0, 0, 0, filename)
    # data cleaning: we have to look for the object "monster 2" because p2 also matches but poorly!
    p1 = re.compile("(monster 2)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
    p2 = re.compile("([\w_]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
    for line in open(f"{filename}", "r"):
      if line == "": continue
      line = line[0:-1]
      #print("{}".format(line))
      m = p1.match(line)
      if not m:    # for the "monster 2" line
        m = p2.match(line)        
      if (m):
        object_name, x0, x1, y0, y1 = m.group(1,2,3,4,5)
        #print("{}: {}, {}, {}, {}".format(object_name, x0, x1, y0, y1))
        if object_name not in these_boxes:
          these_boxes[object_name] = []
        these_boxes[object_name].append([float(x0), float(x1), float(y0), float(y1)])

    # input: boxes, a dictionary of form file_index->these_boxes{}, where
    #               these_boxes holds object_name->list of boxes, each box defined as (x0, x1, yo, y1)
    #               and with the special feature 'file_info' with date,time,epoch,feature file name
    # output: features, a dictionary of form index->these_features{}, where
    #               these_features holds feature_name->x0, x1, y0, y1 where the coordinates describe
    #               and with the special feature 'file_info' with date,time,epoch,feature file name
    # a box that encloses all the identified boxes.
    #  Exception: a new feature, 'rocket_height', is an estimate of the y-coordinate of the center of the
    #             rocket. It replaces 'rocket_body', 'rocket_flame_white', and 'rocket_flame_yellow'
    #  Exception: a new feature, 'rocket_slope', is an estimate of the angle from horizontal of the rocket
    #  Exception: a new feature, 'rocket_x', is an estimate of the x position of the center of the rocket
    #             this is needed only to draw a line in the image for verification of the accuracy of the localization
    these_feature_data = {}
    these_feature_data['file_info'] = these_boxes['file_info']
    for object_name in these_boxes:
      if object_name == 'file_info': continue
      list_of_boxes = these_boxes[object_name]
      if object_name == 'rocket_body':
        #print("rocket body: {}".format(list_of_boxes))
        #if 'monster' in these_boxes or 'monster 1' in these_boxes or 'monster 2' in these_boxes:
        # Except some frames have the sails and not the monsters
        # jprScreen_0062.2020-11-06.17-06-13.1604703973.278438.png
        #   print("Found monster in image. Will look for false rocket body detection")
        list_of_boxes = filter_for_multiple_objects(list_of_boxes, 'rocket body')
        if len(list_of_boxes) > 1:
          print("Rocket body seems to have {} parts: looking for false positives".format(len(list_of_boxes)));
          # if segmentation found > 1 object, probably only one is real
          # the simplest approach is to choose the largest group reasoning that artifacts are smaller
          # however, this is not foolproof. So let's scan for vertical alignment, which is a false positive
          # if it's more than two in a column for rocket bodies.  This doesn't apply to barriers, of course.
          delete_list = []
          for i in range(len(list_of_boxes)):
            the_list = list_of_boxes[i]
            last_x0 = 0
            vertical_flag = 0
            for subbox in the_list:
              if last_x0 == 0: last_x0 = subbox[0]
              elif last_x0 == subbox[0]:
                vertical_flag = vertical_flag + 1   # count boxes with the same x0
            if vertical_flag == len(the_list) - 1:  # the first subbox was the comparitor
              # if all the boxes are lined up on top of each other, it's likely a false positive
              # print("Deleting vertical boxes {} from rocket_body".format(the_list))
              delete_list.append(i)
            # else:
            #   print("Found {} vertical boxes out of {} in the group.".format(vertical_flag,the_list))
          delete_list.sort(reverse=True)
          for i in delete_list:
              # print("Deleting group {} from list_of_boxes".format(i))
              del list_of_boxes[i]

        # assume there is one left. Since we scan every frame, we have to reduce the list every time
        list_of_boxes = list_of_boxes[0]

        rocket_body_boxes         = list_of_boxes
        #print("rocket body boxes: {}\n".format(rocket_body_boxes))

        rocket_flame_white_boxes = rocket_flame_yellow_boxes = []
        if 'rocket_flame_white' in these_boxes:
          rocket_flame_white_boxes = these_boxes['rocket_flame_white']
        if 'rocket_flame_yellow' in these_boxes:
          rocket_flame_yellow_boxes = these_boxes['rocket_flame_yellow']
        object_features = consolidate_boxes_for_rocket(rocket_body_boxes, rocket_flame_white_boxes, rocket_flame_yellow_boxes)
        these_feature_data['rocket_height'] = object_features['rocket_height']
        these_feature_data['rocket_x']      = object_features['rocket_x']
        global_rocket_x                     = object_features['rocket_x']
        these_feature_data['rocket_slope']  = object_features['rocket_slope']
      # we handle these together with rocket_body above
      elif (object_name == 'rocket_flame_white' or object_name == 'rocket_flame_yellow'): continue
      # sometimes more than one bird is in an image so we have to segregate them
      elif object_name == 'bird':
        bird_list_of_boxes = filter_for_multiple_objects(list_of_boxes, 'bird')
        counter = 0
        for bird_list in bird_list_of_boxes:
            object_features = consolidate_boxes_for_non_rocket(bird_list)
            these_feature_data["{}_{}".format(object_name,counter)] = object_features           
            counter = counter + 1
      # we have upper and lower barriers. Here is where we start to distinguish
      elif object_name == 'barrier':
        list_of_boxes = filter_for_barriers(list_of_boxes)
        counter = 0
        for barrier_list in list_of_boxes:
            object_features = consolidate_boxes_for_non_rocket(barrier_list)
            these_feature_data["{}_{}".format(object_name,counter)] = object_features           
            counter = counter + 1
      else:
          object_features = consolidate_boxes_for_non_rocket(list_of_boxes)
          these_feature_data[object_name] = object_features

    return these_feature_data

# filter the bird list_of_boxes to distinguish birds that are far apart in x and/or y
# we have to do clustering by checking each box against each other one. :-(
# return list of list of boxes, one for each bird
#   Turns out we have to do the same with rocket bodies and sail artifacts, and
# with barriers. See filter_for_barriers(list_of_boxes) below: it needs a different criterion.
def filter_for_multiple_objects(list_of_boxes, label):
  #print("filter for multiple objects: entering list_of_boxes\n{}".format(list_of_boxes))
  object_lists = []
  distance_threshold = 35
  for i in range(len(list_of_boxes)):
    x0 = list_of_boxes[i][0]
    x1 = list_of_boxes[i][1]
    y0 = list_of_boxes[i][2]
    y1 = list_of_boxes[i][3]
    # we scan through all the subboxes of all the object in object_lists
    # if we can match the current subbox with one, we add it to that object's list
    # otherwise we start a new object
    found_it = 0
    object_counter = 0
    for object in object_lists:
       #print("object {} : subboxes {}".format(object_counter, object))
       no_good  = 0
       for subbox in object:
         b_x0, b_x1, b_y0, b_y1 = subbox
         # this criterion is good for small objects but not for huge barriers
         if abs(x0 - b_x0) > distance_threshold or abs(y0 - b_y0) > distance_threshold:
           # print("object subbox {} at {}, {} is far from {} at {}, {}".\
           #      format(i, i_x0, i_y0, b_x0, b_y0))
           no_good = 1
           break;
       if not no_good:
         # looks like this box isn't far from any of the subboxes assigned to this object
         #print("Assigning subbox {} to object {}".format(i, object_counter))
         object_lists[object_counter].append( list_of_boxes[i] )
         found_it = 1
       object_counter = object_counter + 1
    if not found_it:
      # we couldn't assign this subbox to any of the existing objects
      object_lists.append( [ list_of_boxes[i] ])
  #print("filter_for_multiple_objects(): found {} {} objects".format(len(object_lists), label))
  return object_lists                                                             

# for barriers, false positives are not a big problem. We have to distinguish lower from upper.
# So we use a criterion in which a subbox is assigned to a group if it close to any, rather than
# to all, of the group's members.
def filter_for_barriers(list_of_boxes):
  #print("filter for barriers: entering list_of_boxes\n{}".format(list_of_boxes))
  object_lists = []
  distance_threshold = 100
  for i in range(len(list_of_boxes)):
    x0 = list_of_boxes[i][0]
    x1 = list_of_boxes[i][1]
    y0 = list_of_boxes[i][2]
    y1 = list_of_boxes[i][3]
    # we scan through all the subboxes of all the object in object_lists
    # if we can match the current subbox with one, we add it to that object's list
    # otherwise we start a new object
    found_it = 0
    object_counter = 0
    for object in object_lists:
       #print("object {} : subboxes {}".format(object_counter, object))
       no_good  = 1
       for subbox in object:
         b_x0, b_x1, b_y0, b_y1 = subbox
         # this criterion is good for the huge barriers
         if abs(x0 - b_x0) < distance_threshold and abs(y0 - b_y0) < distance_threshold:
           # print("object subbox {} at {}, {} is far from {} at {}, {}".\
           #      format(i, i_x0, i_y0, b_x0, b_y0))
           no_good = 0   # we found a close-enough subbox in the group, so quit looking
           break;
       if not no_good:
         # looks like this box is close to at least one of the subboxes assigned to this object
         #print("Assigning subbox {} to object {}".format(i, object_counter))
         object_lists[object_counter].append( list_of_boxes[i] )
         found_it = 1
       object_counter = object_counter + 1
    if not found_it:
      # we couldn't assign this subbox to any of the existing objects
      object_lists.append( [ list_of_boxes[i] ])
  #print("filter_for_barriers(): found {} objects".format(len(object_lists)))
  return object_lists                                                             


def write_feature_data_to_an_image(these_feature_data, image_file):
    # and write to image for quality check
    #print("these_feature_data: \n{}".format(these_feature_data['file_info']))
##    the_date, the_time, the_epoch, the_feature_filename = these_feature_data['file_info']
    # find the file
##    filepath = "screenshots/*{}*{}*{}*png".format(the_date, the_time, the_epoch)
    filepathname = f"screenshots/{image_file}"

    if not filepathname:
      print(f"Cannot find image file '{filepathname}'")
      return
    print(f"Reading image file {filepathname}")
    # read the image
    the_image = cv2.imread(filepathname, cv2.IMREAD_COLOR)
    for object in these_feature_data:
       if object == 'file_info':    continue
       if object == 'rocket_slope': continue
       if object == 'rocket_x':     continue
       if object == 'rocket_height':
          height = these_feature_data[object]
          x      = these_feature_data['rocket_x']
          slope  = these_feature_data['rocket_slope']   # slope is the raw slope * 1000
          min_x  = int(x - 30)
          w      = 60
          min_y  = int(height - slope * 30/1000.0)
          max_y  = int(height + slope * 30/1000.0)
          h      = max_y - min_y
       else:
          foo1, foo2, min_x, max_x, min_y, max_y = these_feature_data[object]
          # print("object {}: x0 {} x1 {}, y0 {} y1 {}".format(object,min_x, max_x, min_y, max_y))
          min_x = int(min_x)
          max_x = int(max_x)
          min_y = int(min_y)
          max_y = int(max_y)
          w     = max_x - min_x
          h     = max_y - min_y
       color_b = color_g = color_r = 255
       #print("image {}, min_x {}, min_y {}, w {}, h {}, color_b {}".\
       #      format(the_image, min_x, min_y, w, h, color_b))
       cv2.line(the_image, (min_x, min_y), (min_x + w, min_y + h), (color_b,color_g,color_r), 2)
    #cv2.imshow('the image',the_image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    cv2.imwrite(f"screenshots-with-features-identified/{image_file}.with-features.png",the_image)
    #fp_log.write("{}: pt {} w {} h {}\n".format(name, [min_x0, min_y0], w, h))

def write_feature_data_to_NN_file(these_feature_data, epoch, fp_nn, index):
    global global_rocket_x

    #print("these_feature_data: \n{}".format(these_feature_data['file_info']))

    # format of output file:
    # obs = (rocket_height, rocket_angle, velocity, enemy_1_distance, enemy_1_height, 
    #       enemy_2_distance, enemy_2_height, enemy_3_distance, enemy_3_height,
    #       enemy_4_distance, enemy_4_height, barrier_top_distance, barrier_top_height,
    #       barrier_bottom_distance, barrier_bottom_height)
    #print("CF: Inside Function")
    i = 0
    enum_rocket_height            = i        ; i = i + 1
    enum_rocket_slope             = i        ; i = i + 1
    enum_rocket_velocity_x        = i        ; i = i + 1    
    enum_rocket_velocity_y        = i        ; i = i + 1
    enum_enemy1_distance          = i        ; i = i + 1
    enum_enemy1_height            = i        ; i = i + 1
    enum_enemy2_distance          = i        ; i = i + 1
    enum_enemy2_height            = i        ; i = i + 1
    enum_enemy3_distance          = i        ; i = i + 1
    enum_enemy3_height            = i        ; i = i + 1
    enum_enemy4_distance          = i        ; i = i + 1
    enum_enemy4_height            = i        ; i = i + 1
    enum_barrier_top_distance     = i        ; i = i + 1
    enum_barrier_top_height       = i        ; i = i + 1
    enum_barrier_bottom_distance  = i        ; i = i + 1
    enum_barrier_bottom_height    = i        ; i = i + 1
    # set the distance to all threats to maximum distance (1000 px)
    feature_vector = [0, 0, 1500, 0, 1000, 0, 1000, 0, 1000, 0, 1000, 0, 1000, 0, 1000, 0 ] # 16 elements
    #print("CF: Reached inizialization of list")
    x_positives = [0,0,0,0,0,0]
    x_old       = [0,0,0,0,0,0]
    y_old       = 0
    enemy_counter = 0
    for object in these_feature_data:
       if   object == 'file_info':    continue
       elif object == 'rocket_slope': continue
       elif object == 'rocket_x':     continue
       elif object == 'rocket_height':
       
          height   = int(these_feature_data[object])
          x        = int(these_feature_data['rocket_x'])
          slope    = int(these_feature_data['rocket_slope'])   # slope is the raw slope * 1000
          feature_vector[enum_rocket_height]    = height
          feature_vector[enum_rocket_slope]     = slope
          
       # process barrier
       elif object[0:len('barrier')] == 'barrier':
          # print("object {}".format(object))
          # figure out whether this barrier is near the top or the bottom. Then choose the y-boundary
          # closer to the center of the field
          foo1, foo2, min_x, max_x, min_y, max_y = these_feature_data[object]
          if 'rocket_x' not in these_feature_data:
            rocket_x = global_rocket_x  # assume rocket is where it was last time
          else:
            rocket_x = these_feature_data['rocket_x']
          distance = int(min_x - rocket_x)
          if min_y < 450/2:    # half screen height so this object is in top half
            height   = int(max_y)
            feature_vector[enum_barrier_top_distance] = distance
            x_positives[4] = distance
            feature_vector[enum_barrier_top_height]   = height
          else:  # this object is in the bottom half
            height   = int(min_y)
            feature_vector[enum_barrier_bottom_distance] = distance
            x_positives[5] = distance
            feature_vector[enum_barrier_bottom_height]   = height
                            
       # process enemy. Flying enemies like birds and imps could have two lines in the AI, one for the
       # top of the object and one for the bottom. We could use also use one line at the mid-Y point and
       # let the AI figure out that it has to stay far away from that line. Let's do the second for now.
       # # braindamaged python doesn't have variable variables, doesn't have switch(), and can't do this:
       #command1 = "feature_vector[enum_enemy{}_distance] = distance".format(enemy_counter)
       #eval(command1)
       #command2 = "feature_vector[enum_enemy{}_height  ] = height".format(enemy_counter)
       #eval(command2)
       elif object[0:len('bird')] == 'bird' or object[0:len('monster')] == 'monster' or object == 'imp':
          foo1, foo2, min_x, max_x, min_y, max_y = these_feature_data[object]
          # print("object {}: x0 {} x1 {}, y0 {} y1 {}".format(object,min_x, max_x, min_y, max_y))
          if 'rocket_x' not in these_feature_data:
            rocket_x = global_rocket_x  # assume rocket is where it was last time
          else:
            rocket_x = these_feature_data['rocket_x']
          distance      = int(min_x - rocket_x)
          if object[0:len('monster')] == 'monster':
              height        = int(min_y)          # min_y is the "top" of the object. Monsters always are on surfaces
          else:
              height        = int((min_y + max_y)/2)
          enemy_counter = enemy_counter + 1       # we start with 1, not 0
          if enemy_counter == 1:
             feature_vector[enum_enemy1_distance] = distance
             x_positives[0] = distance
             feature_vector[enum_enemy1_height]   = height
          elif enemy_counter == 2:
             feature_vector[enum_enemy2_distance] = distance
             x_positives[1] = distance
             feature_vector[enum_enemy2_height]   = height
          elif enemy_counter == 3:
             feature_vector[enum_enemy3_distance] = distance
             x_positives[2] = distance
             feature_vector[enum_enemy3_height]   = height
          elif enemy_counter == 4:
             feature_vector[enum_enemy4_distance] = distance
             x_positives[3] = distance
             feature_vector[enum_enemy4_height]   = height
       else:
         print(f"writing to NN: Unknown object '{object}'")

       ## Getting x velocity as an input
       x_final = 0
       for vel_i in range(len(x_positives)):
          x_interm = abs(x_old[vel_i]- x_positives[vel_i])
          if x_interm > x_final:
             x_final = x_interm
       
       if x_final == 0:
          feature_vector[enum_rocket_velocity_x]   = 1500
       else:
          feature_vector[enum_rocket_velocity_x]   = x_final
       feature_count = 0   
       for x_vel in range(4, 14,2): ##saving old data to system   
          x_old[feature_count] = feature_vector[x_vel]
          feature_count += 1

       feature_vector[enum_rocket_velocity_y] = height - y_old
       y_old = height          
    # now print the 16-element vector for the NN (the 17-element format includes the index
    # number of the image, for cross reference. As we progress, we will probably want to also include
    # the run identifier and exclude both of them when reading into jlw_gym.
    
    # fp_nn.write("{}  {}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}: {}\n".\
    #print("CF: Finished For Loop")
    fp_nn.write("{} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}\n".\
          format(feature_vector[enum_rocket_height],           feature_vector[enum_rocket_slope], 
                 feature_vector[enum_rocket_velocity_x],       feature_vector[enum_rocket_velocity_y],
                 feature_vector[enum_enemy1_distance],         feature_vector[enum_enemy1_height], 
                 feature_vector[enum_enemy2_distance],         feature_vector[enum_enemy2_height], 
                 feature_vector[enum_enemy3_distance],         feature_vector[enum_enemy3_height], 
                 feature_vector[enum_enemy4_distance],         feature_vector[enum_enemy4_height], 
                 feature_vector[enum_barrier_top_distance],    feature_vector[enum_barrier_top_height], 
                 feature_vector[enum_barrier_bottom_distance], feature_vector[enum_barrier_bottom_height]
                 # , index
                 ))
    #print("CF: Wrote to file")
    global s_blue, b_send
    print("CF: Bluetooth Setup")

##    if s_send == '': connect_to_downstream_socket()    # this daemon ought to exist by now
##    binary_vector = str(feature_vector)
##    ## making the list into a string, encoding it and sending it to RM_socket
##    data = binary_vector.encode('utf-8')
##    s_send.sendall(data)
    try:
       print("CF: Inside Try-block")
       #b_send, address = s_blue.accept()
       #print("CF: After Accepting")       
       # This can be any data:
       binary_vector = ' '.join(map(str, feature_vector)) ##FEATURE VECTOR FROM CF
       print("CF: After making list")
       ## making the list into a string, encoding it and sending it to RM_socket
       data = binary_vector.encode('utf-8')
       b_send.sendall(data)
       print(f"{DAEMON_NAME}: {data.decode()} ")
       
    except:
       print("Closing Pi socket")
       s_send.close()
       s_blue.close()

    print("CF: If you reached here not problem")

############################################
#
#   MAIN SECTION
#
############################################

def main():
  global s_receive, b_send
  ##This is where the receive socket is to give the feature extraction input filenam
  feature_files = {}
  ##Becuase the regex allows for longer data strings than the file, if the data has been
  ## sent while this is cooking, it allows for combination of strints that reults in an error
  ## Breaking the file.

  ##Simple lazy fix is to take more time to load FE and screenshot while bluetooth is loading
  ## TODO make this never happen again.
  while True:
      s_receive.listen()
      conn, addr = s_receive.accept()
      print('Connected by CF ', addr)
      b_send, address = s_blue.accept()
      print("CF: Accepted Blue")
      while True:
          data = conn.recv(1024)
          if not data:
              break
          data = data.decode()
          print(f'{DAEMON_NAME}: Data {data} received from {PORT_RECEIVE}')
          feature_filename = data
          print("CF: Data is utilized")
            

  # uncomment this to write the jlw_observations.new.txt file.
  # Also the write_feature_data_to_NN_file() statement and the fp_nn.close() statement
          fp_nn = open("jlw_observations.new.txt", "w")

          p = re.compile('(jprScreen_\d+\.\d\d\d\d-\d\d-\d\d\.\d\d-\d\d-\d\d\.\d+\.\d+\.png)')
          image_name1 = p.search(feature_filename)
          image_name = image_name1.group(1)
          p1   = re.compile('jprScreen_(\d+).(\d\d\d\d-\d\d-\d\d).(\d\d-\d\d-\d\d).(\d+.\d+).png.feature-list.txt')
          name = feature_filename 
          m    = p1.search(name)
          if (m):
           index, date, time, epoch = m.group(1,2,3,4)
           feature_files[index] = (date, time, epoch, name)
           boxes = {}
           date, time, epoch, feature_filename = feature_files[index]
           #print("CF: Data Reached here seach")
           these_feature_data = process_feature_file(feature_filename)
           print("CF: Data Reached here process")
         # uncomment this to see the images with the annotations. These are also written to file
           #write_feature_data_to_an_image(these_feature_data, image_name)
         # uncomment this to write the jlw_instruction.new.txt file and the fp_nn open and .close() statements
           write_feature_data_to_NN_file(these_feature_data, epoch, fp_nn, index)
           print("CF: Data Reached here write")
          else:
           print("no match")
         # uncomment this to write the jlw_instruction.new.txt file
         # Also the write_feature_data_to_NN_file() statement and the fp_nn = open() statement
##          if s_send == '': connect_to_downstream_socket()    # this daemon ought to exist by now
##
##          feature_vector = [0, 0, 1000, 0, 1000, 0, 1000, 0, 1000, 0, 1000, 0, 1000, 0 ]
##          binary_vector = str(feature_vector)
##         ## making the list into a string, encoding it and sending it to RM_socket
##          data = binary_vector.encode()
##          s_send.sendall(data)
##          print(f"{DAEMON_NAME} sent data {data.decode()} to RM_socket ")

          fp_nn.close()    
try:
  setup_sockets()
  main()
finally:
  closesocket()
