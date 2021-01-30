import numpy as np
import re
import gym
from gym import Env
from gym.spaces import Box
from gym.wrappers import TimeLimit
import sys
try:
    import cv2
except ImportError:
    cv2 = None


#class JLW_SNES_Env(gym.Wrapper)
class JLW_SNES_Env(Env):
    r"""JLW gym preprocessing

    This class is adapted from gym's atari_preprocessing.py to include:
    * replacing env.step() with a custom jlw_step() function to calculate reward
    * using an input stream of "the correct answer" for each step to do imitative learning
    * using an observation vector of features extracted from images rather than the images
    *   themselves, which are quite large compared with the atari images (about 450x580 vs 84x84,
    *   or 37 times larger).  The new observation vector has continuous 14 variables.
    * the output vector has one element, which is the integer number of keypresses to execute
    *   in a row. The range is zero to about 7.
    * using a simple reward function based on the difference between the "correct" action and
      the output of the network.

    The original class followed the guidelines in 
    Machado et al. (2018), "Revisiting the Arcade Learning Environment: 
    Evaluation Protocols and Open Problems for General Agents".

    Specifically:

    * NoopReset: obtain initial state by taking random number of no-ops on reset. 
    * Frame skipping: 4 by default
    * Max-pooling: most recent two observations
    * Termination signal when a life is lost: turned off by default. Not recommended by Machado et al. (2018).
    * Grayscale observation: optional
    * Scale observation: optional
    [Removed:     * Resize to a square image: 84x84 by default]

    Args:
        env (Env): environment
        noop_max (int): max number of no-ops

    [Removed:
        frame_skip (int): the frequency at which the agent experiences the game. 
        screen_size (int): resize Atari frame
        terminal_on_life_loss (bool): if True, then step() returns done=True whenever a
            life is lost. 
        grayscale_obs (bool): if True, then gray scale observation is returned, otherwise, RGB observation
            is returned.
        grayscale_newaxis (bool): if True and grayscale_obs=True, then a channel axis is added to
            grayscale observations to make them 3-dimensional.
        scale_obs (bool): if True, then observation normalized in range [0,1] is returned. It also limits memory
            optimization benefits of FrameStack Wrapper.
     ]
    """
    # trying removing "env" from arg list because it is not clear that we need it, but script won't run without it
    # because it's looking for a name of some sort.  We don't need it if we import Env instead of using gym.Wrapper.
    #def __init__(self, env):
    #    super().__init__(env)
    def __init__(self, datafile):
        #super().__init__(env)
        assert cv2 is not None, \
            "opencv-python package not installed! Try running pip install gym[atari] to get dependencies  for atari"
        self.lives       = 0
        self.frame_skip  = 1      # in case we want to merge groups of frames
        self.game_over   = False
        self.f_obs       = ''
        self.datafile    = datafile
        self.datafile1   = ''
        self.scalefactor = 1000.0   # we divide all our inputs by this so data range from 0 to 1

    def say_hello(self, message="Howdy y'all!"):
        print (message)

    def step(self, action, include_correct=0):
        R = 0.0

        for t in range(self.frame_skip):
            # _, reward, done, info = self.env.step(action)
            obs, reward, done, info = self.jlw_step(action, include_correct)
            R += reward
            self.game_over = done

            if done:
                break
        return obs, R, done, info

    # this seems to return just the observation matrix
    #def reset(self, **kwargs):
    def reset(self, include_correct=0):
        # print("Entering reset with foo=", foo)
        # reset file pointer to the beginning and start reading with the first line in the file
        if self.f_obs != '':
          self.f_obs.seek(0,0)
          (obs, reward, done, info) = self.process_next_line('reset', include_correct)
          #(obs, reward, done, info) = self.process_next_test_line()
          return obs
        

    def jlw_step(self, action, include_correct=0):
        return self.process_next_line(action, include_correct) ##this is to the process next line with the fixing data
       ## return self.process_next_test_line()

    # The hard work is here
    # Strategy: we force the NN to reproduce the keystrokes of the human expert. The
    #   keystrokes consist of zero to N presses of the action key in a given time interval.
    #   The "correct" data are known to us but are not part of the observation vector.
    #   The reward is calculated by subtracting the difference of abs(action - correct) from N.
    #     When the game ends, the reward is a large positive value if it ended successfully and
    #     a large negative value if not.  The library considers 175 a winning value so make sure
    #     we can reach that. Another example uses 200 as the reward for successfully completing a game.
    # inputs:
    #   maybe: screen image in self.obs_buffer[0]  (the prior screen image is in self.obs_buffer[1]
    #   maybe: data stream consisting of observation vector plus the "correct answer"
    #          data stream includes: rocket height, rocket angle,
    #                                enemy #1 distance in pixels, enemy #1 height in pixels (distance from top)
    #                                enemy #2 distance in pixels, enemy #2 height in pixels (distance from top)
    #                                enemy #3 distance in pixels, enemy #3 height in pixels (distance from top)
    #                                enemy #4 distance in pixels, enemy #4 height in pixels (distance from top)
    #                                barrier top    distance in pixels, barrier top lowest height in pixels
    #                                barrier bottom distance in pixels, barrier bottom lowest height in pixels
    #   include_correct: a flag, normally 0. If 1, we include the correct answer as first element in the
    #                    obs list. This is used in checking how good the output is after training.
    # our model could include constants (rocket velocity in pixels/sec, gravity in pixels/(sec*sec),
    #                                    and impulse per action keypress (radians rocket direction/press)
    #                                    in order to calculate the correct answer mathematically,
    #           but we will use the "correct answer" stream instead to do imitative learning
    # returns: observation vector, reward, done, info 

