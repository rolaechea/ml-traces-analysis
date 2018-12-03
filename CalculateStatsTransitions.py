#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 14:57:01 2018

@author: rafaelolaechea
"""
from ParseTrace import getTransitionToBagOfTimesForAllRepsForAProduct, getTestSetSamplingRatiosDict

from TransitionDictionaryManipulations import downSampleSingleDictionary, calculatePerTransitionsCounts

import numpy as np

import pickle

from sklearn.model_selection import train_test_split

if __name__ == "__main__":
    """
    Go through 100 files and calculate Stats of transitions
    """
    conf_listing = train_test_split(range(0,2304), train_size=20, test_size=2304-100)[0]

    Multiplier = 2.0
    ratioDict = getTestSetSamplingRatiosDict()
    
    
    DictionaryArray = []
    
    for confId in conf_listing:
        print("Sampling Conf {0}".format(confId))
        tmpDict = getTransitionToBagOfTimesForAllRepsForAProduct(confId)
        print("Obtained bag for {0} with {1} transitions ".format(confId, tmpDict.keys()))
        sampledDict = downSampleSingleDictionary(tmpDict, ratioDict, Multiplier)            
        print("Done Sampling ")
        DictionaryArray.append(sampledDict)

    outConf = open("smallConf.pkl" , "wb")        
    pickle.dump(conf_listing, outConf)
    outConf.close()

    outConfRaw = open("rawSmallSample.pkl" , "wb")        
    pickle.dump(DictionaryArray, outConfRaw)
    outConfRaw.close()
    
    print (calculatePerTransitionsCounts(DictionaryArray))

    dictMeanPerProductExecution = {}
    for transitionId in ratioDict.keys():
        dictMeanPerProductExecution[transitionId] = {}

    for confDict, confId in zip(DictionaryArray, conf_listing):
       for transitionId in ratioDict.keys():
            if  transitionId in    confDict.keys():
                dictMeanPerProductExecution[transitionId][confId] = np.mean(confDict[transitionId])

    for transitionId in dictMeanPerProductExecution.keys():
        print ("Transitions {0}".format(transitionId))
        for confId in dictMeanPerProductExecution[transitionId].keys():
            print (dictMeanPerProductExecution[transitionId][confId])
    