#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 11:21:47 2018

@author: rafaelolaechea
"""

import rosbag
import AutonomooseTraces 
from pickleFacade import saveObjectToPickleFile

if __name__ == "__main__":
    subfolder = "traces-November-22nd"
    
    
    dictConfToTraces = {}
    for confId in range(0, 32):
        print "Conf {0}".format(confId)
        for rep in range(0, 10):
            rosbagFilename = "{0}/track_transition_counts-configuration-{1}-repetition-{2}.bag".format(subfolder, confId, rep)
        
            executionTraceBag = rosbag.Bag(rosbagFilename, 'r')

            newTrace = AutonomooseTraces.ExecutionTrace(executionTraceBag)
     
            newTrace.setConfigurationId(confId)
        
            if confId in dictConfToTraces.keys():
                dictConfToTraces[confId].append(newTrace)
            else:
                dictConfToTraces[confId] = [newTrace]
                
#            print "Configuration {0} Size {1}".format(j, newTrace.getSize())
            
            
 #           for i in range(0, len(newTrace.lstExecutedTransitions)):
 #               print newTrace.lstExecutedTransitions[i].__dict__
    print dictConfToTraces.keys()
    
    saveObjectToPickleFile("autonomoose_executions.pkl", dictConfToTraces)