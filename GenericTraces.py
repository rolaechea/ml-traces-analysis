#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  6 11:42:20 2018

@author: rafaelolaechea
"""

class ExecutionTrace:
    def __init__(self):
        """
        Constructor to represent an execution trace
        """
        
        self.size = 0
        
        self.configurationId = 0
        
        self.lstExecutedTransitions = []
    
    def getSize(self):
    
        return self.size
    
    def setSize(self, size):
        self.size = size 
        
    def setConfigurationId(self, configurationId):
        
        self.configurationId = configurationId

    def getConfigurationId(self):

        return self.configurationId
    
    def getTransitionList(self):

        return self.lstExecutedTransitions
        

class TransitionType():
    def __init__(self, transitionId):
        self.transitionId =  transitionId
    
    def getTransitionId(self):
        return self.transitionId    