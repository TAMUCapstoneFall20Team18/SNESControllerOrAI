#!/usr/bin/python3

import cv2
import glob
import os
import re
import sys



# setup()
#   reads the specified keylog and directory of screen capture images
#   returns keylog_entries (list of epoch times of presses of the 'a' key)
#           feature_files  (dictionary of feature files, index->(date, time, epochtime of screen capture))
# print("feature file index {}: {} {}, epoch {}".format(index, date, time, epoch, filename))
def setup(keylog_filename, feature_dirpathname):

  # read the keylog
  # keytime 2020-11-06.17-05-44 (1604703944.493658), systemtime2020-11-06.17-05-44 (1604703944.4938269):30:a
  keylog_entries = []
  p1 = re.compile('^(\d+.\d{6}) (\d\d)')
  p2 = re.compile('^(\d+.\d+) (\d\d)')
  counter = 0
  for line in open(keylog_filename, 'r'):
    line = line[0:-1]
    # print("line {:03d}: {}".format(counter,line))
    counter = counter + 1
    if (line != ''):
      m = p1.match(line)
##      print(f"match is {m}")
      if not m:
       m = p2.match(line)
       print(f"match 2 is {m}")
      if (m):
        key_time,key_character = m.group(1,2)
        #print(f"time {key_time}, key character {key_character}")
        # print("key {} pressed at {} {} (epoch {}) system time. Delta before system time: {:.3f} msec\n".format(key_character, key_date, key_time, key_epoch, delta))
        #if (key_character != 35): continue
        # print("key {} pressed at {} {} (epoch {}) system time. Delta before system time: {:.3f} msec".format(key_character, key_date, key_time, key_epoch, delta))
        # store the epoch time of the 'a' keypress.  If we have multiple keys, we'd have to use a dictionary
        #print(f"appended key_time press {key_time}")
        keylog_entries.append(key_time)
    else:
      print(f"line empty {counter}")
  # read the list of files that pertain to the session in the specified keylog
  # jprScreen_0135.2020-11-06.15-49-17.1604699357.8424392.png.feature-list.txt
  feature_files = {}
  p = re.compile('jprScreen_(\d+).(\d\d\d\d-\d\d-\d\d).(\d\d-\d\d-\d\d).(\d+.\d+).png.feature-list.txt')
  for entry in os.scandir(feature_dirpathname):
    name = entry.name
    m = p.match(name)
    if (m):
      index, date, time, epoch = m.group(1,2,3,4) 
      feature_files[index] = (date, time, epoch, name) #what is inside feature files
      #print(f"picture epoch time {epoch}")
  
  sorted_dict = dict(sorted(feature_files.items(), key=lambda item: item[0]))  #only way to sort the dictionary
  feature_files = sorted_dict

  return keylog_entries, feature_files

# returns dictionary of epoch_time_of_image_file->
#    ( keypresses after this time until the next image file,
#      interval in sec to the next image file )
def compute_keypresses_following_each_image(keylog_entries, feature_files):

  if len(feature_files) == 0:
    print("The features_files list is empty")
    return {}
  keypresses_since_this_image = {}
  last_image_epoch_time = 0
  first_image_epoch_time = 0
  for index in feature_files:
    this_date, this_time, this_epoch_time, filename = feature_files[index]
    if last_image_epoch_time == 0:
      # this image is the first one so there are no prior keypresses
      last_image_epoch_time = this_epoch_time
      first_image_epoch_time = this_epoch_time
    else:
      # count the keypresses from the last image to this one
      count = 0
      # in some samples, there are epoch times earlier than the first one but with consistent index numbers
      # let's ignore these until we can figure out how this can happen
      if this_epoch_time < first_image_epoch_time:
        print("WARNING: screenshot index {} has time {} {} ({}), which is earlier than that of the first screenshot.\n  Filename: {}".\
              format(index, this_date, this_time, this_epoch_time, filename))
        continue
      for entry in keylog_entries:
        if entry >= last_image_epoch_time and entry < this_epoch_time: ##calc keypresses
           count = count + 1
      interval = float(this_epoch_time) - float(last_image_epoch_time)
      keypresses_since_this_image[ last_image_epoch_time ] = (count, interval)
      last_image_epoch_time = this_epoch_time
  # this is the last image
  count = 0
  for entry in keylog_entries:
    if entry >= this_epoch_time:
       count = count + 1
  interval = float(this_epoch_time) - float(last_image_epoch_time)  
  keypresses_since_this_image[ last_image_epoch_time ] = (count, interval)
  return keypresses_since_this_image

