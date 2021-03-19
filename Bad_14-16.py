import re
##goal is to convert the 14 input to the 16 input 

##all calculations are done with int cast, all outputs are strings
def x_array_from_enemy(en_array):
    feature_count = 0
    x_val = []
    for x_vel in range(0,len(en_array),2): 
       x_val.insert(feature_count, int(en_array[x_vel]))
       feature_count += 1
    ##print(f"x val {x_val}")
    return x_val

def convert_14_to_16(value_array, first_flag, training):
    global x_old, y_old
    rocket_add = []
    en_add = []

    height_loc = 0 ##location of height
    ##regular [height, slope, enemy stuff]
    ##training [correct, height, slope, enemy]
    if training:
        height_loc +=1 
    
    for value in range(len(value_array)):
        if value <= height_loc+1: ##correct, height, slope
            rocket_add.append(value_array[value])
        else:
            en_add.append(value_array[value]) 
            
    if first_flag:
        vel_val = ['0','0']    ## x, y velocity
        rocket_add.extend(vel_val)
        rocket_add.extend(en_add)
        #value_array = rocket_add
        x_old = x_array_from_enemy(en_add)
        y_old = int(rocket_add[height_loc])

    else:
        ##print(f'x old {x_old}')
        x_final = 0
        current_x = x_array_from_enemy(en_add)
        #print(f"current_x {current_x}, x_old {x_old}")
        for vel_i in range(len(current_x)):
            x_interm = abs(x_old[vel_i]-current_x[vel_i])
            #w print(f"x interm/delta {x_interm}, x_final {x_final}")
            if x_interm > x_final:
               x_final = x_interm
       
        if x_final == 0:
            #x  = 1500
            x  = 0
        else:
            x  = x_final

        y = int(rocket_add[height_loc]) - y_old
        vel_val = [str(x), str(y)]
        ##vel_val = [x, y]
        rocket_add.extend(vel_val)
        rocket_add.extend(en_add)
        x_old = x_array_from_enemy(en_add)
        y_old = int(rocket_add[height_loc])
        #print(f"x_old {x_old}, y_old {y_old}")
    value_array = rocket_add
    #print("value_array {}".format(value_array))
    return value_array

def main():
    
    #filename = "data_2"
    filename = "jlw_observations_2021JAN09"
    old = open(f'{filename}.txt', "r")
    new = open(f'{filename}_new.txt', "w")##going to have to edit the NN input
    #new_copy = open(f'{filename}_new_copy.txt', "w") ##something to train against, may not be necessary after multiple runs

    doc_str = "# correct rocket-y rocket-angle x-velocity y-velocity enemy1-x, enemy1-y enemy2-x enemy2-y enemy3-x enemy3-y enemy4-x enemy4-y top-barrier-bottom-y bottom-barrier-top-y\n"
    new.write(doc_str)
    #new_copy.write(doc_str)
    
    first_flag = True
    training = True
    x_old = []
    y_old = 0
    count = 0
    while True: 
        count += 1
     
        # Get next line from file 
        line = old.readline() 
        
        # if line is empty 
        # end of file is reached 
        if not line: 
            break
        #print("Line{}: {}".format(count, line.strip()))

        ##pattern matching
        array_14 = []
        p1 = re.compile("^(\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+)")
        m1 = p1.search(line)
        p2 = re.compile("^(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+) +(-*\d+)")
        m2 = p2.search(line)


        
        if(m1): ##training data
##            print(f'm1 {m1}, len {len(m1.group())}')
            for values in range(1,16):
                array_14.append(m1.group(values))
                
            array_16 = convert_14_to_16(array_14, first_flag, training)
            #print(f"Array 16 {array_16}")
            for value2 in range(len(array_16)):
                new.write(f'{array_16[value2]} ')
                #new_copy.write(f'{array_16[value2]} ')
            new.write('\n')
            #new_copy.write('\n')

            if first_flag:
                first_flag = False
            
        elif(m2): ##data without correct guidence
##            print(f'm2 {m2}')
            for values in range(1,15):
                array_14.append(m2[values])
            training = False
            array_16 = convert_14_to_16(array_14, first_flag, training)
            
            for value2 in range(len(array_16)):
                new.write(f'{array_16[value2]} ')
                #new_copy.write(f'{array_16[value2]} ')
            new.write('\n')
            #new_copy.write('\n')

            if first_flag:
                first_flag = False
        else:
            print("no go")
            new.write(line) ##puts back any text back into the program
            new_copy.write(line)

    new.write("DONE-BAD 0  0 0 0 0 0 0 0 0 0 0 0 0 0")
    #new_copy.write("DONE-BAD 0  0 0 0 0 0 0 0 0 0 0 0 0 0")
    print("done")
    old.close()
    new.close()
    #new_copy.close()

    
main()



