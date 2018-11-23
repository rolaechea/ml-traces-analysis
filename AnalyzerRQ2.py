#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 12:00:41 2018

@author: rafaelolaechea
"""
import sys

#sumTimeTakenPerTransitionFromConfigurationAndRep,

import random

from sklearn.preprocessing import  StandardScaler



from ParseTrace import  loadObjectFromPickle





def print_help():
    """
    Print statements explaining how program is used.
    """
    print("python AnalyzerRQ2.py regressors.pkl testConf.pkl")
    
def check_accuracy_for_overall_time_prediction():
    """
    Check if we can analyze how long will a certain task take based on our counts
    """
    pass

def showTimeTaken(configurationId):
    """
    Given a configuration, list how much it took to execute each one based on two metrics:
        a. Add upp all transitions
        b. JSON file information.        
    """
    
numTracesToPredictOverallTime = 30
    
if __name__ == "__main__":
    if   len(sys.argv) > 2:
        
        regressorInputFilename = sys.argv[1]
        
        testConfFilename = sys.argv[2]                                
        
    else:    
        
        print_help()
        
        exit(0)
    
    regressorsArray = loadObjectFromPickle(regressorInputFilename)
    
    print ("Length of regressorsArray = {0}".format(len(regressorsArray)))
    
    testConfigurationsList = loadObjectFromPickle(testConfFilename)
    
    print ("Length of test Transitions = {0}".format(len(testConfigurationsList)))
    
    
    subsetConfigurationsToCheck = random.sample(testConfigurationsList, numTracesToPredictOverallTime)
    
    for aConfId  in subsetConfigurationsToCheck:
        print ("Evaluating Accuracy on Configuration {0} Repetition {1}".format())
        
        timeTakenDict = sumTimeTakenPerTransitionFromConfigurationAndRep(1, 1)
#        
#    totalTime = sum([timeTakenDict[a][1] for a  in timeTakenDict.keys()])
#    
#    print(timeTakenDict)
#    print (totalTime)
#
#
#    timeTakenDict = sumTimeTakenPerTransitionFromConfigurationAndRep(1, 2)
#    
#    totalTime = sum([timeTakenDict[a][1] for a  in timeTakenDict.keys()])
#    
#    print(timeTakenDict)
#    print (totalTime)
#    

    
#    timeTakenDict = sumTimeTakenPerTransitionFromConfigurationAndRep(100, 1)
#    
#    totalTime = sum([timeTakenDict[a][1] for a  in timeTakenDict.keys()])
#    
#    print(timeTakenDict)
#    print (totalTime)