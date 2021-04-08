#!/usr/bin/python3

import cv2
import numpy as np
import os
import sys
import socket
import time
import re

##HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
##PORT_RECEIVE = 9081    # Port to listen on (non-privileged ports are > 1023)
##PORT_SEND    = 9082     # Port to listen on (non-privileged ports are > 1023)
##DAEMON_NAME  = "FE_socket"
##
##def setup_sockets():
##   global s_receive, s_send
##
##   s_receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##   print("{} to bind to port {}".format(DAEMON_NAME, PORT_RECEIVE))
##   s_receive.bind((HOST, PORT_RECEIVE))
##   s_send    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##   setup_sendsocket()
##
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
##       
##
##def connect_to_downstream_socket():
##  global s_send
##
##  if s_send != '': return
##
##  try:
##     s_send    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##     s_send.connect((HOST, PORT_SEND))
##  except:
##     print("Cannot connect to port {}. Quitting...".format(PORT_SEND))
##
##def closesocket():
##   global s_receive, s_send
##   if s_receive != '':
##     s_receive.shutdown(socket.SHUT_RDWR)
##     s_receive.close()
##   print(f"Closed socket {PORT_RECEIVE}")

# look for the template in the color screenshot the_image from JetPilotRising. The standard
# cv2 matchTemplate with color misses many rocket images that seem clear enough to the eye.
# strategy:
#   scan with a block of NxM pixels corresponding to the typical size of the target
#   look for patterns of color characteristic of the target:
#      yellow and white for the rocket,
#      silver           for coins
#      brown            for monster
#      dark brown       for barriers
#      orange           for birds
#   acceptance pattern has to be statistical since our rules are not perfect
#   steps: for each target, scan in broad jumps to find a region of interest
#          then survey that region more carefully to define location
#   impression: Looks like this works best for the rocket, which is poorly detected by templates
#               This works poorly for coins, which are well detected by templates.
#               So we can run this in the narrow strip holding the rocket
def find_rocket_in_JPR_image():
  global the_image, f, sky, water

  tpl_w = tpl_h = 30   # make up an arbitrary 75-pixel template area
  img_h, img_w, img_d = the_image.shape
  # scan over the image with 50% overlapping of template
  #print("scanning the_image ({}x{}) with template area {}x{}".format(img_w, img_h, tpl_w, tpl_h))
  rect_list = []
  # rocket is in band x 40-275 and y 0-440 (full height). Other objects are in x>200 or so.
  # even though coins tend to be missed, we shift by 1/2 sample width for efficiency
  #  for x in range(0, int(img_w - tpl_w/2) - 1, int(tpl_w/2)):
  #    for y in range(0, int(img_h - tpl_h/2) - 1, int(tpl_h/2)):
  for x in range(40, 275, int(tpl_w/2)):
    #for y in range(0, int(img_h - tpl_h/2) - 1, int(tpl_h/2)):
    for y in range(sky, water, int(tpl_h/2)):
       if x + tpl_w >= img_w:
         w = img_w - x - 1
       else:
         w = tpl_w
       if y + tpl_h >= img_h:
         h = img_h - y - 1
       else:
         h = tpl_h
       temp = JPR_examine_area_for_rocket(x, y, w, h)
       if temp is not None:
         for i in temp:
           rect_list.append(i)
  #print("rect_list for image: {}".format(rect_list))
  for rect in rect_list:
      w = h = 30
      color_b = color_g = color_r = 255
      name, min_x0, min_y0 = rect
      if name == 'rocket_body':
         color_b = 0; color_g = 0; color_r = 255
      if name == 'rocket_flame_yellow':
         color_b = 0; color_g = 255; color_r = 255
      if name == 'rocket_flame_white':
         color_b = 155; color_g = 155; color_r = 155
      #  "the_image" gets written to disk as the annotated image.
      cv2.rectangle(the_image, (min_x0, min_y0), (min_x0 + w, min_y0 + h), (color_b,color_g,color_r), 2)
      tab_str = "\t"
      if len(name) < 15:
          tab_str = "\t\t"
      if len(name) <  7:
          tab_str = "\t\t\t"
      f.write("{}{} {} \t {} \t {} \t {}\n".format(name,tab_str, min_x0, min_x0 + w, min_y0, min_y0 + h))
  # looks like the image is indexed as [y:x]
  # subregion = the_image[119:192, 90:244]
  # cv2.imshow('subregion',subregion)

  #cv2.imshow('the image',the_image)
  #cv2.waitKey(0)
  #cv2.destroyAllWindows()

