"""
Description: Adaptation of keras.io example "Implement Actor Critic Method in CartPole environment."
             to imitation learning of SNES games
Method: Replace reliance on CartPole-v0 environment with jlw-snes-v0 environment
        Adapt the network to the Jet Pilot Rising game with 14 continuous inputs and
        1 output with 10 integer values.

Title: Actor Critic Method
Author: [Apoorv Nandan](https://twitter.com/NandanApoorv)
### Actor Critic Method
As an agent takes actions and moves through an environment, it learns to map
the observed state of the environment to two possible outputs:
1. Recommended action: A probabiltiy value for each action in the action space.
   The part of the agent responsible for this output is called the **actor**.
2. Estimated rewards in the future: Sum of all rewards it expects to receive in the
   future. The part of the agent responsible for this output is the **critic**.
Agent and Critic learn to perform their tasks, such that the recommended actions
from the actor maximize the rewards.
### References
- [CartPole](http://www.derongliu.org/adp/adp-cdrom/Barto1983.pdf)
- [Actor Critic Method](https://hal.inria.fr/hal-00840470/document)
"""
"""
## Setup
"""

import gym
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import jlw_gym
import math
import os

def find_index_of_max_element(the_list):
    the_list = np.squeeze(the_list)
    the_max_value = -1
    the_max_index = 0;
    for i in range(len(the_list)):
        if the_list[i] > the_max_value:
            the_max_value = the_list[i]
            the_max_index = i
    return the_max_index

def generate_test_predictions(x_data): ##For trained network
    prediction       = model.predict([x_data])
    prediction_index = find_index_of_max_element(prediction[0])

    return prediction

def generate_predictions(x_test, y_test, model, line_num): 
##    global model

    # this is what we will do to play games once we have a trained network: accept a line of
    # features and generate keypress commands to the emulator
    # Generate predictions (probabilities -- the output of the last layer)
    # on new data using `predict`
    print("Generate predictions")
##    print(model.summary())
    # step through one input at a time even though model.predict is designed to
    # take a bunch of lines at a time
    sum_2_error = 0
    count       = 0
    #print(f"x test {x_test},\n y test {y_test}")
    for i in range(line_num):
        x_input    = x_test[i]
        #print("x input  ", x_input)

        y_output   = y_test[i]
        #print("y output index={} and vector=".format(find_index_of_max_element(y_output)), y_output)

        prediction       = model.predict([x_input])
        y_index          = find_index_of_max_element([y_output])
        prediction_index = find_index_of_max_element(prediction[0])
        ## print("prediction vector = ", prediction[0])
        ## print("prediction index={} and vector=".format(prediction_index, prediction[0]))
        #print("y output index= {}, prediction index={}".format(y_index, prediction_index))
        print("correct output index= {}, prediction index={}".format(y_index, prediction_index))
        sum_2_error = sum_2_error + (y_index - prediction_index)*(y_index - prediction_index)
        count       = count + 1
        #print(f"N predict {count}")

    #  sum_2_error = math.sqrt(sum_2_error)
    print("N = {}, RMS error {:.5f}".format(count, sum_2_error));



# Configuration parameters for the whole setup
def main():
    seed = 42
    gamma = 0.99  # Discount factor for past rewards
    max_steps_per_episode = 100
    #max_steps_per_episode = 10000
    env = gym.make("jlw-snes-v0", datafile="{}/jlw_obs_2021JAN06_new.txt".format(os.getcwd()))  # Create the environment
    env.say_hello(message="howdy y'all")
    env.seed(seed)
    eps = np.finfo(np.float32).eps.item()  # Smallest number such that 1.0 + eps != 1.0
    your_file_path = "{}/jlw_model_saved".format(os.getcwd())
    #run_batch_mode = False
    run_batch_mode = True

    """
    ## Implement Actor Critic network
    This network learns two functions:
    1. Actor: This takes as input the state of our environment and returns a
    probability value for each action in its action space.
    2. Critic: This takes as input the state of our environment and returns
    an estimate of total rewards in the future.
    In our implementation, they share the initial layer.
    """
    """
    num_inputs = 16
    # below, action = np.random.choice(num_actions, p=np.squeeze(action_probs)) fails if we have
    # only 1 action so let's try 20, each one representing a number of keypresses between 0 and 19
    num_actions = 11
    num_hidden = 128
    inputs = layers.Input(shape=(num_inputs,))
    common = layers.Dense(num_hidden, activation="relu")(inputs)
    action = layers.Dense(num_actions, activation="softmax")(common)
    critic = layers.Dense(1)(common)
    model = keras.Model(inputs=inputs, outputs=[action, critic])
    """

    num_inputs  = 16
    num_actions = 20

    # A model based on building blocks from
    # https://keras.io/getting_started/intro_to_keras_for_engineers/
    inputs = keras.Input(shape=(num_inputs))     # num_inputs = 14

    # Create a new node in the graph of layers by calling a layer on this inputs object:
    dense = layers.Dense(64, activation="relu")
    x = dense(inputs)

    # A few more layers to the graph of layers:
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dense(256, activation="relu")(x)
    critic  = layers.Dense(1, name='critic_out')(x)

    # Add a dense classifier on top
    outputs = layers.Dense(num_actions, activation="softmax", name='y_out')(x)
    
    if run_batch_mode:
      model = keras.Model(inputs=inputs, outputs=outputs)
    else:
      model = keras.Model(inputs=inputs, outputs=[outputs, critic])
    print(model.summary())

    # Before fit(), specify an optimizer and a loss function 
    # This is the compile() step:
    model.compile(optimizer=keras.optimizers.RMSprop(learning_rate=1e-3), loss=keras.losses.CategoricalCrossentropy())

    if run_batch_mode:
      # Get the data as Numpy arrays
      x_train, y_train, critic_train, line_num = env.make_batch_data() ##One file for training
      compare_file = "jlw_observations.7FPS.predict-future-keypress-from-current-image.2020-11-22_new.txt"
      x_test, y_test, critic_test, line_numt     = env.make_batch_data(compare_file) ##Another file for testing (Empty means same file)
