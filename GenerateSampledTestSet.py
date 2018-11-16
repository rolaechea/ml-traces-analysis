#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 16:46:02 2018

@author: rafaelolaechea
"""

from ParseTrace import getTransitionToBagOfTimesForAllRepsForAProduct, getSamplingRatiosDict

from TransitionDictionaryManipulations import downSampleSingleDictionary, calculatePerTransitionsCounts

import numpy as np
import sys

import pickle

def getComplementSet(confSet, totalEleements=2304):
    complementSet = []
    for x in range(totalEleements):
        if x not in confSet:
            complementSet.append(x)
    return complementSet
        
if __name__ == "__main__":
#    x.py conf_train.pkl  sampled_assesment_pkl  test_conf   
    if   len(sys.argv) > 3:
        
        confTrainFilename = sys.argv[1]        
        
        pkl_file = open(confTrainFilename, 'rb')
    
        confsTrain = pickle.load(pkl_file)        
           
        pkl_file.close()  
                
       
        assesmentConfsFilename = sys.argv[2]
        
        assesmentSampledFilename = sys.argv[3]
        
    else:
        print("Incorrect usage -  requires 3 filenames parameters train conf pkl, and test conf pkl and test conf sampled")
        exit(0)
        
    dictRatios =  getSamplingRatiosDict()
    
    
    confsTest = getComplementSet(confsTrain)

    # Write out test_set
    outputConfsTest = open(assesmentConfsFilename, 'wb')
    
    pickle.dump(confsTest, outputConfsTest, pickle.HIGHEST_PROTOCOL)
    
    outputConfsTest.close()
    

    DictionaryArray = []
    index = 0
    for confId in confsTest:
        if index % 10 == 0:
            print ("Sampled  {0} out of {1}".format(index, len(confsTest)))
            
        tmpDict = getTransitionToBagOfTimesForAllRepsForAProduct(confId)        
        
        sampledDict = downSampleSingleDictionary(tmpDict, dictRatios, 1.111)
        


        DictionaryArray.append(sampledDict)
        
        index = index +1            

    
    # Write out test_samples
    outputSamplesTest = open(assesmentSampledFilename, 'wb')
    
    pickle.dump(DictionaryArray, outputSamplesTest, pickle.HIGHEST_PROTOCOL)
    
    outputSamplesTest.close()
    