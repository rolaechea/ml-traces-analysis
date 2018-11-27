#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 16:46:02 2018

@author: rafaelolaechea
"""

from pickleFacade import loadObjectFromPickle, saveObjectToPickleFile

from ParseTrace import getTransitionToBagOfTimesForAllRepsForAProduct, getTestSetSamplingRatiosDict

from TransitionDictionaryManipulations import downSampleSingleDictionary


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
    useDifferentialSamplingExtra = False
    useDifferentialSampling = False

    if   len(sys.argv) > 3:
        
        confTrainFilename = sys.argv[1]        
        
        pkl_file = open(confTrainFilename, 'rb')
    
        confsTrain = pickle.load(pkl_file)        
           
        pkl_file.close()                  
       
        assesmentConfsFilename = sys.argv[2]
        
        assesmentSampledFilename = sys.argv[3]
        
        if len(sys.argv) > 4:
            
            useDifferentialSampling = True
            
            preExistingSampledConfsFilename = sys.argv[4]
            
            preExistingSampledDatasetFilename =  sys.argv[5]

        if len(sys.argv) > 6:
            useDifferentialSamplingExtra = True

            preExistingSampledConfsFilenameExtra = sys.argv[6]

            preExistingSampledDatasetFilenameExtra =  sys.argv[7]        
    else:
        print("Incorrect usage -  requires 3 filenames parameters train conf pkl, and test conf pkl and test conf sampled, with optional 2 (or 4)  more for differential sampling")
        exit(0)
        
    dictRatios = getTestSetSamplingRatiosDict()
        
    confsTest = getComplementSet(confsTrain)

    saveObjectToPickleFile(assesmentConfsFilename, confsTest)
    
    if useDifferentialSampling:
        
        ConfsAleadySampled = loadObjectFromPickle(preExistingSampledConfsFilename)
        
        DatasetAlreadySampled = loadObjectFromPickle(preExistingSampledDatasetFilename)
    
    if useDifferentialSamplingExtra:

        ConfsAleadySampledExtra = loadObjectFromPickle(preExistingSampledConfsFilenameExtra)

        DatasetAlreadySampledExtra = loadObjectFromPickle(preExistingSampledDatasetFilenameExtra)    

    DictionaryArray = []
    counter = 0
    for confId in confsTest:
        if counter % 10 == 0:
            print ("Sampling  {0} out of {1}".format(counter, len(confsTest)))
            
        if (useDifferentialSampling and confId in ConfsAleadySampled):
            
            indexOfConfid = ConfsAleadySampled.index(confId)
            
            DictionaryArray.append(DatasetAlreadySampled[indexOfConfid])

        elif  (useDifferentialSamplingExtra and confId in ConfsAleadySampledExtra):

            indexOfConfid = ConfsAleadySampledExtra.index(confId)

            DictionaryArray.append(DatasetAlreadySampledExtra[indexOfConfid])
            
        else:

            tmpDict = getTransitionToBagOfTimesForAllRepsForAProduct(confId)        
        
            sampledDict = downSampleSingleDictionary(tmpDict, dictRatios)
        
            DictionaryArray.append(sampledDict)
        
        counter = counter +1            

    saveObjectToPickleFile(assesmentSampledFilename, DictionaryArray)
    

    