def show_and_write_keypresses_data(keypresses_since_this_image, feature_files): #see if it worked function
  last_epoch_time = 0
  for index in feature_files:
    date, time, epoch, filename = feature_files[index]
    if epoch not in keypresses_since_this_image:
      print("skipping too-early epoch {}".format(epoch))
      continue
    keypresses, interval        = keypresses_since_this_image[epoch]
    interval                    = interval * 1000
    #print("{} keypresses over {:.1f} msec after feature file index {}: {} {}, epoch {}". \
    #format(keypresses, interval, index, date, time, epoch)

  # write a playback script with keypresses and time interval
  last_epoch_time = 0
  first_date, first_time, foo, goo = feature_files["0000"]
  with open("./playback.{}.{}.txt".format(first_date, first_time), "w") as f:
    for index in feature_files:
      date, time, epoch, filename    = feature_files[index]
      if epoch not in keypresses_since_this_image:
        #print("skipping too-early epoch {}".format(epoch))
        continue
      keypresses, interval = keypresses_since_this_image[epoch]
      interval             = interval * 1000
      f.write("{} keypresses over {:.1f} msec\n".format(keypresses, interval))

"""
# for each screenshot's feature file, read that file and put the information about
# the features identified in that file into the dictionary these_boxes[]. For example,
# the feature "rocket_body" that is usually associated with a bunch of 30x30 pixel
# boxes would have an entry boxes['rocket_body'] = ((100, 130, 240, 270), (115 ...), ...)
#   To assist with locating the corresponding screenshot image, the feature
# these_boxes['file_info'] holds (date, time, epoch, filename)
# return boxes[] array, which has index->these_boxes for the file with that index (=frame number)
def read_feature_files_into_boxes(feature_files):
  print("feature_files has {} entries".format(len(feature_files)))
  # now consolidate the features for each frame
  p = re.compile("([\w_]+).*(\d\d\d).*(\d\d\d).*(\d\d\d).*(\d\d\d)")
  boxes = {}
  for index in feature_files:
    date, time, epoch, filename = feature_files[index]
    these_boxes = {}  # object_type->x0, x1, y0, y1
    these_boxes['file_info'] = (date, time, epoch, filename)
    for line in open("{}/{}".format(feature_dirpathname, filename), "r"):
      if line == "": continue
      line = line[0:-1]
      print("{}".format(line))
      m = p.match(line)
      if (m):
        object_name, x0, x1, y0, y1 = m.group(1,2,3,4,5)
        #print("{}: {}, {}, {}, {}".format(object_name, x0, x1, y0, y1))
        if object_name not in these_boxes:
          these_boxes[object_name] = []
        these_boxes[object_name].append([float(x0), float(x1), float(y0), float(y1)])
    boxes[index] = these_boxes  # object_type->x0, x1, y0, y1
    # break
    # print("{}".format(boxes))
  return boxes

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
def consolidate_boxes(boxes):
  feature_data = {}
  print("boxes has {} entries".format(len(boxes)))
  for index in boxes:
    these_boxes = boxes[index]
    these_feature_data = {}
    these_feature_data['file_info'] = these_boxes['file_info']
    for object_name in these_boxes:
      if object_name == 'file_info': continue
      list_of_boxes = these_boxes[object_name]
      if object_name == 'rocket_body':
        #print("rocket body: {}".format(list_of_boxes))
        rocket_body_boxes         = list_of_boxes
        rocket_flame_white_boxes = rocket_flame_yellow_boxes = []
        if 'rocket_flame_white' in these_boxes:
          rocket_flame_white_boxes = these_boxes['rocket_flame_white']
        if 'rocket_flame_yellow' in these_boxes:
          rocket_flame_yellow_boxes = these_boxes['rocket_flame_yellow']
        object_features = consolidate_boxes_for_rocket(rocket_body_boxes, rocket_flame_white_boxes, rocket_flame_yellow_boxes)
        these_feature_data['rocket_height'] = object_features['rocket_height']
        these_feature_data['rocket_x']      = object_features['rocket_x']
        these_feature_data['rocket_slope']  = object_features['rocket_slope']
      # we handle these together with rocket_body above
      elif (object_name == 'rocket_flame_white' or object_name == 'rocket_flame_yellow'): continue
      else:
        object_features = consolidate_boxes_for_non_rocket(list_of_boxes)
        these_feature_data[object_name] = object_features

      '''
      elif object_name == 'barrier':
        print("barrier: {}".format(list_of_boxes))
        object_features = consolidate_boxes_for_barrier(list_of_boxes)
      elif object_name == 'bird':
        print("bird: {}".format(list_of_boxes))
        object_features = consolidate_boxes_for_bird(list_of_boxes)
      elif object_name == 'imp':
        print("imp: {}".format(list_of_boxes))
        object_features = consolidate_boxes_for_imp(list_of_boxes)
      elif object_name == 'monster':
        print("monster: {}".format(list_of_boxes))
        object_features = consolidate_boxes_for_monster(list_of_boxes)
      '''
    feature_data[index] = these_feature_data
  return feature_data
"""

