#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 22:05:10 2018

@author: rafaelolaechea
"""
import sys
import pickle
import datetime



from ParseTrace import getFilenameFromConfigurationAndRepetition, extractTransitionToBagOfTimesDictionaryFromTraceFile

from TransitionDictionaryManipulations import conjoinRepetedDictionaries, calculatePerTransitionsCounts, \
downSampleToNewMaxExecutions

from ConfigurationUtilities import getAllPossibleIds
from sklearn.model_selection import train_test_split
from subprocess import call


#trainingSetConfigurations = [81,1383,2044,1913,872,711,171,112,448,195,1232,117,467,25,159,387,1056,1082,2174,1102,1178,1127,1077,548,322,530,1560,207,476,1655,227,687,1868,385,1810,849,1900,1274,1116,839,523,1789,1886,971,260,421,118,1675,1646,401,614,235,1032,1509,1320,1680,2006,1771,1216,295,2196,492,747,1165,1154,2222,2133,1057,237,542,715,1444,1052,2090,197,1199,735,1976,99,2269,1074,2046,2097,491,495,546,1447,1401,2226,1182,1650,972,1473,2260,2205,951,478,1145,283,1282,1368,1991,1272,2034,416,214,609,224,1079,850,1776,2,642,1140,821,758,220,1876,1477,1649,713,1203,352,148,1357,2149,522,2146,234,643,299,142,739,311,2184,453,1221,1236,180,22,1459,1562,30,1523,1065,265,863,1911,2190,1572,1665,604,1076,2272,727,1467,1258,459,1925,1840,901,115,60,1860,2178,2264,447,1851,2130,729,497,1179,305,1667,164,1895,415,388,1910,824,83,465,1626,1440,1978,316,1081,1785,314,1123,1376,967,473,2132,1703,1915,655,738,1042,2259,165,392,1584,1487,408,1247,1442,1327,1693,1623,2183,441,2031,2185,2070,1352,254,1504,354,1831,1075,1713,5,1839,1070,1735,963,1318,431,2066]

if __name__ == "__main__":
    
    if  len(sys.argv) > 3:
         # First parameter is size of training set, 2nd is name of configurationFile
         TrainingConfSize = int(sys.argv[1])
         TrainingConfFilename = sys.argv[2]
         OutputFilename = sys.argv[3]
    else:        
        TrainingConfSize = 230
        TrainingConfFilename = "configurationsListing.pkl"
        OutputFilename = "FilteredAndSampledTransitions.pkl"
    
    trainingSetConfigurations = train_test_split(getAllPossibleIds(), getAllPossibleIds(), train_size=TrainingConfSize, test_size=(2304-TrainingConfSize))[0]
    

    
    ConfSerialization = open(TrainingConfFilename, 'wb')
    pickle.dump(trainingSetConfigurations, ConfSerialization, pickle.HIGHEST_PROTOCOL)
    ConfSerialization.close()
    
    # Extract all transitions
    call(["free", "-h"])
    print("Start Loop ")
#    print(datetime.datetime.now().time())


    for outerPart in range(0, 3):
        transitionArrayOfDictionary = []    

        smallSet = trainingSetConfigurations[outerPart*20:(outerPart*20)+20]

        print("Starting Loop {0} with memory:".format(outerPart))
        call(["free", "-h"])        
        print ("Saving {0}".format(smallSet))

        for configurationId in smallSet[0:20]:
            loopCountT = 0
            for repId in range(1,11):            
                traceFilename = getFilenameFromConfigurationAndRepetition(configurationId, repId)

#                if (repId == 1) and  ((loopCountT % 1) == 0):                
#                    print("Parsing Configuration {0} repetition {1} trace Filename {2} {3}".format(configurationId, repId, traceFilename, loopCountT))
#                    print(datetime.datetime.now().time())
#                    call(["free", "-h"])
                AllTransitions = extractTransitionToBagOfTimesDictionaryFromTraceFile(traceFilename )

                transitionArrayOfDictionary.append(AllTransitions)
            loopCountT = loopCountT + 1
        
#        print("Merging Dictionaries part {0}".format(outerPart))

        print("Possible Peak Memory part {0}".format(outerPart))
        call(["free", "-h"])
        print ("Will Conjoin ")
        
        mergedDicionary  = conjoinRepetedDictionaries(transitionArrayOfDictionary)

        print("Other Possible Peak after merging")
        call(["free", "-h"])
                        
        
        allCounts = calculatePerTransitionsCounts(mergedDicionary)

        print (allCounts)

        saveObjectToPickleFile("tmpFile_{0}.pkl".format(outerPart), mergedDictionary)       

        transitionArrayOfDictionary = []
        AllTransitions = []
        mergedDicionary = []

        print("Memory After Clean Up")
        call(["free", "-h"])
        
#    print("downsampling")

#    print(datetime.datetime.now().time())
    
#    finalArrayDict = downSampleToNewMaxExecutions(mergedDicionary, actualCountsDictionary=allCounts)

#    print("saving")
    
#   print(datetime.datetime.now().time())

#    output = open(OutputFilename, 'wb')
#    pickle.dump(finalArrayDict, output, pickle.HIGHEST_PROTOCOL)
#    pickle.dump(mergedDictionary, output, pickle.HIGHEST_PROTOCOL)    
#    output.close()
    
    