##      print(f"Len x train {len(x_train)}, len x test {len(x_test)}")
##      print(f"Len y train {len(y_train)}, len y test {len(y_test)}")
##      if len(x_test) > len(x_train):
##        diff_len = abs(len(x_train) - len(x_test))
##        print("Popping elements from x_test to match")
##        for popper in range(diff_len):
##              x_test.pop()
##              y_test.pop()
##              print(f"popping test {popper}")
##      if len(x_test) < len(x_train):
##          diff_len = abs(len(x_train) - len(x_test))
##          print("Popping elements from x_train to match")
##          for popper in range(diff_len):
##              x_train.pop()
##              y_train.pop()
##              print(f"popping train {popper}")

        
      ##needs to reset file pointer, may need to have different test file anyway
      
      #print("x_train ", x_train)
      #print("y_train ", y_train)

      #print("x_test ", x_test)
      #print("y_test ", y_test)
      #print("X train {}\n Y train {}\n critic tr {}\n x te {}\n y te {}\n c te {}\n".format(x_train, y_train, critic_train, x_test, y_test, critic_test))

      # Train the model for 1 epoch from Numpy data
      batch_size = 200
      epochs = 10000
      print("Fit on NumPy data")
      # https://stackoverflow.com/questions/44036971/multiple-outputs-in-keras
      #history = model.fit(x_train, {'y_out': y_train, 'critic_out': critic_train}, batch_size=batch_size, epochs=1000, verbose=0)
      history = model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, verbose=0)
      # # Train the model for 1 epoch using a dataset
      # dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train)).batch(batch_size)
      # print("Fit on Dataset")
      # history = model.fit(dataset, epochs=10)
      #print(f" x_test {x_test},\n y_test {y_test}")
      #print(f" len x_test {len(x_test)},\n len y_test {len(y_test)}")
      #test_scores = model.evaluate(x_test, {'y_out': y_teset, 'critic_out': critic_test}, verbose=2)
      test_scores = model.evaluate(x_test, y_test, verbose=2)
      print(f"test scores for {epochs} epochs: {test_scores}")
      #print(f" x_test {x_test},\n y_test {y_test}")
      generate_predictions(x_test, y_test, model, line_numt)

      model.save(your_file_path, save_format='tf')
      print("Model saved in '{}'".format(your_file_path))
      # # returns a compiled model
      # # identical to the previous one
      # from tensorflow.keras.models import load_model    # for reloading models
      # model = load_model('my_model')

      json_string = model.to_json()
      with open("{}.json".format(your_file_path), "w") as f:
         f.write(json_string)
      # # model reconstruction from JSON:
      # from tensorflow.keras.models import model_from_json
      # model = model_from_json(json_string)
