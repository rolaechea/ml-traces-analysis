#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 11:21:47 2018

@author: rafaelolaechea
"""
import sys

import rosbag

import AutonomooseTraces 
from pickleFacade import saveObjectToPickleFile

if __name__ == "__main__":
    """
    Must execute in python2, as ROSBAAGS are only compatible with python 2.
    """
    if len(sys.argv) > 2:
        
        InputFolder = sys.argv[0]
        
        OutputFilename = sys.argv[1]        
        
    else:
        print ("Requires two arguments: source folder with traces, and filename to store pkl of traces.") 
        
        exit()
    
    dictConfToTraces = {}
    
    for confId in range(0, 32):
        print ("Conf {0}".format(confId))
        for rep in range(0, 10):
            rosbagFilename = "{0}track_transition_counts-configuration-{1}-repetition-{2}.bag".format(InputFolder, confId, rep)
        
            executionTraceBag = rosbag.Bag(rosbagFilename, 'r')

            newTrace = AutonomooseTraces.ExecutionTraceAutonomoose(executionTraceBag, confId)
        
            if confId in dictConfToTraces.keys():
                dictConfToTraces[confId].append(newTrace)
            else:
                dictConfToTraces[confId] = [newTrace]
                    
    print (dictConfToTraces.keys())
    
    saveObjectToPickleFile(OutputFilename, dictConfToTraces)