global_rocket_x = 0 #storage for last place of the rocket

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
   slope = -1000.0 #rising

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


'''
def consolidate_boxes_for_barrier(list_of_boxes):
    return 0

def consolidate_boxes_for_bird(list_of_boxes):
   this_feature = []
   this_feature = (x0, x1, y0, y1)
   return this_feature

# returns center y-coordinate of imps, which are not high and can be in mid-air, and left x-coordinate
def consolidate_boxes_for_imp(list_of_boxes):
   this_feature = []
   this_feature = (x0, x1, y0, y1)
   return this_feature

# returns top y-coordinate of monsters, which are high and are always on a lower barrier, and left x-coordinate
def consolidate_boxes_for_monster(list_of_boxes):
   this_feature = []
   this_feature = (x0, x1, y0, y1)
   return this_feature
'''

def process_feature_file(filename):
    global global_rocket_x

    these_boxes = {}  # object_type->x0, x1, y0, y1
    these_boxes['file_info'] = (date, time, epoch, filename)
    # data cleaning: we have to look for the object "monster 2" because p2 also matches but poorly!
    p1 = re.compile("(monster 2)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
    p2 = re.compile("([\w_]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
    for line in open("{}/{}".format(feature_dirpathname, filename), "r"):
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
        # list_of_boxes = filter_rocket_body_list_of_boxes(list_of_boxes)
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

      '''
      elif object_name == 'bird':
        print("bird: {}".format(list_of_boxes))
        object_features = consolidate_boxes_for_bird(list_of_boxes)
      elif object_name == 'imp':
        print("imp: {}".format(list_of_boxes))
        object_features = consolidate_boxes_for_imp(list_of_boxes)
      elif object_name == 'monster':
        print("monster: {}".format(list_of_boxes))
        object_features = consolidate_boxes_for_monster(list_of_boxes)
      '''
    return these_feature_data

# sometimes the rocket body detection finds a sail that has identical colors.
# The tip-off is that there are overlapping boxes with the same x0 and x1
# but different y0 and y1 (ie, stacked vertically). So let's remove them. If we have to we can
# look for a monster in the same image.
# eg jprScreen_0026.2020-11-06.17-05-55.1604703955.0032473.png
##def filter_rocket_body_list_of_boxes(list_of_boxes):
##    bad_entries = []
##    for i in range( len(list_of_boxes)-1 ):
##         i_x0, i_x1, i_y0, i_y1 = list_of_boxes[i]
##         for j in range(1, len(list_of_boxes) ):
##            if i == j: continue
##            j_x0, j_x1, j_y0, j_y1 = list_of_boxes[j]
##            #print("ix0 {} jx0 {} ix1 {} jx1 {} iy0 {} jy0 {}".\
##            #      format(i_x0, j_x0, i_x1, j_x1, i_y0, j_y0))
##            if i_x0 == j_x0 and i_x1 == j_x1 and abs(i_y0 - j_y0) < 30:
##              # this is a spurious detection, so set up to remove both box(i) and box(prior_i)
##              print("Found false detections at index {} and {}".format(i, j))
##              if i not in bad_entries:  bad_entries.append(i)
##              if j not in bad_entries:  bad_entries.append(j)
##    bad_entries.sort(reverse=True)
##    print("filter_rocket_body_list_of_boxes(): Found false detections in boxes {}".format(bad_entries))
##    for i in bad_entries:
##            del list_of_boxes[i]

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
  distance_threshold = 100 #may need to readjust
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


def write_feature_data_to_an_image(these_feature_data, input_image_dir):
    # and write to image for quality check
    #print("these_feature_data: \n{}".format(these_feature_data['file_info']))
    the_date, the_time, the_epoch, the_feature_filename = these_feature_data['file_info']
    # find the file
    filepath = "{}/*{}*{}*{}*png".format(input_image_dir, the_date, the_time, the_epoch)
    print("Looking for image file in {}.".format(filepath))
    filepathname = ''
    for name in glob.glob(filepath):
      filepathname = name
      print("name {}".format(name))
    if not filepathname:
      print("Cannot find image file '{}'".format(filepath))
      return
    print("Reading image file {}".format(filepathname))
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
##    cv2.imshow('the image',the_image)
##    cv2.waitKey(0)
##    cv2.destroyAllWindows()
     #  cv2.imwrite(f"screenshots-with-features-identified/{image_file}.with-features.png",the_image)
    #fp_log.write("{}: pt {} w {} h {}\n".format(name, [min_x0, min_y0], w, h))

def write_feature_data_to_NN_file(these_feature_data, epoch, fp_nn, index):
    global global_rocket_x

    #print("these_feature_data: \n{}".format(these_feature_data['file_info']))

    # format of output file:
    # obs = (correct, rocket_height, rocket_angle, enemy_1_distance, enemy_1_height, 
    #       enemy_2_distance, enemy_2_height, enemy_3_distance, enemy_3_height,
    #       enemy_4_distance, enemy_4_height, barrier_top_distance, barrier_top_height,
    #       barrier_bottom_distance, barrier_bottom_height)
    i = 0
    correct                      = i        ; i = i + 1 #key presses
    enum_rocket_height           = i        ; i = i + 1
    enum_rocket_slope            = i        ; i = i + 1
    enum_enemy1_distance         = i        ; i = i + 1
    enum_enemy1_height           = i        ; i = i + 1
    enum_enemy2_distance         = i        ; i = i + 1
    enum_enemy2_height           = i        ; i = i + 1
    enum_enemy3_distance         = i        ; i = i + 1
    enum_enemy3_height           = i        ; i = i + 1
    enum_enemy4_distance         = i        ; i = i + 1
    enum_enemy4_height           = i        ; i = i + 1
    enum_barrier_top_distance    = i        ; i = i + 1
    enum_barrier_top_height      = i        ; i = i + 1
    enum_barrier_bottom_distance = i        ; i = i + 1
    enum_barrier_bottom_height   = i        ; i = i + 1
    # set the distance to all threats to maximum distance (1000 px)
    feature_vector = [ 0, 0, 0, 1000, 0, 1000, 0, 1000, 0, 1000, 0, 1000, 0, 1000, 0 ]

    # get the "correct answer" from the keypresses file for this screen image
    if epoch in keypresses_since_this_image:
      keypresses, interval = keypresses_since_this_image[epoch]
      #interval             = interval * 1000
      feature_vector[correct] = keypresses
    else:
      feature_vector[correct] = 0                         # KLUDGE: fix me
      #print("skipping too-early epoch {}".format(epoch))

    enemy_counter = 0
    for object in these_feature_data:
       if   object == 'file_info':    continue
       elif object == 'rocket_slope': continue
       elif object == 'rocket_x':     continue
       elif object == 'rocket_height':
          height = int(these_feature_data[object])
          x      = int(these_feature_data['rocket_x'])
          slope  = int(these_feature_data['rocket_slope'])   # slope is the raw slope * 1000
          feature_vector[enum_rocket_height] = height
          feature_vector[enum_rocket_slope]  = slope
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
            feature_vector[enum_barrier_top_height]   = height
          else:  # this object is in the bottom half
            height   = int(min_y)
            feature_vector[enum_barrier_bottom_distance] = distance
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
             feature_vector[enum_enemy1_height]   = height
          elif enemy_counter == 2:
             feature_vector[enum_enemy2_distance] = distance
             feature_vector[enum_enemy2_height]   = height
          elif enemy_counter == 3:
             feature_vector[enum_enemy3_distance] = distance
             feature_vector[enum_enemy3_height]   = height
          elif enemy_counter == 4:
             feature_vector[enum_enemy4_distance] = distance
             feature_vector[enum_enemy4_height]   = height
       else:
         print("writing to NN: Unknown object '{}'".format(object))

    # now print the 15-element vector for the NN (the 16-element format includes the index
    # number of the image, for cross reference. As we progress, we will probably want to also include
    # the run identifier and exclude both of them when reading into jlw_gym.
    # fp_nn.write("{}  {}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}: {}\n".\
    fp_nn.write("{} {} {} {} {} {} {} {} {} {} {} {} {} {} {}\n".\
          format(feature_vector[correct],
                 feature_vector[enum_rocket_height],           feature_vector[enum_rocket_slope], 
                 feature_vector[enum_enemy1_distance],         feature_vector[enum_enemy1_height], 
                 feature_vector[enum_enemy2_distance],         feature_vector[enum_enemy2_height], 
                 feature_vector[enum_enemy3_distance],         feature_vector[enum_enemy3_height], 
                 feature_vector[enum_enemy4_distance],         feature_vector[enum_enemy4_height], 
                 feature_vector[enum_barrier_top_distance],    feature_vector[enum_barrier_top_height], 
                 feature_vector[enum_barrier_bottom_distance], feature_vector[enum_barrier_bottom_height]
                 # , index
                 ))


def show_feature_data():
  print("feature_data:\n")
  for index in feature_data:
    print("Index {}:\n".format(index))
    for object in feature_data[index]:
      print("  Object: {}. Data {}".format(object, feature_data[index][object]))

############################################
#
#   MAIN SECTION
#
############################################

if (len(sys.argv) < 4):
  print("Usage: {} <name of keylog file> <directory of feature-list files> <directory of image files>".format(sys.argv[0]))
  sys.exit(1)

keylog_filename     = sys.argv[1]
feature_dirpathname = sys.argv[2]
image_dirpathname   = sys.argv[3]
print("Using keylog file '{}', feature files in '{}', and screenshot images in {}". \
      format(keylog_filename, feature_dirpathname, image_dirpathname))

keylog_entries, feature_files = setup(keylog_filename, feature_dirpathname) 

#print("Keypress log with list of keypress epoch times:\n{}\n\nList of feature files with image acquisition date, time, epoch".format(keylog_entries))

keypresses_since_this_image = compute_keypresses_following_each_image(keylog_entries, feature_files)  
if len(keypresses_since_this_image) == 0:
  sys.exit(1)

show_and_write_keypresses_data(keypresses_since_this_image, feature_files)

# uncomment this to write the jlw_instruction.new.txt file.
# Also the write_feature_data_to_NN_file() statement and the fp_nn.close() statement
fp_nn = open("jlw_observations.new.txt", "w")

print("feature_files has {} entries".format(len(feature_files)))
# now consolidate the features for each frame
p = re.compile("([\w_]+).*(\d\d\d).*(\d\d\d).*(\d\d\d).*(\d\d\d)")
boxes = {}
for index in feature_files:
    # if index <= "0101": continue
    date, time, epoch, filename = feature_files[index]
    these_feature_data = process_feature_file(filename)

    # uncomment this to see the images with the annotations. These are not currently written to file
    # write_feature_data_to_an_image(these_feature_data, image_dirpathname)

    # uncomment this to write the jlw_instruction.new.txt file and the fp_nn open and .close() statements
    write_feature_data_to_NN_file(these_feature_data, epoch, fp_nn, index)
    #write_feature_data_to_an_image(these_feature_data, image_dirpathname)

# uncomment this to write the jlw_instruction.new.txt file
# Also the write_feature_data_to_NN_file() statement and the fp_nn = open() statement
fp_nn.close()    

# These process all files at once, then process all the feature data at once, then create the output images at once
#boxes        = read_feature_files_into_boxes(feature_files)
#feature_data = consolidate_boxes(boxes)
#write_feature_data_to_image(feature_data, image_dirpathname)
