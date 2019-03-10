#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 18:50:39 2019

@author: rafaelolaechea
"""
import sys

from ConfigurationUtilities import mean_absolute_error_and_stdev

resultsFilePattern = "rq2_predictions_rep_{0}.csv"

def collectRQ2ResultsForADirectory(directoryName, traceId=1):
    """
    Iterate through all results in a directory, calculate averages and prints them.
    """
    
    numLines = 0    
    for repIndex in range(1, 11):
        fd = open(directoryName + resultsFilePattern.format(repIndex), "r")
        

        
        lstConfigurationIds = []
        lstCurrentExecutionTimes = []
        lstCurrentPredictedTimes = []
        firstLine = True
        
        for line in fd:
            # Skip the first line
            if firstLine == True:
                firstLine = False
                continue
                        
            # Skip colofon
            if line.startswith("Mean_"):
                break

            tmpConfigurationId, tmpExecutionTime, tmpPredictedTime,   = line.split(",")
            
            lstConfigurationIds.append(int(tmpConfigurationId))
            
            lstCurrentExecutionTimes.append(float(tmpExecutionTime))            
            
            lstCurrentPredictedTimes.append(float(tmpPredictedTime))
            
            numLines = numLines + 1                
        
        meanMAE, stdMAE = mean_absolute_error_and_stdev (lstCurrentExecutionTimes, lstCurrentPredictedTimes)
        
        averageY = sum(lstCurrentExecutionTimes)/len(lstCurrentExecutionTimes)
        

        print("{0},{1},{2},{3},{4},{5}%,{6}%".format(traceId,repIndex,meanMAE,stdMAE, averageY, (100*meanMAE/averageY), (100*stdMAE/averageY)))
        fd.close()
        
        
    

if __name__ == "__main__":
   """
   Collect all results for rq2 and generate single CSV file containing output.    
    
   Parameters (list of folders where case studies are located)
    
   """
   
   lstDirectories = []
   
   if  not( len(sys.argv) > 1):
       print ("At least one parameter is required. Parameters are list of folders in which to look for rq2 results csv")
   else:
       for i in range(1, len(sys.argv)):
           lstDirectories.append(sys.argv[i])
   
   i = 1
   for aDirectory in lstDirectories:
       collectRQ2ResultsForADirectory(aDirectory, i)
       i = i + 1