## EDIT BEGINS
##    def process_next_test_line(self):
##        if self.f_obs == '':
##           try:
##             self.f_obs = open(self.datafile, "r")
##             print("Opened '{}' for data input".format(self.datafile))
##           except:
##             print("Cannot open input file '{}'.".format(self.datafile))
##             sys.exit(1)
##        try:
##          line = self.f_obs.readline()
##          # implement the comment character but only in the first column
##          while line[0:1] == '#':
##             line = self.f_obs.readline()
##        except:
##           print("Error reading input data: found empty line. Exiting...")
##           sys.exit(1)
##        if '' == line:  # end of file
##             return [(),  -1, 0, '']
##        line = line[0:-1]              # remove terminal line return
##        line = line.strip()            # remove any leading or trailing white space
##        line = line.replace("  ", " ") # shrink doubled spaces
##        
##        obs_string = line.split(' ')
##
##        info    = ''
##        
##        obs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
##        reward = 0
##        obs = []
##        for datum in obs_string:
##            obs.append(float(datum)/self.scalefactor)   # normalize all the data to between zero and 1
##        done    = False
##        
##        return [obs, reward, done, info]
##EDIT ENDS

    def process_next_line(self, action, include_correct):
        # print("Entering process_next_line()");
        #print(f"Include Correct is {include_correct}")
        if self.f_obs == '':
           try:
             self.f_obs = open(self.datafile, "r")
             print("Opened '{}' for data input".format(self.datafile))
           except:
             print("Cannot open input file '{}'.".format(self.datafile))
             sys.exit(1)
        try:
          line = self.f_obs.readline()
          # print("line: '{}'".format(line))
          # implement the comment character but only in the first column
          while line[0:1] == '#':
             line = self.f_obs.readline()
             # print("line: {}".format(line))
        except:
           print("Error reading input data: found empty line. Exiting...")
           sys.exit(1)
        if '' == line:  # end of file
             return [(),  -1, 0, '']
        line = line[0:-1]              # remove terminal line return
        line = line.strip()            # remove any leading or trailing white space
        line = line.replace("  ", " ") # shrink doubled spaces

        #obs = (correct, rocket_height, rocket_angle, x vel, y vel, enemy_1_distance, enemy_1_height, 
        #       enemy_2_distance, enemy_2_height, enemy_3_distance, enemy_3_height,
        #       enemy_4_distance, enemy_4_height, barrier_top_distance, barrier_top_height,
        #       barrier_bottom_distance, barrier_bottom_height)
        obs_string = line.split(' ')
        info    = ''
        # remove the correct answer from the observation vector and put it in a local variable
        # now calculate reward and done status
        correct = obs_string.pop(0)
        #print(f"Correct from SNES_env is {correct} ")

        #  provide a default value for obs in case we encounter one of the first 3 options
        obs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if correct == 'DONE-OK':
           reward = 200
           done   = True
        elif correct == 'DONE-BAD':
           reward = -200
           done   = True
        elif action == "reset":
           reward = 0
           done   = False
        else:
           # convert input to floating point format. Note that the "correct" field was popped above
           # by    correct = obs_string.pop(0) because we needed that datum to figure out whether
           # we can convert the rest of the data to float.
           obs = []
           for datum in obs_string:
               if datum == 1500:  datum = 1000
               obs.append(float(datum)/self.scalefactor)   # normalize all the data to between zero and 1
           # print("obs vector string: ", obs_string)
           # print("obs vector: ", obs)

           # map the actual output value of 0-19 onto the model's range of possible outputs, 1-20.
           # we can subtract one when we take the model output back to the simulator.
           correct = float(correct)
           correct = correct + 1
