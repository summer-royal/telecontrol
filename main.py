main.py

Details

Activity

Approvals


""" 
The main controller for our project. 
"""

#Include import statements!
import process
import cipher
import collect
import execute

import time
import numpy as np
import concurrent
import threading #This may not be correct, we need to analyze signals as they come in

class Project(object):
    def __init__(self):
        self.recorder = [] # it will be a history of 1/0 given timestamps - from this we can get a percentage
        self._lock = threading.Lock() # initialize lock 
        self.prev_command = None # most recent command actually delivered
        self.ratio = 0.9 # ratio of commands in self.recorder required to trigger a switch
        self.time_in_ms = 25


    def store_recorder(self, processx, diff_EEG):
        '''
        decipher command from EEG time window, 
        store one second of prior commands in recorder,
        return current command        
        '''

        command = processx.deCipher(diff_EEG) # decipher command
        self.recorder.append(command) # append most recent commands
        self.recorder = self.recorder[prev_second:] # save rolling window of previous n commands
        return command


    def locked_update(self, board1, processx, robot1):
        '''
        alternate sampling and commanding between two threads,
        pull data/command from already streaming board objects,
        issue robot command if current command window reaches some threshold ratio,
        impose some refractory period between newly issued commands

        NOTE: MVP intensity-based command result instead of binary... TBD
        '''

        # record while another thread has a lock; store data within class
        while not self._lock.acquire():
            diff_EEG = collect.readEEG(board1, self.time_in_ms) # pull last time_in_ms * sample rate from stream
            command = self.store_recorder(self, processx, diff_EEG)
            self._lock.acquire(blocking = False) # attempt to claim lock
            time.sleep(sampling_delay) # time delay between samplings (if needed)

        # lock released from other thread; lock claimed in this thread
        # send command if > ratio of previous second is command and previous command was different
        if len(self.recorder.index(command)) > len(self.recorder) * self.ratio and self.prev_command != command:
            self.prev_command = command
            robot1.action(command) # issue command
            time.sleep(command_delay) # wait time between issuing new commands (imposed refractory period)

        self._lock.release() # unlock current thread


def main():
    blackbox = Project()
    processx = process.Process()
    robot1 = execute.LightsCamera() #multiple robots could be run here
    board1 = collect.streamEEG() # begin streaming EEG data, return object producing current stream
    
    while(True):
        # two threads alternate locking: lock one during process/execute; have other continue recording
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(blackbox.locked_update, board1, processx, robot1)

if __name__ == "__main__":
    main()
