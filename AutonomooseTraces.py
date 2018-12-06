#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 10:56:25 2018

@author: rafaelolaechea
"""

from GenericTraces import ExecutionTrace, TransitionType

__dict_TransitionClassNameToId__ = {"LocalizerCompletion" : 1, "WaypointsCollectionCompletion" : 2, "MapServerCompletion": 3, "DynamicObjectTrackingCompletion": 4, \
                                    "OccupancyCompletion":5, "BehaviorPlannerCompletion":6, "LocalPlannerCompletion":7}

class LearnFromTraces(object):
    
    def __init__(self, learnerType):
        """
         [x.getYValue() for x in q[0][1].lstExecutedTransitions if x.getTransitionId() == 1]
        """
        pass
    



class ExecutionTraceAutonomoose(ExecutionTrace):    
    def __init__(self, traceBag, configurationId):
        
        super(ExecutionTraceAutonomoose, self).__init__()
        
        self.configurationId = configurationId
        
        self.parseExecutedTransitions(traceBag)
        
        self.setSize(len(self.lstExecutedTransitions))
        

    def parseExecutedTransitions(self, traceBag):
        
        self.lstExecutedTransitions = []
        
        for aMsg in traceBag.read_messages():
            if 'loop_id' in dir(aMsg.message):
                newExecutedTransition = ExecutedTransitionAutonomoose(aMsg.message)
                self.lstExecutedTransitions.append(newExecutedTransition)
                

class TransitionTypeAutonomoose(TransitionType):
    def __init__(self, transitionId, transitionName):

        super(TransitionTypeAutonomoose, self).__int__(self, transitionId)
        
        self.transitionName =     transitionName
        self.globalTransitionId = -1
        
    def getGlobalTransitionId(self):
        return self.globalTransitionId
    
    def getTransitionName():
        return ""        
        
    def isDummy():
        return False
        
                
class ExecutedTransitionAutonomoose(object):
    
    def __init__(self, transitionRosMessage):
        
        self.transitionName = self.decodeMessageClassName(transitionRosMessage.__class__)

        self.loopId =  transitionRosMessage.loop_id
        
        self.timeTaken = transitionRosMessage.transition_time_taken
       
        if self.transitionName in __dict_TransitionClassNameToId__.keys():

            self.transitionId = __dict_TransitionClassNameToId__[self.transitionName]            

            self.globalTransitionId = self.calculateGlobalTransitionId(transitionRosMessage)
    
        else:
            self.transitionId = -1

        self.isDummy = False
        
    def calculateGlobalTransitionId(self, transitionRosMessage):
    
        return self.transitionId
    
    def setIsDummyTransition(self, isDummy):
        
        self.isDummy = isDummy
        
    def isDummyTranstion(self):
    
        return self.isDummy
    
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
    
    def getTimeTaken(self):
        
        return self.timeTaken
    
    def getLoopId(self):
        
        return self.loopId
    
    
    def getTransitionId(self):
        
        return  self.transitionId  #self.transitionType.getTransitionId()
    
    def getTransitionName(self):
    
        return self.transitionName #self.self.transitionType.getTransitionName()
    


