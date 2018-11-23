#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 22:05:10 2018

@author: rafaelolaechea
"""
import sys





from ParseTrace import getFilenameFromConfigurationAndRepetition, extractTransitionToBagOfTimesDictionaryFromTraceFile, \
saveObjectToPickleFile, loadObjectFromPickle

from TransitionDictionaryManipulations import conjoinRepetedDictionaries, calculatePerTransitionsCounts, addCountDictionaries, \
downSampleToNewMaxExecutions
#downSampleToNewMaxExecutions

from ConfigurationUtilities import getAllPossibleIds
from sklearn.model_selection import train_test_split
from subprocess import call

temporaryFilenameTemplate = "tmpFile_{0}.pkl"

#trainingSetConfigurations = [81,1383,2044,1913,872,711,171,112,448,195,1232,117,467,25,159,387,1056,1082,2174,1102,1178,1127,1077,548,322,530,1560,207,476,1655,227,687,1868,385,1810,849,1900,1274,1116,839,523,1789,1886,971,260,421,118,1675,1646,401,614,235,1032,1509,1320,1680,2006,1771,1216,295,2196,492,747,1165,1154,2222,2133,1057,237,542,715,1444,1052,2090,197,1199,735,1976,99,2269,1074,2046,2097,491,495,546,1447,1401,2226,1182,1650,972,1473,2260,2205,951,478,1145,283,1282,1368,1991,1272,2034,416,214,609,224,1079,850,1776,2,642,1140,821,758,220,1876,1477,1649,713,1203,352,148,1357,2149,522,2146,234,643,299,142,739,311,2184,453,1221,1236,180,22,1459,1562,30,1523,1065,265,863,1911,2190,1572,1665,604,1076,2272,727,1467,1258,459,1925,1840,901,115,60,1860,2178,2264,447,1851,2130,729,497,1179,305,1667,164,1895,415,388,1910,824,83,465,1626,1440,1978,316,1081,1785,314,1123,1376,967,473,2132,1703,1915,655,738,1042,2259,165,392,1584,1487,408,1247,1442,1327,1693,1623,2183,441,2031,2185,2070,1352,254,1504,354,1831,1075,1713,5,1839,1070,1735,963,1318,431,2066]

if __name__ == "__main__":
    verboseDebug = False
    
    if  len(sys.argv) > 3:
         # First parameter is size of training set, 2nd is name of configurationFile
         TrainingConfSize = int(sys.argv[1])
         TrainingConfFilename = sys.argv[2]
         OutputFilename = sys.argv[3]
         
         if len(sys.argv) > 4 and sys.argv[4] == "debug":
             verboseDebug = True
    else:        
        print(" Incorrect Usage. Requires three parameters: # of configurations in train. size, file to save training set ids, file to save filtered dataset and optional debug parameter")
    
    trainingSetConfigurations = train_test_split(getAllPossibleIds(), getAllPossibleIds(), train_size=TrainingConfSize, test_size=(2304-TrainingConfSize))[0]
   
    
    ConfSerialization =  saveObjectToPickleFile(TrainingConfFilename, trainingSetConfigurations)

    if  verboseDebug:
        print("Memory Information at Program Launch ")
        call(["free", "-h"])

    globalCounts = {}
    for outerPart in range(0, 23):
        transitionArrayOfDictionary = []    

        smallSet = trainingSetConfigurations[outerPart*20:(outerPart*20)+20]

        if verboseDebug:
            print("At subloop {0}, memory status :".format(outerPart))
            call(["free", "-h"])        


        for configurationId in smallSet:

            for repId in range(1,11):            

                traceFilename = getFilenameFromConfigurationAndRepetition(configurationId, repId)

                AllTransitions = extractTransitionToBagOfTimesDictionaryFromTraceFile(traceFilename )

                transitionArrayOfDictionary.append(AllTransitions)

        
        if verboseDebug:
            print("Possible Peak subloop memory at loop  {0}".format(outerPart))
            call(["free", "-h"])
        
        mergedDictionary  = conjoinRepetedDictionaries(transitionArrayOfDictionary)

        transitionArrayOfDictionary = []
        
        if verboseDebug:
            print("Possible Peak subloop memory at loop  {0}".format(outerPart))
            call(["free", "-h"])
                                
        allCounts = calculatePerTransitionsCounts(mergedDictionary)

        print (allCounts)

        addCountDictionaries(globalCounts, allCounts)

        if verboseDebug:
            print("Will save Dict of length = {0}".format(len(mergedDictionary)))
        
        saveObjectToPickleFile(temporaryFilenameTemplate.format(outerPart), mergedDictionary)       

        transitionArrayOfDictionary = [] 
        AllTransitions = []
        mergedDictionary = []
        allCounts = {}
        
        if verboseDebug:
            print("Memory After Clean Up")
            call(["free", "-h"])
    
    if verboseDebug:
        print("Completed")
        print (globalCounts)
    
    if verboseDebug:
        print("Final Memory Before Shutdown")
        call(["free", "-h"])

    GlobalTmpFinalArray = []      
    for outerIndex in range(0, 23):
        if verboseDebug:
            print("Memory Start Loading Loop at {0}".format(outerIndex))
            call(["free", "-h"])         
        
        unsampledMergedDictArray = loadObjectFromPickle(temporaryFilenameTemplate.format(outerPart))
        
        if verboseDebug:
            print("Loading Memory Peak I at {0}".format(outerIndex))
            call(["free", "-h"])        
        
        TmpFinalArrayDict = downSampleToNewMaxExecutions(unsampledMergedDictArray, maxPerTransition=10000, actualCountsDictionary=globalCounts)

        if verboseDebug:
            print("Loading Memory Peak II at {0}".format(outerIndex))
            call(["free", "-h"])
        
        unsampledMergedDictArray = []
        
        GlobalTmpFinalArray.extend(TmpFinalArrayDict)
        
        TmpFinalArrayDict = []
        
        if verboseDebug:
            print("Reloading Memory Final at {0}".format(outerIndex))
            call(["free", "-h"])
    
    if verboseDebug:
         print("Saving Final Dictionary of length {0}".format(len(GlobalTmpFinalArray)))
         
    saveObjectToPickleFile(OutputFilename, GlobalTmpFinalArray)

    

