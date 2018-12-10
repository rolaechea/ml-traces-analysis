#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 10:56:25 2018

@author: rafaelolaechea
"""

from GenericTraces import ExecutionTrace, TransitionType

enumLocalizerTransition = 1
enumWaypointsCollectionTransition = 2
enumMapServerTransition = 3

__dict_TransitionClassNameToId__ = {"LocalizerCompletion" : 1, "WaypointsCollectionCompletion" : 2, "MapServerCompletion": 3, "DynamicObjectTrackingCompletion": 4, \
                                    "OccupancyCompletion":5, "BehaviorPlannerCompletion":6, "LocalPlannerCompletion":7}

ListNoSubTransitions = frozenset([enumLocalizerTransition, enumWaypointsCollectionTransition])


def decodeMessageClassName(classObject):
    """
    Returns the name of an anm_msg object, which is  normally  a transition.
    """
    prefixAnmMsg = "_anm_msgs__"
    clsNameEndMarker = "\'"
    
    startIndexTransitionName = str(classObject).find(prefixAnmMsg)+ len(prefixAnmMsg)
    
    endIndexTransitionName = str(classObject)[startIndexTransitionName:].find(clsNameEndMarker) + startIndexTransitionName
    
    strTransitionName = str(classObject)[startIndexTransitionName:endIndexTransitionName]
    
    return strTransitionName
    
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
        

    def setStartSystem(self, indexId):
        """
        Sets the start system index, such that All transitions with offset < startSystemIndex were sent before the system message.
        Transition with index = startSystemIndex was sent right after system message
        
        Note: startSystemIndex should always be equal to zero (i.e. first message)        
        """
        
        self.startSystemIndex = indexId
        
        #print(self.startSystemIndex)

    def parseExecutedTransitions(self, traceBag):
        
        self.lstExecutedTransitions = []
        

        for aMsg in traceBag.read_messages():
            if 'loop_id' in dir(aMsg.message):
                newExecutedTransition = ExecutedTransitionAutonomoose(aMsg.message)
                
                self.lstExecutedTransitions.append(newExecutedTransition)
                #print(len(self.lstExecutedTransitions))
                
            elif 'ST_OFF'  in dir(aMsg.message):             
                self.setStartSystem(len(self.lstExecutedTransitions))

class TransitionTypeAutonomoose(TransitionType):
    allTransitionTypes = []
    
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
        
        tmpTransitionName = decodeMessageClassName(transitionRosMessage.__class__)

        self.isAutonomooseStart = False
        
        self.loopId =  transitionRosMessage.loop_id
        
        self.timeTaken = transitionRosMessage.transition_time_taken
       
        if tmpTransitionName in __dict_TransitionClassNameToId__.keys():

            self.coarseTransitionId = __dict_TransitionClassNameToId__[tmpTransitionName]            

            self.fineTransitionId = self.parseFineTransitionId(transitionRosMessage)
    
            self.transitionId = self.calculateTransitionId()
            
        else:
            raise Exception("Unknown Transition encountered")

        self.isDummy = False
        
    def calculateTransitionId(self):
        """
        Calculate Unique Id based on Transition Ids (Coarse/Fine)
        """
        return self.coarseTransitionId
    
    def parseFineTransitionId(self, transitionRosMessage):
        """
        Code to parse the fine grained transition id from a ROS message.
        """
        if self.coarseTransitionId in ListNoSubTransitions:            
            tmpRetId = -1
        else:
            tmpRetId = 0
            
        return tmpRetId
    
    def setIsDummyTransition(self, isDummy):
        
        self.isDummy = isDummy
        
    def isDummyTranstion(self):
    
        return self.isDummy
    
    def getTimeTaken(self):
        
        return self.timeTaken
    
    def getLoopId(self):
        
        return self.loopId
        
    def getTransitionId(self):
        
        return  self.transitionId
    
    def getCoarseTransitionId(self):
        
        return self.coarseTransitionId
    
    def getFineTransitionId(self):

        return self.fineTransitionId

    


