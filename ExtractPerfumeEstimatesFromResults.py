#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 11:59:01 2019

@author: rafaelolaechea
"""

#class 



class ResourceValueWrapper(object):
    def __init__(self, isInterval=False, pointValue=0.0, startIntervalValue=0.0, EndIntervalValue=0.0):
        self.isInterval =  isInterval
        self.pointValue = pointValue
        self.startIntervalValue =  startIntervalValue
        self.EndIntervalValue =  EndIntervalValue

def createResourceWrapperFromString(rawString):
    """
    Creates a ResourceValueWrapper object from a string
    
    String can be either [Number/Float,NumberFloat]  or Number/Float
    """    
    if rawString.find(",") != -1:
        # Interval Case
        commaOffset = rawString.find(",") 
        #
        # Extrac start/end from a strig of  [Number,Number]
        IntervalStart = float(rawString[1:commaOffset])
        IntervalEnd = float(rawString[commaOffset+1:len(rawString)-1])
        
        
        return ResourceValueWrapper(True, 0.0, IntervalStart, IntervalEnd)
    else:
        # Point Value.
        
        pointValue = float(rawString)
        return ResourceValueWrapper(False, pointValue)
    
    

        

class RawLink(object):
    def __init__(self, fromDotId, toDotId, hasResource=False, resourceValue=None, Count=0):
        self.fromDotId = fromDotId
        self.toDotId = toDotId
        self.hasResource = hasResource
        self.resourceValue = resourceValue
        self.Count = Count
        
        
class PerfumeResults(object):  
    def __init__(self, configurationId, resultsFilename):
        self.configurationId = configurationId
        self.resultsFilename = resultsFilename
        
        self.parsePerfumeFile()
        
    def parsePerfumeFile(self):
        """
            Extract sets of entity identifiers.
            Extract set of transitions.
        """        
        self.setRawLinks = set([])
        
        self.setEntities = set()

        fdPerf  = open(self.resultsFilename, "r")
        
        allLines  = [x.strip() for x in fdPerf.readlines()]
        
        self.parseEntities(allLines)       
        
        self.parseTransitions(allLines)       
                
        fdPerf.close()
        
        #print (self.setEntities)
        
        #print ("Number of Entities found {0}".format(len(self.setEntities)))

        #print ("Number of Edges found {0}".format(len(self.setRawLinks)))        
        
    def _extractTransitionIdFromLine(self, aResultLine):
        """
        Helper function to parse a string and extract first occurence of "T_XXX" or "t_XXX"  (should only be called on line that includes it.)
        """
        if aResultLine.find("\"T_") != -1:        
            startTransitionIdOffset =  aResultLine.find("\"T_")  + 1
            endTransitionIdOffset = aResultLine.find("\"", startTransitionIdOffset)
        
            transitionId = aResultLine[startTransitionIdOffset:endTransitionIdOffset]
            
        elif aResultLine.find("\"t_") != -1:            
            startTransitionIdOffset =  aResultLine.find("\"t_")  + 1
            endTransitionIdOffset = aResultLine.find("\"", startTransitionIdOffset)
        
            transitionId = aResultLine[startTransitionIdOffset:endTransitionIdOffset]        
            
        return transitionId
    
    def _extractEdgeIdsFromLineWithEdge(self, aResultLine):
        """
        Returns a tuple of id from, and id to extracted from aResultLine
        """
        offsetEndFirstId = aResultLine.find("->")
        
        offsetStartSecondId = offsetEndFirstId + 2
        offsetEndSecondId = aResultLine.find(" ", offsetStartSecondId)
        
        firstId =  aResultLine[0:offsetEndFirstId]
        secondId = aResultLine[offsetStartSecondId:offsetEndSecondId]        
            
        return firstId, secondId
    
    def parseEntities(self, allLines):
        """
        Extracts set of entities identifers (with respect to transitions) into a set.
        
        Also Extracts initial, INITIAL, and FINAL ENTITIES.
        
        3 other entities , initial, TERMINAL, and initial
        """
        
        
        for aResultLine in allLines:
            
            if aResultLine.find("\"T_") != -1 or aResultLine.find("\"t_") != -1:
                
                transitionId = self._extractTransitionIdFromLine(aResultLine)
                             
                self.setEntities.add(transitionId)
                

    def parseTransitions(self, allLines):
        """
        Extracts all edges and annotates with them resource consumption (either Segment or Value, or None), and count.
        """
        for aResultLine in allLines:
            
            if aResultLine.find("->") != -1:
                sourceEdge, destinationEdge = self._extractEdgeIdsFromLineWithEdge(aResultLine)
                
                labelStartIndex = aResultLine.find("\"") + 1
                labelEndIndex = aResultLine.find("\"", labelStartIndex)
                              
                labelText = aResultLine[labelStartIndex : labelEndIndex].strip()
                
                splittedLabelText = labelText.split(" ")
                

                if len(splittedLabelText) == 2:
                    #FIRST ITEM IS COUNT, SECOND ITEM IS PROBABILITY (WHICH WE IGNORE)
                    
                    Count = int(splittedLabelText[0])
                    newRawLink = RawLink(sourceEdge, destinationEdge, False, None, Count)
                else:                                        
                    # FIRST ITEM IS RESOURCE, SECOND ITEM IS COUNT
                    Count = int(splittedLabelText[1])
                    
                    aResourceValue =  createResourceWrapperFromString(splittedLabelText[0])
                    newRawLink = RawLink(sourceEdge, destinationEdge, True, aResourceValue, Count)
                    
                    
                    
                self.setRawLinks.add(newRawLink)


def CaclulateTransitionIdToIdentifiers():
    """
    Extracts for each transition id, the list of identifier that represent it in the dot file.
    """
    pass


def CalculateAllIntervalsRelatedToATransition():
    """
    Extracts all intervals (including count) that are related to a transition.
    """
    

def generateFilenames():
    """
    Returns a list of filenames to process
    """
    
if __name__ == "__main__":
    
    newPerfumeResultsExtractor = PerfumeResults(1054, "PerfumeControl/results_rq_3/x264_akiyo_configuration_1054.dot")
    
    newPerfumeResultsExtractor = PerfumeResults(13, "PerfumeControl/results_rq_3/autonomoose_first_configuration_0.dot")
    
    transitionId = []
    
    """
    pass
    
    Inputs 
        1. Subject System
        2. Base Folder
        3. Video Files (CSV)
        4. Configurations (CSV)        
        5. Output file
        
    Algorithm Desciption 
    
    Output Description
        
        For each product in X264
            For each transition in that product's learnt model:        
                Have a mapping of Counts, Time Taken where Time Taken can be Single Value or Value Range.
    -----
        ~~~ a PDF for each transition Times Product around possible times ???
         
        How to handle intervals ?
         Overlapping Intervals ??
         Width of INtervals ?
         


1.        
    """
    

