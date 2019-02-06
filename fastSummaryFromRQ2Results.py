#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 20:21:28 2019

@author: rafaelolaechea
"""
import pickleFacade

def summarizeTracesX264SpecialFromResults(pklOuptputFilename, baseFilenameTemplate="news/results/rq2_predictions_rep_{0}.csv"):
    """
    Summarize Traces X264 from both results and from reading through traces (for the configurations in the training set)
    
    
    Get Input data for files News and Container.
    """

    dctAllTracesExecutionTimes = {}
    showNextInserts = False
    for testTrainSplit in range(1, 11):
        fdFilename = baseFilenameTemplate.format(testTrainSplit)
        print("Starting openning {0}".format(fdFilename))
        fdAll = open(fdFilename, "r")
        lineIndex = 0        
        
        seenConfigurations = 0
        
        for line in fdAll:
            if lineIndex == 0:
                lineIndex = lineIndex + 1
                continue
            
            splitInParts = line.strip().split(",")
            if lineIndex == 18440  and testTrainSplit == 1: 
                print (splitInParts)
                
            confId, timeTaken = splitInParts[0], splitInParts[1]
            
            if (confId, (seenConfigurations+1)) not in dctAllTracesExecutionTimes.keys():
                seenConfigurations = seenConfigurations + 1
                if showNextInserts:
                    print ("Will insert {0}--{1}".format(confId, seenConfigurations))
                dctAllTracesExecutionTimes[(confId, seenConfigurations)] = timeTaken            
                if seenConfigurations == 10:
                    seenConfigurations = 0
                
            lineIndex = lineIndex + 1            
            if lineIndex == 18441 :                
                break
            
        print ("After full search we have  {0} keys".format(len(dctAllTracesExecutionTimes.keys())))
        
        if len(dctAllTracesExecutionTimes.keys()) >= 23030 :
            showNextInserts = True
    for a,b in dctAllTracesExecutionTimes.keys():
        if (a not in range(0, 2304)) and (b not in range(1, 11)):
            print ("a={0} b={1}".format(a,b))
    
    pickleFacade.saveObjectToPickleFile(pklOuptputFilename, dctAllTracesExecutionTimes)
    
if __name__ == "__main__":
    print ("Started Reading")
    summarizeTracesX264SpecialFromResults("news/traceExecutionTimesForAll.pkl")
    print ("Finished Reading")