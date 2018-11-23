#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 14:40:06 2018

@author: rafaelolaechea
"""
import math
import random




def extractLinearArrayTimeTakenForSingleTransition(ArrayOfDictTransitionIdsToValueSet, transitionId):
    """
      Input: 
          Param 1    An array of dicionaries of transitions x Count (one per conf.), 
          Param 2    A list of configurations such that len(param_1) = len (param_2)
     Output
         A list of list of time taken (y_1-1 ... y_1n-), (y_2-1, y_2-N) ... corresponding to  time takes from P1(conf_1), P2(conf_2) where conf_i is the ith configuration given in Param 2.
      Assumption
          Users knows that configuration that each element of ArrayOfDictTransitionIdsToValueSet corresponds to. 
          Returned List contains list of lists of times, in same conf. order as ArrayOfDictTransitionIdsToValueSet
    """  
    AllYVals = []
    for dictToValueSet in ArrayOfDictTransitionIdsToValueSet:
        if transitionId in dictToValueSet.keys():
            singleYVal = dictToValueSet[transitionId]
        else:
            singleYVal = []
        AllYVals.append(singleYVal)       
    return AllYVals


def downSampleSingleDictionary(AnInputDictionary, samplingRatios={}, RatioMultiplier=1.0):
    """
    Returns a new dictionary, sampling each transition according to the given sampling ratios multiplied by multiplicator.
    """
    sampledDictionary = {}
    for transitionId in AnInputDictionary.keys():
        if transitionId in samplingRatios.keys():
#            print("Sampling Transitions  {0}".format(transitionId))            
            numExecutions = len(AnInputDictionary[transitionId])
            
            numExecutionsToSample = int(math.ceil(numExecutions*samplingRatios[transitionId]*RatioMultiplier))
            if numExecutionsToSample < numExecutions:
                sampledDictionary[transitionId] = random.sample(AnInputDictionary[transitionId], numExecutionsToSample)
            else:
                sampledDictionary[transitionId] = AnInputDictionary[transitionId]
                
    return sampledDictionary
                


def addCountDictionaries(firstCountDictionary, secondCountDictionary):
    for transitionId in secondCountDictionary.keys():
        if secondCountDictionary in firstCountDictionary.keys():
            firstCountDictionary[transitionId] = firstCountDictionary[transitionId] + secondCountDictionary[transitionId]
        else:
            firstCountDictionary[transitionId] = secondCountDictionary[transitionId]
    
def downSampleToNewMaxExecutions(inputDictionary, maxPerTransition=500000, actualCountsDictionary={}):
    """
    Input: An array of dicionaries of transitions x Count (one per conf.)
    Output: Similary array but dowsnamplig the number of executions such that the sum of executions of  a transition across all configurations <~ maxPerTransition
    """
    newArrayOfDictionaries  = []
    SamplingRatios = {}
    for transitionId in actualCountsDictionary.keys():
        if actualCountsDictionary[transitionId] > maxPerTransition:
            SamplingRatios[transitionId] = maxPerTransition / actualCountsDictionary[transitionId] 
        else:
            SamplingRatios[transitionId] = 1.0
#        print( "For transition {1}, will sample only {0} % of all its executions. ".format(SamplingRatios[transitionId]*100.0, transitionId))             
    
    for perConfDict in inputDictionary:
        sampledPerConfDictionary = {}
        for transitionId in perConfDict.keys():
            numExecutions = len(perConfDict[transitionId])
            numberToSample = int(math.ceil(numExecutions*SamplingRatios[transitionId]))
            
            if sampledPerConfDictionary == 1.0 or numberToSample==numExecutions:
                sampledPerConfDictionary[transitionId] = perConfDict[transitionId] # no sampling at all required
            else:
                sampledPerConfDictionary[transitionId] = random.sample(perConfDict[transitionId], numberToSample)
        newArrayOfDictionaries.append(sampledPerConfDictionary)
    
#            print( "Sampling {0} % of all executed transitions with id = {1}, giving {2} samples out of  {3} ".format(SamplingRatios[transitionId]*100.0, \
#                  transitionId, numberToSample, numExecutions))

    return newArrayOfDictionaries 

def calculatePerTransitionsCounts(inputDicionary):
    """
    Input: An array of dicionaries of transitions x Count.
    Output: Total # of executed transitions per transition
    """
    TransitionCounts = {}
    for dictFile in inputDicionary:
        for transitionId in dictFile.keys():
            if transitionId in TransitionCounts.keys():
                TransitionCounts[transitionId] += len(dictFile[transitionId])
            else: 
                TransitionCounts[transitionId] = len(dictFile[transitionId])
        
    return TransitionCounts
            
def conjoinRepetedDictionaries(inputDicionary):
    """
    Input:    List of Dictionaries for configurations P_1 ... P_N
    Output: List of Dictionaries for P_1' ... P'_N/10 where P_1' = P1 ... P10
    """
    newMergedDicionary = []
    numReptitions = 10
    for i in range(int(len(inputDicionary)/numReptitions)):
        newMergedDicionary.append(inputDicionary[numReptitions*i])
        transitionsSetCurrentDictionary = set(newMergedDicionary[-1].keys()) 
        for j in range(1, numReptitions):
            for newKey in inputDicionary[(numReptitions*i)+j].keys():
                if newKey in transitionsSetCurrentDictionary:
                    newMergedDicionary[-1][newKey] += inputDicionary[(numReptitions*i)+j][newKey]
                else:
                    newMergedDicionary[-1][newKey] = inputDicionary[(numReptitions*i)+j][newKey]
    return newMergedDicionary