##      prediction = generate_test_predictions(x_test)
##      return prediction
      print("Done batch processing.")


    #
    # Train with dynamic data
    #

    if not run_batch_mode:

      optimizer = keras.optimizers.Adam(learning_rate=0.01)
      huber_loss = keras.losses.Huber()
      action_probs_history = []
      critic_value_history = []
      rewards_history = []
      running_reward = 0
      episode_count = 0

      #print("env: ", env)

      while True:  # Run until solved
        #print("calling reset()...")
        state = env.reset(include_correct=1)
        correct = state.pop()
        #print(" found state: ", state)
        
        episode_reward = 0
        with tf.GradientTape() as tape:
            for timestep in range(1, max_steps_per_episode):
                # env.render(); Adding this line would show the attempts
                # of the agent in a pop up window.

                #print("state: ", state)
                state = tf.convert_to_tensor(state)
                state = tf.expand_dims(state, 0)

                # Predict action probabilities and estimated future rewards
                # from environment state
                action_probs, critic_value = model(state)
                critic_value_history.append(critic_value[0, 0])

                # Sample action from action probability distribution
                #print('num_actions ', num_actions)
                #print('action_probs ', action_probs)
                action = np.random.choice(num_actions, p=np.squeeze(action_probs))
                action_probs_history.append(tf.math.log(action_probs[0, action]))

                # Apply the sampled action in our environment
                state, reward, done, _ = env.step(action, include_correct=1)
                if (timestep % 99 == 0):
                  print("last training timestep {}: action {}, correct {}, reward {}".format(timestep, action, correct, reward))
                correct = state.pop()
                rewards_history.append(reward)
                episode_reward += reward

                if done:
                    break

            # Update running reward to check condition for solving
            running_reward = 0.05 * episode_reward + (1 - 0.05) * running_reward

            # Calculate expected value from rewards
            # - At each timestep what was the total reward received after that timestep
            # - Rewards in the past are discounted by multiplying them with gamma
            # - These are the labels for our critic
            returns = []
            discounted_sum = 0
            for r in rewards_history[::-1]:
                discounted_sum = r + gamma * discounted_sum
                returns.insert(0, discounted_sum)

            # Normalize
            returns = np.array(returns)
            returns = (returns - np.mean(returns)) / (np.std(returns) + eps)
            returns = returns.tolist()

            # Calculating loss values to update our network
            history = zip(action_probs_history, critic_value_history, returns)
            actor_losses = []
            critic_losses = []
            for log_prob, value, ret in history:
                # At this point in history, the critic estimated that we would get a
                # total reward = `value` in the future. We took an action with log probability
                # of `log_prob` and ended up recieving a total reward = `ret`.
                # The actor must be updated so that it predicts an action that leads to
                # high rewards (compared to critic's estimate) with high probability.
                diff = ret - value
                actor_losses.append(-log_prob * diff)  # actor loss

                # The critic must be updated so that it predicts a better estimate of
                # the future rewards.
                critic_losses.append(
                   huber_loss(tf.expand_dims(value, 0), tf.expand_dims(ret, 0))
                )

            # Backpropagation
            loss_value = sum(actor_losses) + sum(critic_losses)
            grads = tape.gradient(loss_value, model.trainable_variables)
            optimizer.apply_gradients(zip(grads, model.trainable_variables))

            # Clear the loss and reward history
            action_probs_history.clear()
            critic_value_history.clear()
            rewards_history.clear()

            # Log details
            episode_count = episode_count + 1

            # save the model (https://keras.io/getting_started/faq/#what-are-my-options-for-saving-models)
            model.save(your_file_path, save_format='tf')
            # # returns a compiled model
            # # identical to the previous one
            # from tensorflow.keras.models import load_model    # for reloading models
            # model = load_model('my_model')
            
            json_string = model.to_json()
            with open("{}.json".format(your_file_path), "w") as f:
                f.write(json_string)
            # # model reconstruction from JSON:
            # from tensorflow.keras.models import model_from_json
            # model = model_from_json(json_string)

            if episode_count % 10 == 0:
                template = "running reward: {:.2f} at episode {}"
                print(template.format(running_reward, episode_count))

            #if running_reward > 195:  # Condition to consider the task solved
            if running_reward > 5000:  # Condition to consider the task solved
                print("Solved at episode {}!".format(episode_count))
                break

    print("Now testing the model...")
##    print(f"State is {state}")
##    print("\nTesting in batch mode\n")
##    state = env.reset(include_correct=0) ##Why is this being called?
##    print(f"State is {state}")
##    x_train, y_train, critic_train, x_test, y_test, critic_test = env.make_batch_data()
    #print("x_test ", x_test)
    #print("y_test ", y_test)
    ##generate_predictions(x_test, y_test, model)
    ##      prediction = generate_test_predictions(x_test)
    ##      return prediction


    print("\nTesting moving forward in time with feed-forward of predicted actions\n")
    
    state = env.reset(include_correct=1)
    print(f"State is {state}")
    correct = state.pop()  # remove the correct answer from the end
    #print(f'Correct starting value {correct}')
    print("Press enter when ready")
    input()
    rms_sum = 0
    N       = 1
    include_correct = 1
    while True:

        state = tf.convert_to_tensor(state)
        state = tf.expand_dims(state, 0)
        #correct = state.pop()
        # Predict action probabilities and estimated future rewards
        # from environment state
        # action_probs, critic_value = model(state)
        if state.shape == (1, 0):
            break
        action_probs = model(state)

        # don't do probabilities when we are trying to get an answer from the NN
        # print ("action_probs", action_probs[0])
        action = find_index_of_max_element(action_probs[0])
        # action = np.random.choice(num_actions, p=np.squeeze(action_probs))
        #  for i in range (0,len(state)):
        #      print("variable {}: input {}, model {}".format(i, diff( state[i]-action[i]), state[i], action[i]))
        #  print("")
        include_correct = 1
        # Apply the sampled action in our environment
        state, reward, done, _ = env.step(action,include_correct) #State is obs
        if type(state) == tuple:
            print(f"State is {state}")
        correct = state.pop()
        #print(f"state {state}, correct {correct}")
        print("correct '{}', predicted '{}', reward '{}, done '{}'.".format(correct, action, reward, done))
        N = N + 1
        print(f'N = {N}')
        rms_sum = rms_sum + (int(correct) - int(action))*(int(correct) - int(action))
        # print("  state: ", state)

        if done:
           break

    print("N {}, sum of squared errors {}".format(N, rms_sum))