##           reward  = 20 - abs(correct - action)
##           reward  = reward * reward

           (rocket_y, rocket_angle, rocket_x_vel, rocket_y_vel, e1_x, e1_y, e2_x, e2_y, e3_x, e3_y, e4_x, e4_y, bu_x, bu_y, bl_x, bl_y) = obs
           reward = 0.1
           if e1_x != 1.00 and rocket_y > e1_y - .05 and rocket_y < e1_y + .05:     reward = reward - 0.01/e1_x
           if e2_x != 1.00 and rocket_y > e2_y - .05 and rocket_y < e2_y + .05:     reward = reward - 0.01/e2_x
           if e3_x != 1.00 and rocket_y > e3_y - .05 and rocket_y < e3_y + .05:     reward = reward - 0.01/e3_x
           if e4_x != 1.00 and rocket_y > e4_y - .05 and rocket_y < e4_y + .05:     reward = reward - 0.01/e4_x
           if rocket_y < bu_y + .05:                                                reward = reward - 0.01/bu_x
           if rocket_y > bl_y - .05:                                                reward = reward - 0.01/bl_x
           if rocket_y <  .10:                                                      reward = reward - 0.01/rocket_y
           if rocket_y >  .40:                                                      reward = reward - 0.01/(0.5 - rocket_y)
           done    = False

        #print(f'Type {type(correct)}')
        if include_correct == True and (isinstance(correct, float) or isinstance(correct, int)):
            obs.append(correct)
            #print(f'Appended correct {correct}')
        elif include_correct == True and not (isinstance(correct, float) or isinstance(correct, int)):
            lest_we_pray = 0
            obs.append(lest_we_pray)
            #print(f"Not an int or float, correct send is {lest_we_pray}")
        else:
            print(f"Not appended {correct}")
        return [obs, reward, done, info]

    # returns ( (x_training, y_training), (x_testing, y_testing))
    # where x is the input vector and y is the "correct" label/result
    #This obscenity was made to have half the data for testing and the other half for training.
    def make_batch_data(self, compare_file = ""):
        action  = 0    # dummy value: we're just want the input data
        x      = []
        y      = []
        critic = []  # what is supposed to go into this? it's the prediction of the action
        done = False
        line_num = 0
        #print(done)

        if compare_file != "":
            p1 = re.compile("^(\w.*\.txt|\d.*\.txt)")  
            m1 = p1.search(compare_file)
            if (m1):
                self.datafile1 = self.datafile
                self.datafile  = compare_file
                self.f_obs     = ''
                #print(self.datafile)
        while not done:         
           [obs, reward, done, info] = self.process_next_line(action, include_correct=1)
##           [obs, reward, done, info] = self.process_next_test_line()
           if reward < 0:
               break;
           x.append(obs)
           correct = obs.pop()
           #print(f"correct {correct}")
           correct_array = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
##           print(f"correct array is {correct_array}")
           correct_array[int(correct)] = 1
           y.append(correct_array)
           critic.append(float(correct))
           line_num += 1

           #print(f'x {x}, \ny {y}')
        #print(line_num)
        if compare_file != "": #This is to reset the file being read to the inital batch file
            self.datafile = self.datafile1
            self.f_obs     = ''
            [obs, reward, done, info] = self.process_next_line(action, include_correct=1)
        return x, y, critic, line_num
        # read the rest of the input file
##        x_testing      = []
##        y_testing      = []
##        critic_testing = []  # what is supposed to go into this? it's the prediction of the action
##        for i in range(101):
##           [obs, reward, done, info] = self.process_next_line(action, include_correct=1)
####           [obs, reward, done, info] = self.process_next_test_line() 
##           if reward < 0:
##               break;
##           x_testing.append(obs)
##           correct = obs.pop()#()
####           print(f"correct {correct}")
##           correct_array = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 0, 0 ,0 ,0 ,0 ,0 ,0]
##           #Why different numbers? because want to see if pop is the issue here
##           correct_array[int(correct)] = 1
##           y_testing.append(correct_array)
##           critic_testing.append(float(correct))
##           print("X train {}\n Y train {}\n critic tr {}\n x te {}\n y te {}\n c te {}\n".format(x_training, y_training, critic_training, x_testing, y_testing, critic_testing))
##        return x_training, y_training, critic_training, x_testing, y_testing, critic_testing


# this section is adapted from the SimpleShipAI project at https://github.com/jmpf2018/SimpleShipAI
if __name__ == '__main__':
    mode = 'normal'
    if mode == 'normal':
        env = JLWPreprocessing(gym.Wrapper)
        for i_episode in range(10):
            ##observation = env.reset()
            env.reset()
            # for t in range(10000):
            for t in range(10):
                action = np.array([1])
                print("Starting Step t {} with action {}".format(t, action))
                observation, reward, done, info = env.step(action)
                if done:
                    print("Episode finished after {} timesteps".format(t + 1))
                    break
        env.close()
   
