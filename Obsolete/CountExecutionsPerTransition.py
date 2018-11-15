#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 09:53:44 2018

@author: rafaelolaechea
"""
import sys
import numpy as np

from ConfigurationUtilities import getAllPossibleIds
from sklearn.model_selection import train_test_split


from ParseTrace import  getArrayOfDictTransitionIdsToValueSet

if __name__ == "__main__":
    """
    Objective: Count the number of executed transitions for each transition in a training set.
    Input Parameter: <number> size of the training set in terms of # of products.
    Output Parameter: CSV Listing of Transitions #, # of Total Transitions Executed,  # of Products that include that transitions, Average # Executions per Product that includes,  Std. Dev # of Executions Product that Include it. 
    """    

    # Read command line parameters
    if  len(sys.argv) > 1:
         # First parameter is size of training set
         TrainingConfSize = int(sys.argv[1])
    else:        
        TrainingConfSize = 32
        
    TraininingSetConfigruationIds = train_test_split(getAllPossibleIds(), getAllPossibleIds(), train_size=TrainingConfSize, test_size=(2304-TrainingConfSize))[0]
    
    ArrayOfDictTransitionIdsToValueSet = getArrayOfDictTransitionIdsToValueSet(TraininingSetConfigruationIds)
    
    print ("Transitions Id, # of Total Execution,  # of Products that include that transitions, Average # Executions per Product that includes,  Std. Dev # of Executions Product that Include it")

    for transitionId in range(2, 35):
        AllYVals = []
        confLoopIndex = 0
        for configurationId in TraininingSetConfigruationIds:
            if transitionId in ArrayOfDictTransitionIdsToValueSet[confLoopIndex].keys():
                AllYVals.append(ArrayOfDictTransitionIdsToValueSet[confLoopIndex][transitionId])
            else:
                AllYVals.append([])
            confLoopIndex = confLoopIndex +1
        
        totalExecutions = sum([len(a) for a in AllYVals])
      
        configurationsWithTransitions = sum([1 if (len(a) > 0) else 0 for a in AllYVals]) 
        
        if configurationsWithTransitions > 0:
            AverageTransitionsPerfConf = totalExecutions / configurationsWithTransitions        

            stdDevTransitionsPerConf = np.std(list(filter(lambda x: x > 0, [len(a) for a in AllYVals])))
        else:
            AverageTransitionsPerfConf = 0
            
            stdDevTransitionsPerConf = 0
            
        # Print info for transition
        
        print("{}, \t {:>12}, \t {:>12}, \t {:>12}, \t\t {:.2f}".format(transitionId, totalExecutions, configurationsWithTransitions, AverageTransitionsPerfConf, stdDevTransitionsPerConf ))