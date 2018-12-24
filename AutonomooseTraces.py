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
enumDynamicObjectTransition = 4
enumOccupancyTransition = 5
enumBehaviourPlannerTransition = 6
enumLocalPlannerTransition = 7

__dict_TransitionClassNameToId__ = {"LocalizerCompletion" : 1, "WaypointsCollectionCompletion" : 2, "MapServerCompletion": 3, "DynamicObjectTrackingCompletion": 4, \
                                    "OccupancyCompletion":5, "BehaviorPlannerCompletion":6, "LocalPlannerCompletion":7}


ListNoSubTransitions = frozenset([enumLocalizerTransition, enumWaypointsCollectionTransition])


ListMandatoryTransitions = frozenset([enumLocalizerTransition, enumMapServerTransition, enumOccupancyTransition, enumBehaviourPlannerTransition, enumLocalPlannerTransition])

dctConfToBitsetAutonomoose = {}

def generateBitsetForOneConfigurationAutonomoose(configurationId):
    """
    Generates a bitset of features (0/1) from a configuration id for Autonomoose.
    
    Features are listed in the following order:
        Behavior Planner
        Occupancy or Mockupancy Planner
        Waypoints Collection
        Dyn. Object Tracking
        Dyn. Car Tracking.
        Dyn. Person Tracking
        
    Perf. Optimization -- Caching
    
    """
    
    if configurationId in dctConfToBitsetAutonomoose.keys():
       return  dctConfToBitsetAutonomoose[configurationId]
   
    bitmapIndex = []
    BooleanOptions = [("BEHAVIOR", 4 ), \
                      ("OCCUPANCY", 2),
                      ("WAYPOINTS", 1)]

    i = configurationId - (int(configurationId/8)*8)

    for (name, divisor) in BooleanOptions:
        if int(i/divisor) > 0:
            bitmapIndex.append(1)
        else:
            bitmapIndex.append(0)        
        subtractValue = int(i/divisor)*divisor
        i = i - subtractValue

    dynamicCompletionIndex = int(configurationId/8)
    
    if dynamicCompletionIndex == 0:
        bitmapIndex.append(0)  #  active_dynamic_object_tracking == false
        bitmapIndex.append(0)  #  active_avod_bb_car  == false
        bitmapIndex.append(0)  #  active_avod_bb_person  == false                              
    elif dynamicCompletionIndex == 1:
        bitmapIndex.append(1)  #  active_dynamic_object_tracking == true
        bitmapIndex.append(0)  #  active_avod_bb_car  == false        
        bitmapIndex.append(1)  #  active_avod_bb_person  == true 
    elif dynamicCompletionIndex == 2:
        bitmapIndex.append(1)  #  active_dynamic_object_tracking == true  
        bitmapIndex.append(1)  #  active_avod_bb_car  == true
        bitmapIndex.append(0)  #  active_avod_bb_person  == false                             
    else:
        bitmapIndex.append(1) #  active_dynamic_object_tracking == true  
        bitmapIndex.append(1) #  active_avod_bb_car  == true
        bitmapIndex.append(1) #  active_avod_bb_person  == true
        # dynamicCompletionIndex == 3:

    dctConfToBitsetAutonomoose[configurationId] = bitmapIndex
    
    return bitmapIndex
    


def IsRealTransitionForGivenConf(transitionId, ConfigurationId):
#   TODO  -- Filter out 'dummy transitions' --- should be done when reading input.    
#   'Dummy' transitions should take 0 time and/or be ignored. 
    
    if transitionId in ListMandatoryTransitions:
        return True
    else:
        if enumWaypointsCollectionTransition == transitionId:
            # Waypoints Collection on ?                        
            return generateBitsetForOneConfigurationAutonomoose(ConfigurationId)[2] == 1           
        else:
            # DynamicObjectTracking on ?            
            return generateBitsetForOneConfigurationAutonomoose(ConfigurationId)[3] == 1

        # depends if we are on waypoints collection or DynamicObjectTracking transition.


def getOverallRealTimeForASingleTraceAutonomoose(AutonomooseTrace, ConfigurationId):
    """
    Iterates through all non dummy transitions and adds up execution times
    
    Input: A autonomoose Execution Trace.
    """
    tmpTransList = AutonomooseTrace.getTransitionList()

    
    AccumulatedTime = 0.0
    for anAutonomooseTransition in tmpTransList:
        if IsRealTransitionForGivenConf(anAutonomooseTransition.getTransitionId(),ConfigurationId):
            AccumulatedTime = AccumulatedTime + anAutonomooseTransition.getTimeTaken()
#    for aTrans in tmpTransList:
#        print ( dir(AutonomooseTrace))
    return AccumulatedTime


def getSetOfExecutionTimesAutonomoose(transitionData, transitionId, trainingSetConfigurations):
    """
    Inputs: transitionData -- Array of dicts transitions ids to executed Transition Objects of length N.
    Ouputs: array of lists of executed transition times -- of lenth N.
    
 
    """
    retArrayExecutionTimes = []
    
    i = 0
    for dctIdToExecutedTransitions in transitionData:
#        print ("Conf {0} -- is -- {1} ".format(i,trainingSetConfigurations[i]))

        tmpLocalDictTimes = []
        if ((transitionId) in  dctIdToExecutedTransitions.keys()) and IsRealTransitionForGivenConf(transitionId, trainingSetConfigurations[i]):
            tmpLocalDictTimes = [x.getTimeTaken() for x in dctIdToExecutedTransitions[transitionId]]
            retArrayExecutionTimes.append(tmpLocalDictTimes)
        else:
            retArrayExecutionTimes.append(tmpLocalDictTimes)
        i = i+1
        
    return retArrayExecutionTimes

            
def getListOfAvailableTransitionsAutonomoose(transitionData):
    """
    Iterate through transition data to obtain a list of available transitions.
    """    
    setTransitionIds = set()
    for dctIdToExecutedTransitions in transitionData:
        for tmpKey in dctIdToExecutedTransitions.keys():
            setTransitionIds.add(tmpKey)

    return list(setTransitionIds)

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
        

    def getPerTransitionCounts(self):
        """
        Returns a dictionary of number of times each transition has been executed on current trace.
        Only includes -- real transitions -- (non dummy)
        """
        transitionsCounts = {}
        
        for aTransition in self.getTransitionList():
            if IsRealTransitionForGivenConf(aTransition.getTransitionId(), self.getConfigurationId()):                
                if aTransition.getTransitionId() in transitionsCounts.keys():
                    transitionsCounts[aTransition.getTransitionId()] = transitionsCounts[aTransition.getTransitionId()] + 1.0
                else:
                    transitionsCounts[aTransition.getTransitionId()] = 1.0
        return transitionsCounts

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
                
    def addExecutedTransitionsToDictionary(self, dctExecutedTransitions):
        """
        Adss into a dictionary a list of executed transitions.
        """
        for executedTransition in self.lstExecutedTransitions:
            if executedTransition.getTransitionId() in dctExecutedTransitions.keys():
                dctExecutedTransitions[executedTransition.getTransitionId()].append(executedTransition)
            else:
                dctExecutedTransitions[executedTransition.getTransitionId()] = [executedTransition]
        
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

    