def find_nonrocket_in_JPR_image():
  global the_image, f, sky, water

  tpl_w = tpl_h = 30   # make up an arbitrary 75-pixel template area
  img_h, img_w, img_d = the_image.shape
  # scan over the image with 50% overlapping of template
  #print("scanning the_image ({}x{}) with template area {}x{}".format(img_w, img_h, tpl_w, tpl_h))
  rect_list = []
  # rocket is in band x 40-275 and y 0-440 (full height). Other objects are in x>200 or so.
  # even though coins tend to be missed, we shift by 1/2 sample width for efficiency
  #  for x in range(0, int(img_w - tpl_w/2) - 1, int(tpl_w/2)):
  #    for y in range(0, int(img_h - tpl_h/2) - 1, int(tpl_h/2)):
  for x in range(200, 580, int(tpl_w/2)):
    # for y in range(0, int(img_h - tpl_h/2) - 1, int(tpl_h/2)):
    for y in range(sky, water, int(tpl_h/2)):
       if x + tpl_w >= img_w:
         w = img_w - x - 1
       else:
         w = tpl_w
       if y + tpl_h >= img_h:
         h = img_h - y - 1
       else:
         h = tpl_h
       temp = JPR_examine_area_for_nonrocket(x, y, w, h)
       if temp is not None:
         for i in temp:
           rect_list.append(i)
  #print("rect_list for image: {}".format(rect_list))
  for rect in rect_list:
      w = h = 30
      color_b = color_g = color_r = 255
      name, min_x0, min_y0 = rect
      if name == 'barrier':
         color_b = color_g = color_r = 100
      if name == 'bird':
         color_b = 0; color_g = 0; color_r = 255
      if name == 'monster':
         color_b = 0; color_g = 255; color_r = 255
      cv2.rectangle(the_image, (min_x0, min_y0), (min_x0 + w, min_y0 + h), (color_b,color_g,color_r), 2)
      tab_str = "\t"
      if len(name) < 15:
          tab_str = "\t\t"
      if len(name) <  7:
          tab_str = "\t\t\t"
      f.write("{}{} {} \t {} \t {} \t {}\n".format(name,tab_str, min_x0, min_x0 + w, min_y0, min_y0 + h))

