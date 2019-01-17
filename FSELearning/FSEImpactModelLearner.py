#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 15:14:39 2018

@author: rafaelolaechea
"""
import MLConstants

from LearningRound import LearningRound

MIN_NUM_ARGUMENTS = 3

def print_help():
    pass

def parseRuntimeParemeters(inputParameters):
    """
    Parse the following parameters:
        Subject System (x264 or Autonomoose)
        Train Data filename
        Train Conf filename    
    Returns parsed values as a tuple.    
    """
    
    if  len(inputParameters) > MIN_NUM_ARGUMENTS:

        SubjectSystem = inputParameters[1]
         
        if SubjectSystem not in MLConstants.lstSubjectSystems:
             
            print ("Subject systems must be one of {0}".format(", ".join(MLConstants.lstSubjectSystems)))
             
            exit()
            
        InputDataFilename = inputParameters[2]
        
        InputConfsFilename = inputParameters[3]
        
    else:    
        
        print_help()
        
        exit(0) 
        
    return SubjectSystem,   InputDataFilename, InputConfsFilename




if __name__ == "__main__":
    """
    Learn a linear regression model from a learning set of configurations
    Possible subject systems: X264 and Autonomoose.
    
    
    Load data from train set.
    
    Generate Candidate Functions.
    
    """
    pass