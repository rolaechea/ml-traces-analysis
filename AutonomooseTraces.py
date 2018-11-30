#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 10:56:25 2018

@author: rafaelolaechea
"""

__dict_TransitionClassNameToId__ = {"LocalizerCompletion" : 1, "WaypointsCollectionCompletion" : 2, "MapServerCompletion": 3, "DynamicObjectTrackingCompletion": 4, \
                                    "OccupancyCompletion":5, "BehaviorPlannerCompletion":6, "LocalPlannerCompletion":7}

class LearnFromTraces:
    
    def __init__(self, learnerType):
        """
         [x.getYValue() for x in q[0][1].lstExecutedTransitions if x.getTransitionId() == 1]
        """
        pass
    


class ExecutionTrace:    
    def __init__(self, traceBag):
        
        self.parseExecutedTransitions(traceBag)
        
        self.size = len(self.lstExecutedTransitions)
        
    def getSize(self):
        
        return self.size
    
    def setConfigurationId(self, configurationId):
        
        self.configurationId = configurationId

    def getConfigurationId(self):

        return self.configurationId
    
    def getTransitionList(self):

        return self.lstExecutedTransitions
    
    def parseExecutedTransitions(self, traceBag):
        
        self.lstExecutedTransitions = []
        
        for aMsg in traceBag.read_messages():
            if 'loop_id' in dir(aMsg.message):
                newExecutedTransition = ExecutedTransition(aMsg.message)
                self.lstExecutedTransitions.append(newExecutedTransition)
                
                
class ExecutedTransition:
    
    def __init__(self, transitionRosMessage):
        
        self.transitionName = self.decodeMessageClassName(transitionRosMessage.__class__)

        self.loop_id =  transitionRosMessage.loop_id
        
        self.time_taken = transitionRosMessage.transition_time_taken
       
        if self.transitionName in __dict_TransitionClassNameToId__.keys():

            self.transitionId = __dict_TransitionClassNameToId__[self.transitionName]            

            self.globalTransitionId = self.calculateGlobalTransitionId(transitionRosMessage)
    
        else:
            self.transitionId = -1
    
    def calculateGlobalTransitionId(self, transitionRosMessage):
    
        return self.transitionId
    
    def isDummyTranstion(self):
    
        return False
    
    def decodeMessageClassName(self, classObject):
        """
        Returns the name of class containing transition 
        """
        prefixAnmMsg = "_anm_msgs__"
        clsNameEndMarker = "\'"
        
        startIndexTransitionName = str(classObject).find(prefixAnmMsg)+ len(prefixAnmMsg)
        
        endIndexTransitionName = str(classObject)[startIndexTransitionName:].find(clsNameEndMarker) + startIndexTransitionName
        
        strTransitionName = str(classObject)[startIndexTransitionName:endIndexTransitionName]
        
        return strTransitionName
    
    def getGlobalTransitionId(self):
        return self.globalTransitionId
    
    def getTransitionId(self):
        
        return self.transitionId
    
    def getTransitionName(self):
    
        return self.transitionName
    
    def getYValue(self):
        return self.time_taken
    