# this looks in the area to the right of where the rocket is. By the time an object is in the rocket's space,
# it's probably too late to intervene
def JPR_examine_area_for_nonrocket(x0, y0, w, h):
  #print("starting {}+{} {}x{}".format(x0, y0, w, h))
  objects = ['barrier', 'bird']
  count = {}
  count_subsq = {}
  for object in objects:
    count[ object ] = 0
    count_subsq[ object ] = [ [0, 0, 0], [0, 0, 0], [0, 0, 0] ]

  for x   in range(x0, x0 + w - 2, 1):
     for y in range(y0, y0 + h - 2, 1):

       # divide the square into 9 subsquares so we can look (roughly) at shape. We store the
       # characteristics of each pixel in the overall count[] and also in the count_subsq[][]
       divisions_per_dimension = 3
       template_size                = 30  # we have to fix this here because w/h are reduced at the edges of images
       pixels_per_division         = int( template_size / divisions_per_dimension )
       x1 = int( (x - x0) / pixels_per_division)
       y1 = int( (y - y0) / pixels_per_division)   # assume we are using a square, otherwise compute per dimension

       # count the number of pixels that match a rule
       # red = float(the_image[x][y][0]); green = float(the_image[x][y][1]); blue = float(the_image[x][y][2]); 
       # looks like the image is indexed as BGR and [y:x]
       red = float(the_image[y][x][2]); green = float(the_image[y][x][1]); blue = float(the_image[y][x][0]); 
       if green > 0:
          ratio_rg = red/green;
       else: 
          ratio_rg = 10000
       if blue > 0:
         ratio_rb = red/blue;
       else:
         ratio_rb = 10000;
       if blue > 0:
         ratio_gb = green/blue
       else:
         ratio_gb = 10000;
       intensity = red*red + green*green + blue*blue

       if red < 5 and green < 5 and blue < 5:
         count['barrier'] = count['barrier'] + 1
       elif (intensity < 3000 and ratio_rb > 1.5 and
           red < 15 and green < 15 and blue < 10):
         count['barrier'] = count['barrier'] + 1
       elif (intensity < 3000 and ratio_rb > 2 and
           red < 50 and green < 30 and blue < 30):
         count['barrier'] = count['barrier'] + 1

       if (ratio_rb > 3 and 
           red > 200 and green > 100 and blue < 50):
         count['bird'] = count['bird'] + 1
       if (ratio_rb > 5 and 
           red > 120 and green > 50 and blue < 50):
         count['bird'] = count['bird'] + 1

  result = []
  thresholds = {'barrier': 0.8, 'bird': 0.7 }
  for object in ('barrier', 'bird'):
     threshold = thresholds[object] * w * h
     if count[object] > threshold:
       result.append(["{}".format(object), x0, y0])

  return result


# look for rocket. This occurs in a strip that is narrow in the x-dimension where the rocket is constrained to be
def JPR_examine_area_for_rocket(x0, y0, w, h):
  #print("starting {}+{} {}x{}".format(x0, y0, w, h))
  count = {}
  count['rocket_flame_white'] = count['rocket_flame_yellow'] = count['rocket_body'] = 0; 
  for x   in range(x0, x0 + w - 2, 1):
     for y in range(y0, y0 + h - 2, 1):
       # count the number of pixels that match a rule
       # red = float(the_image[x][y][0]); green = float(the_image[x][y][1]); blue = float(the_image[x][y][2]); 
       # looks like the image is indexed as BGR and [y:x]
       red = float(the_image[y][x][2]); green = float(the_image[y][x][1]); blue = float(the_image[y][x][0]); 
       if green > 0:
          ratio_rg = red/green;
       else: 
          ratio_rg = 10000
       if blue > 0:
         ratio_rb = red/blue;
       else:
         ratio_rb = 10000;
       if blue > 0:
         ratio_gb = green/blue
       else:
         ratio_gb = 10000;
       intensity = red*red + green*green + blue*blue
 
       if (ratio_rb > 0.95 and ratio_gb > 0.95 and ratio_rg > 0.95 and
           ratio_rb < 1.05 and ratio_gb < 1.05 and ratio_rg < 1.05 and
           red > 250 and green > 250 and blue > 250 and
           intensity > 100000):
         count['rocket_flame_white'] = count['rocket_flame_white'] + 1

       if (ratio_rb > 2 and ratio_gb > 1.5 and ratio_rg > 1.1 and
           ratio_rb < 5 and ratio_gb < 4.0 and ratio_rg < 1.5 and
           red > 120 and green > 120 and blue < 100 and
           intensity > 30000):
         count['rocket_flame_yellow'] = count['rocket_flame_yellow'] + 1

       if (ratio_rb > 1.1 and ratio_gb > 1.0 and ratio_rg > 1.0 and
           ratio_rb < 1.3 and ratio_gb < 1.2 and ratio_rg < 1.1 and
           red > 100 and green > 120 and blue > 90 and
           intensity > 0):
         # print("x,y {}/{}. RGB {}/{}/{}. ratio_rg {}, ratio_rb {}, ratio_gb {}, intensity {}".format(x, y, red, green, blue, ratio_rg, ratio_rb, ratio_gb, intensity))
         count['rocket_body'] = count['rocket_body'] + 1

  result = []
  thresholds = {'rocket_flame_white': 0.2, 'rocket_flame_yellow': 0.3, 'rocket_body': 0.5 }
  for object in ('rocket_flame_white', 'rocket_flame_yellow', 'rocket_body'):
     threshold = thresholds[object] * w * h
     if (count[object] > threshold):
         result.append(["{}".format(object), x0, y0])

  return result


# modifies the_image. 
# color comparison from stackoverflow.com/questions/55828943/use-matchtemplate-with-colored-images-opencv
def find_template_in_image(template_pathname, color_r, color_g, color_b, template_name):
  global the_image, f

  #print("template_pathname '{}', template '{}'".format(template_pathname,template))
  #print("template_pathname '{}'".format(template_pathname))
  color_p = 1
  if (color_p):
    template = cv2.imread(template_pathname)
    if ( "{}".format(template) == 'None'):
       print("cannot load template '{}'".format(template_pathname))
       return
    d, w, h = template.shape[::-1]
    # print('Template dimensions: ', template.shape, '. W/H/D {}/{}/{}'.format(w,h,d))
    res = cv2.matchTemplate(the_image, template, cv2.TM_SQDIFF_NORMED)
    threshold = 0.1
    loc = np.where( res <= threshold)
  else:
    img_gray = cv2.cvtColor(the_image, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(template_pathname,0)  # grayscale
    # print("template_pathname '{}', template '{}'".format(template_pathname,template))
    if ( "{}".format(template) == 'None'):
       print("cannot load template '{}'".format(template_pathname))
       return
    w, h = template.shape[::-1]
    #print('Template dimensions: ', template.shape)
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
    threshold = 0.8    
    loc = np.where( res >= threshold)

  # coalesce overlapping identifications based on the x0,y0 point. Use 1/2 of width and height as threshold
     
  # store a list of the x0,y0 corner of each rectangle
  list_of_rectangles = []
#  for pt in sorted( zip(*loc[::-1]), key=my_sort_function ):
  for pt in zip(*loc[::-1]):
      # print("{}: pt {} w {} h {}\n".format(template_name, pt, w, h))
      if len(list_of_rectangles) == 0:
          list_of_rectangles.append((pt[0], pt[0], pt[1], pt[1]))
      else:
          found_it = 0
          # step through the rectangles we've seen already and see if we can lump this one in
          for i in range(len(list_of_rectangles)):
             rect = list_of_rectangles[i]
             min_x0 = rect[0];  max_x0 = rect[1]; min_y0 = rect[2]; max_y0 = rect[3]
             # consider the points the same if the rectangles overlap 50%
             if abs(min_x0 - pt[0]) <= w/2:
                min_x0 = min(min_x0, pt[0])
                max_x0 = max(max_x0, pt[0])
             if abs(min_y0 - pt[1]) <= h/2:
                 min_y0 = min(min_y0, pt[1])
                 max_y0 = max(max_y0, pt[1])
             if ( (pt[0] >= min_x0 and pt[0] <= max_x0) and
                (pt[1] >= min_y0 and pt[1] <= max_y0) ):
                list_of_rectangles[i] = (min_x0, max_x0, min_y0, max_y0)
                found_it = 1
                break  # we assume each point can match only one existing rectangle
          if (not found_it):
                # add this rectangle to the list
                list_of_rectangles.append((pt[0], pt[0], pt[1], pt[1]))
  list_of_rectangles = sorted(list_of_rectangles, key=my_sort_function)
#  print the objects of this template type that were found in this image
#  if len(list_of_rectangles) > 0:
#    print("{}: ".format(template_name),list_of_rectangles)
  for rect in list_of_rectangles:
      min_x0 = rect[0];   min_y0 = rect[2];
      #min_x0 = rect[2];  max_x0 = rect[3];  min_y0 = rect[0]; max_y0 = rect[1]
      cv2.rectangle(the_image, (min_x0, min_y0), (min_x0 + w, min_y0 + h), (color_b,color_g,color_r), 2)
      tab_str = "\t"
      if len(template_name) < 15:
          tab_str = "\t\t"
      if len(template_name) <  7:
          tab_str = "\t\t\t"
      f.write("{}{} {} \t {} \t {} \t {}\n".format(template_name,tab_str, min_x0, min_x0 + w, min_y0, min_y0 + h))

# sort by x-coordinate and then by y-coordinate
# we might try dividing each by 10 to try to group nearby points
# each element in tuple is (min_x0, max_x0, min_y0, max_y0)
def my_sort_function(tuple):
    return tuple[0]*1000 +tuple[2]

def analyze_image(input_image_name_root, input_image_dir):
  global the_image, f, sky, water
  global s_send
  
  # location of first period in name
  cp              = input_image_name_root.index('.')
  # find the portion of the name before the first period
  # we use this to select the templates for use with this image
  template_prefix = "jpr"
  #template_prefix = input_image_name_root[0:cp]

  print("Analyzing image {}".format(input_image_name_root))

  # read the original image
  the_image = cv2.imread("{}/{}".format(input_image_dir,input_image_name_root), cv2.IMREAD_COLOR)
  #print("image dimensions (Height/Width/Colors): ", the_image.shape)
  feature_name = f'feature-lists/{input_image_name_root}.feature-list.txt'
  f = open(feature_name, "w")
  f.write("Object name\t\t x0 \t x1 \t y0 \t y1\n")

  d, w, h = the_image.shape[::-1]
  sky    = 0
  water = h
  if h < water:
    water = h

  # show the image
  #  cv2.imshow('the image', the_image)
  #  cv2.imshow('Window name', the_image_old)
  #  cv2.waitKey(0) # waits until a key is pressed in the window
  #  cv2.destroyAllWindows() # destroys the window showing image

  # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html
  targets = (
              ("jpr.template.monster.1.png",                                  255, 255, 255,  "monster 1"),
              ("jpr.template.monster.2.png",                                  255, 255, 255,  "monster 2"),
              ("jpr.template.jlw-screencapture.jprScreen_32.png.Monster.png", 255, 255, 255, "monster"),
              ("jpr.template.jlw-screencapture.jprScreen_33.png.Monster.png", 255, 255, 255, "monster"),
              ("jpr.template.jlw-screencapture.jprScreen_34.png.Monster.png", 255, 255, 255, "monster"),
              ("jpr.template.jlw-screencapture.jprScreen_35.png.Monster.png", 255, 255, 255, "monster"),
              ("jpr.template.jlw.enemy-imp.png",                              255, 255, 255, "imp"),
              ("jpr.template.jlw.enemy-imp1.png",                             255, 255, 255, "imp"),
              ("jpr.template.jlw.enemy-imp2.png",                             255, 255, 255, "imp"),
              ("jpr.template.jlw.enemy-imp3.png",                             255, 255, 255, "imp"),
              ("jpr.template.jlw.enemy-imp4.png",                             255, 255, 255, "imp"),
              ("jpr.template.jlw.enemy-imp5.png",                             255, 255, 255, "imp"),
              ("jpr.template.jlw.enemy-imp6.png",                             255, 255, 255, "imp"),
              ("jpr.template.jlw.enemy-imp7.png",                             255, 255, 255, "imp"),
              ("jpr.template.jlw.enemy-imp8.png",                             255, 255, 255, "imp"),
              ("jpr.template.jlw.enemy-imp9.png",                             255, 255, 255, "imp"),
  )

  for target in targets:
      (template_pathname, color_r, color_g, color_b, template_name) = target
      if template_pathname[0:len(template_prefix)] != template_prefix:
         continue
      # print("trying template '{}'\n".format(template_pathname))
      find_template_in_image("./templates/{}".format(template_pathname), color_r, color_g, color_b, template_name)

  # this finds the rocket and other objects
  #cv2.imshow('the image',the_image)
  #cv2.waitKey(0)
  #cv2.destroyAllWindows()
  find_rocket_in_JPR_image()
  find_nonrocket_in_JPR_image()

  #cv2.imshow('result', the_image)
  #cv2.waitKey(0) # waits until a key is pressed in the window
  #cv2.destroyAllWindows() # destroys the window showing image
  f.close()
  cv2.imwrite("screenshots-annotated/{}.annotated.png".format(input_image_name_root),the_image)

###Daemon send
##  if s_send == '': connect_to_downstream_socket()    # this daemon ought to exist by now
##  data   = feature_name.encode('utf-8')
##  s_send.sendall(data) #that file
##  print(f"{DAEMON_NAME} sent data {data.decode()} to CF_socket ")
####  reply = s_send.recv(1024)
####  print(" .. {} got the following: {}".format(DAEMON_NAME, reply.decode()))
##  
#
#  main
#
def main():
##  global s_receive, s_send
##     
##  while True:
##     s_receive.listen()
##     conn, addr = s_receive.accept()
##     
##     print('Connected by', addr)
##     while True:
##     #This takes in the data from screenshot 
##         data = conn.recv(1024)
##         if not data:
##            break
##     ##screenshots/jprScreen_{str}.{datetime_str}.{epoch_time}.png is sent. use as filename
##         data = data.decode()
##         print(f"{DAEMON_NAME} received data {data}")
##         input_image_dir1 = re.search("^(\w*)", data)
##         input_image_dir = input_image_dir1.group(1)
##         input_image_name_root1 = re.search("(jprScreen_(\d+)\.(\d{4}-\d\d-\d\d)\.(\d\d-\d\d-\d\d)\.(\d+\.\d+)\.png)",data)
##         input_image_name_root = input_image_name_root1.group(1)
####         print(f" Image dir {input_image_dir}, input image name {input_image_name_root}")


   if (not os.path.exists("./screenshots-annotated")):
     os.mkdir("./screenshots-annotated")

   if (not os.path.exists("./feature-lists")):
     os.mkdir("./feature-lists")

   if (not os.path.exists("./logs")):
     os.mkdir("./logs")

   if (not os.path.exists("./screenshots")):
     print("Please move your screenshots to the subdirectory 'screenshots'")
     sys.exit(1)

   if (not os.path.exists("./templates")):
     print("Please move your templates to the subdirectory 'templates'")
     sys.exit(1)

   images = []
   if (len(sys.argv) < 2):
     print("Usage: {} <directory of input screenshots> <skip start> <skip factor>\n".format(sys.argv[0]))
     sys.exit(1);
   input_image_dir = sys.argv[1]

   skip_start = skip_factor = 0
   if (len(sys.argv) == 3):
     skip_start  = sys.argv[2]
     skip_factor = sys.argv[3]
     print("This process will skip the first {} entries and then process every {} file".format( \
                                                                                                skip_start, skip_factor))

   input_images = []
   for entry in os.scandir(input_image_dir):
     if (entry.name[-3:] == "png"):
        input_images.append(entry.name)
   input_images.sort()

   for input_image_name_root in input_images:
     if skip_start > 0:
       skip_start = skip_start - 1
       continue
     print(input_image_name_root)
     analyze_image(input_image_name_root, input_image_dir)
     skip_start = skip_factor - 1

##   analyze_image(input_image_name_root, input_image_dir)

   print("done");
main()
##try:
##  setup_sockets()
##  main()
##finally:
##  closesocket()
  
