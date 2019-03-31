#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 11:59:01 2019

@author: rafaelolaechea
"""

#class 

import numpy as np


from EstimateTimeForATransition import TransitionEstimator
    
import MLConstants
        
    

class ResourceValueWrapper(object):
    def __init__(self, isInterval=False, pointValue=0.0, startIntervalValue=0.0, EndIntervalValue=0.0):
        self.isInterval =  isInterval
        self.pointValue = pointValue
        self.startIntervalValue =  startIntervalValue
        self.EndIntervalValue =  EndIntervalValue
        
    def getRepresntativeNumbers(self, Count):
        """
        Converts an interva/number with a Count into a list of numbers        
        """
        Count = int(Count)
        if self.isInterval:
            numberOfSegments = Count + 1
            sizeOfSegment = (self.EndIntervalValue - self.startIntervalValue)/numberOfSegments
            
            lstDistributedPoints = []
            for i in range(0, Count):
                distributedPoint = self.startIntervalValue + (1+i)*sizeOfSegment
                lstDistributedPoints.append(distributedPoint)
            return lstDistributedPoints
        
        else:            
            return [self.pointValue] * Count
    
                

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

class SummaryResourceEstimatesForTransition(object):
    """
    Object that holds summary of the resources estimated by Perfume for a given transition.
    """
    def __init__(self, configurationId, transitionId, resourceLowerBound=0.0, resourceUpperBound=0.0, resourceMean=0.0, resourceStd=0.0):
        self.configurationId = configurationId
        self.transitionId = transitionId
        self.resourceLowerBound = resourceLowerBound
        self.resourceUpperBound = resourceUpperBound
        self.resourceMean = resourceMean
        self.resourceStd = resourceStd
        
class PerfumeResults(object):  
    def __init__(self, configurationId, resultsFilename):

        self.configurationId = configurationId

        self.resultsFilename = resultsFilename
        
        self.dctEntitiesToIdentifierSet = {}
                
        self.dctIdentifierToEntity = {}
        
        self.parsePerfumeFile()
        

        
    def parsePerfumeFile(self):
        """
            Extract sets of entity identifiers.
            Extract set of transitions.
        """        
        self.setRawLinks = set([])
        
        self.setEntities = set()

        
        self.dctIdentifierToTransitionid = {}
        
        self.dctTransitionIdToIdentfiers = {}
        
        
        fdPerf  = open(self.resultsFilename, "r")
        
        allLines  = [x.strip() for x in fdPerf.readlines()]
        
        self.parseEntities(allLines)       
        
        self.parseTransitions(allLines) 
        
                
        fdPerf.close()
        
        #print (self.setEntities)
        
        #print ("Number of Entities found {0}".format(len(self.setEntities)))

        #print ("Number of Edges found {0}".format(len(self.setRawLinks)))        

    def _extractIdentifierFromEntityLine(self, aResultLine):
        """
        Parses the first number in aResultLine as the identifier
        """

        txtIdentifier = aResultLine.split(" ")[0]
        
        return txtIdentifier
    
        
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
    
    
    def updateEntityIdentiferMappings(self, EntityTransitionId, correspondingIdentifier):
        """
        Updates the two maps/lookups  (self.dctEntitiesToIdentifierSet, self.dctIdentifierToEntity) from Identifier to transitionId , and from transitionId to set of Identifiers.        
        """
        
        if EntityTransitionId in self.dctEntitiesToIdentifierSet.keys():
            self.dctEntitiesToIdentifierSet[EntityTransitionId].add(correspondingIdentifier)
        else:
            self.dctEntitiesToIdentifierSet[EntityTransitionId] = set([correspondingIdentifier])
        
        if correspondingIdentifier in self.dctIdentifierToEntity.keys():
            # already set no need to update.
             if self.dctIdentifierToEntity[correspondingIdentifier] != EntityTransitionId:
                 print ("Incorrect Perfume Output  - Redefining entity")
        else:
            self.dctIdentifierToEntity[correspondingIdentifier] = EntityTransitionId
        

        
    def parseEntities(self, allLines):
        """
        Extracts set of entities identifers (with respect to transitions) into a set.
        
        Also Extracts initial, INITIAL, and FINAL ENTITIES.
        
        3 other entities , initial, TERMINAL, and initial
        """
        
        
        for aResultLine in allLines:
            
            if aResultLine.find("\"T_") != -1 or aResultLine.find("\"t_") != -1:
                
                transitionId = self._extractTransitionIdFromLine(aResultLine)
                
                correspondingIdentifier = self._extractIdentifierFromEntityLine(aResultLine)
                             
                self.setEntities.add(transitionId)
                
                
                self.updateEntityIdentiferMappings(transitionId, correspondingIdentifier)
                

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
                
    def GetIdentifiersCorrespondingToATransitionId(self, EntityTransitionId):
        return self.dctEntitiesToIdentifierSet[EntityTransitionId]
        
    def getOutgoingLinks(self, transitionRawIdentifier):
        pass
    
    def getIncomingLinks(self, EntityTransitionId):
        setIncomingLinks = set([])
        tmpSetCorrespondingIdentifiers = self.GetIdentifiersCorrespondingToATransitionId(EntityTransitionId)
        
        for aRawLink in self.setRawLinks:
            if aRawLink.toDotId in tmpSetCorrespondingIdentifiers:
                setIncomingLinks.add(aRawLink)
        return setIncomingLinks
    
    def getAllEntities(self):
        return self.setEntities
        

    def extractSummaryFromParsedPerfumeResult(self, EntityTransitionId):
        """
        Extracts a summary for givent transition id based on a parsed Perfume object
        
        Returns a resource Summary object with resourceLowerBound=0.0, resourceUpperBound=0.0, resourceMean=0.0, resourceStd=0.0.
        """
        
        lstResourcePointEstimates = []        

        tmpSetIncomingLinks = self.getIncomingLinks(EntityTransitionId)
            
        for aRawLink in tmpSetIncomingLinks:

            tmpResourceValue    = aRawLink.resourceValue
                
            lstRepresentativeNumbers = tmpResourceValue.getRepresntativeNumbers(aRawLink.Count)
            
            lstResourcePointEstimates.extend(lstRepresentativeNumbers)

        npArrayResourceEstimates = np.array(lstResourcePointEstimates)
        
        resourceLowerBound, resourceUpperBound, resourceMean, resourceStd = \
                np.min(npArrayResourceEstimates), np.max(npArrayResourceEstimates), np.mean(npArrayResourceEstimates), np.std(npArrayResourceEstimates) 
        
        return SummaryResourceEstimatesForTransition(self.configurationId, EntityTransitionId, resourceLowerBound, resourceUpperBound, resourceMean, resourceStd)
#        configurationId, transitionId, resourceLowerBound=0.0, resourceUpperBound=0.0, resourceMean=0.0, resourceStd=0.0
        
#        print("\t Number of Raw Links Incoming to {0} is {1}".format(EntityTransitionId, len(tmpSetIncomingLinks)))    
#                if tmpResourceValue.isInterval:
#                    print ("tmpResourceValue interval from {0} to {1} with Count {2} =  First Point is {3} .".format( \
#                           tmpResourceValue.startIntervalValue, tmpResourceValue.EndIntervalValue, aRawLink.Count,  lstRepresentativeNumbers[0]))
#                else:
#                    print ("tmpResourceValue numeric value is {0} with Count {1} First Point is {2} ".format(tmpResourceValue.pointValue, aRawLink.Count, lstRepresentativeNumbers[0]))                
#            i = i + 1
#            for anOutgoingLink in self.getOutgoingLinks(transitionIdentifier):
#                    ResourceValueWrapperObject =  anOutgoingLink.getResource()
                    
#                    if ResourceValueWrapperObject.isInterval == True:
#                        lstResourcePointEstimates.extend(getPointSetFromInterval(ResourceValueWrapperObject, anOutgoingLink.Count))
#                    else:
#                        lstResourcePointEstimates.extend([ResourceValueWrapperObject.getPointValue()]*int(anOutgoingLink.Count))


    

                        
            # transitionIdentifer outgoing edges.
            

def getPointSetFromInterval(ResourceValueWrapperObject, Count):
    pass


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
    
    Ignore for now, could come up useful later.
    """
    pass



def calculateQualityScoreOfConfigurations():
    """
    Pass
    """
    lstConfigurations = [71, 263, 327,  401, 635, 1054, 1137, 1212, 1267, 1997]
    for traceName in ["akiyo"]:    
        tmpNewEstimator = TransitionEstimator(MLConstants.x264Name, "{0}/regressors_rep_1.pkl".format(traceName))
        
        transitionsSums = {}
        transitionsCounts = {}
        transitionsAverages = {}
        for currentConfiguration in lstConfigurations :
            tmpResults = PerfumeResults(currentConfiguration, "PerfumeControl/results_rq_3/x264_{0}_configuration_{1}.dot".format(traceName, currentConfiguration))
            
            for transIdName in tmpResults.getAllEntities():
                if transIdName not in ["t_16", "t_17", "t_22"]:
                    summarizedResults = tmpResults.extractSummaryFromParsedPerfumeResult(transIdName)
                                                                                         
                    if transIdName in transitionsSums.keys():
                        transitionsSums[transIdName] = transitionsSums[transIdName] + summarizedResults.resourceMean
                        transitionsCounts[transIdName] = transitionsCounts[transIdName] + 1
                    else:
                        transitionsSums[transIdName] = summarizedResults.resourceMean
                        transitionsCounts[transIdName] =  1                        
        
        for transName in transitionsSums.keys():
            tAverage = transitionsSums[transName] / transitionsCounts[transName]
            print("{0},{1},{2}".format(traceName, transName, tAverage))
            transitionsAverages[transName] = tAverage
            
        dctTotalConfigurationsError = {}
        dctConfigurationsEffectiveCount = {}
        for currentConfiguration in  lstConfigurations:
            tmpResults = PerfumeResults(currentConfiguration, "PerfumeControl/results_rq_3/x264_{0}_configuration_{1}.dot".format(traceName, currentConfiguration))
            
            dctTotalConfigurationsError[currentConfiguration] = 0.0
            dctConfigurationsEffectiveCount[currentConfiguration] = 0.0
            for transIdName in tmpResults.getAllEntities():
                if transIdName not in ["t_16", "t_17", "t_22"]:

                    numericTransId = int(transIdName[2:])
                    PredictedTransitionExecutionTime  = tmpNewEstimator.estimate(currentConfiguration, numericTransId)
                    
                    summarizedResults = tmpResults.extractSummaryFromParsedPerfumeResult(transIdName)
                    
                    normalizedAbsoluteError = abs(summarizedResults.resourceMean - PredictedTransitionExecutionTime) / transitionsAverages[transIdName]
                    
                    normalizedAbsoluteError = min(2.0, normalizedAbsoluteError)
                    
                    dctTotalConfigurationsError[currentConfiguration] =  dctTotalConfigurationsError[currentConfiguration] + normalizedAbsoluteError
                    
                    dctConfigurationsEffectiveCount[currentConfiguration] = dctTotalConfigurationsError[currentConfiguration] + 1.0
        print("Configuration, Nomralized NMAE Average")        
        for currentConfiguration in  lstConfigurations:
            print("{0},{1}".format(currentConfiguration, dctTotalConfigurationsError[currentConfiguration]/dctConfigurationsEffectiveCount[currentConfiguration]))
            
            
    #
    # OFF TO RUNNING AUTONOMOOSE.
    # 
    lstConfigurations =  [0, 3, 6, 7, 13, 18, 20, 26, 29, 31]
    lookupDotEquivalent = { "autonomooseFirst" : "first", "autonomooseSecond" : "second", "autonomooseThird" : "Third" }
    
    for traceName in ["autonomooseFirst", "autonomooseSecond", "autonomooseThird"]:    
        
        tmpNewEstimator = TransitionEstimator(MLConstants.autonomooseName, "{0}/regressors_rep_1.pkl".format(traceName))
        
        traceName = lookupDotEquivalent[traceName]
        
        transitionsSums = {}
        transitionsCounts = {}
        transitionsAverages = {}
        for currentConfiguration in lstConfigurations :
            tmpResults = PerfumeResults(currentConfiguration, "PerfumeControl/results_rq_3/autonomoose_{0}_configuration_{1}.dot".format(traceName, currentConfiguration))
            
            for transIdName in tmpResults.getAllEntities():
                if transIdName not in []:
                    summarizedResults = tmpResults.extractSummaryFromParsedPerfumeResult(transIdName)
                                                                                         
                    if transIdName in transitionsSums.keys():
                        transitionsSums[transIdName] = transitionsSums[transIdName] + summarizedResults.resourceMean
                        transitionsCounts[transIdName] = transitionsCounts[transIdName] + 1
                    else:
                        transitionsSums[transIdName] = summarizedResults.resourceMean
                        transitionsCounts[transIdName] =  1                        
        
        for transName in transitionsSums.keys():
            tAverage = transitionsSums[transName] / transitionsCounts[transName]
            print("{0},{1},{2}".format(traceName, transName, tAverage))
            transitionsAverages[transName] = tAverage
            
        dctTotalConfigurationsError = {}
        dctConfigurationsEffectiveCount = {}
        for currentConfiguration in  lstConfigurations:
            tmpResults = PerfumeResults(currentConfiguration, "PerfumeControl/results_rq_3/autonomoose_{0}_configuration_{1}.dot".format(traceName, currentConfiguration))
            
            dctTotalConfigurationsError[currentConfiguration] = 0.0
            dctConfigurationsEffectiveCount[currentConfiguration] = 0.0
            for transIdName in tmpResults.getAllEntities():
                if transIdName not in ["t_16", "t_17", "t_22"]:

                    numericTransId = int(transIdName[2:])
                    PredictedTransitionExecutionTime  = tmpNewEstimator.estimate(currentConfiguration, numericTransId)
                    
                    summarizedResults = tmpResults.extractSummaryFromParsedPerfumeResult(transIdName)
                    
                    normalizedAbsoluteError = abs(summarizedResults.resourceMean - PredictedTransitionExecutionTime) / transitionsAverages[transIdName]
                    
                    normalizedAbsoluteError = min(2.0, normalizedAbsoluteError)
                    
                    dctTotalConfigurationsError[currentConfiguration] =  dctTotalConfigurationsError[currentConfiguration] + normalizedAbsoluteError
                    
                    dctConfigurationsEffectiveCount[currentConfiguration] = dctTotalConfigurationsError[currentConfiguration] + 1.0
        print("Configuration, Nomralized NMAE Average")        
        for currentConfiguration in  lstConfigurations:
            print("{0},{1}".format(currentConfiguration, dctTotalConfigurationsError[currentConfiguration]/dctConfigurationsEffectiveCount[currentConfiguration]))            

def runFullX264():
    """ 
    Run Comprehensive one
    """
    print ("Selecting Best Configuration, Median Configuration, and Worst Configuration -- Akiyo")
    
    tmpNewEstimator = TransitionEstimator(MLConstants.x264Name, "akiyo/regressors_rep_1.pkl")

    print("ConfigurationId, TransitionId, Our Estimate, Perfume Mean, Perfume STD, Perfume Lower, Perfume Upper")
    for traceName in ["akiyo"]:    
        for currentConfiguration in  [71, 263, 327,  401, 635, 1054, 1137, 1212, 1267, 1997]:
            tmpResults = PerfumeResults(currentConfiguration, "PerfumeControl/results_rq_3/x264_{0}_configuration_{1}.dot".format(traceName, currentConfiguration))
            
            for transIdName in tmpResults.getAllEntities():
                if transIdName not in ["t_16", "t_17", "t_22"]:
                    numericTransId = int(transIdName[2:])
                    PredictedTransitionExecutionTime  = tmpNewEstimator.estimate(currentConfiguration, numericTransId)
                    summarizedResults = tmpResults.extractSummaryFromParsedPerfumeResult(transIdName)
                
                    print("{0}, {1}, {2}, {3}, {4}, {5}, {6}".format(currentConfiguration, numericTransId, PredictedTransitionExecutionTime, summarizedResults.resourceMean, \
                      summarizedResults.resourceStd, summarizedResults.resourceLowerBound, summarizedResults.resourceUpperBound ))

def printPerTrans(): 
    LstAutonomooseConfigurations = [0, 3, 6, 7, 13, 18, 20, 26, 29, 31]
    print("Configuration Id, Transition Id, Execution Time Mean, Execution Time Std, Resource Min, Resource Max")    
    for traceName in ["first", "Second", "Third"]:    
        for currentConfiguration in LstAutonomooseConfigurations:
            AutonomooseResults = PerfumeResults(currentConfiguration, "PerfumeControl/results_rq_3/autonomoose_{0}_configuration_{1}.dot".format(traceName, currentConfiguration))
        
#            print("Extracted Transitions " + str(AutonomooseResults.setEntities) + " for Configuration "  + str(currentConfiguration))
            for EntityTransId in AutonomooseResults.getAllEntities():
                summarizedResults = AutonomooseResults.extractSummaryFromParsedPerfumeResult(EntityTransId)
                print ("{0},{1},{2},{3},{4},{5}, {6}".format(traceName, summarizedResults.configurationId, summarizedResults.transitionId, summarizedResults.resourceMean,\
                       summarizedResults.resourceStd, summarizedResults.resourceLowerBound, summarizedResults.resourceUpperBound))
                
    LstX264Configurations = [71, 263, 327,  401, 635, 1054, 1137, 1212, 1267, 1997]          
    print("Configuration Id, Transition Id, Execution Time Mean, Execution Time Std, Resource Min, Resource Max")    
    for traceName in ["container"]:    
        for currentConfiguration in LstX264Configurations:
            tmpResults = PerfumeResults(currentConfiguration, "PerfumeControl/results_rq_3/x264_{0}_configuration_{1}.dot".format(traceName, currentConfiguration))
        
#            print("Extracted Transitions " + str(AutonomooseResults.setEntities) + " for Configuration "  + str(currentConfiguration))
            for EntityTransId in tmpResults.getAllEntities():
                summarizedResults = tmpResults.extractSummaryFromParsedPerfumeResult(EntityTransId)
                print ("{0},{1},{2},{3},{4},{5}, {6}".format(traceName, summarizedResults.configurationId, summarizedResults.transitionId, summarizedResults.resourceMean,\
                       summarizedResults.resourceStd, summarizedResults.resourceLowerBound, summarizedResults.resourceUpperBound))
                
if __name__ == "__main__":
    lstX264Configurations = [1054]
    
    #x264Results = PerfumeResults(1054, "PerfumeControl/results_rq_3/x264_akiyo_configuration_1054.dot")
    
    # Best, Median, and Worst   
    selectedConfigurationsX264 = [1997, 1137, 635]
    selectedConfigurationsAutonomoose = [29, 26, 31]
    
    tmpNewEstimator = TransitionEstimator(MLConstants.autonomooseName, "autonomooseFirst/regressors_rep_1.pkl")
    print("ConfigurationId,TransitionId,OurEstimate,ResourceMean,ResourceStd,ResourceMin,ResourceMax")  
    for currentConfiguration in selectedConfigurationsAutonomoose:
        AutonomooseResults = PerfumeResults(currentConfiguration, "PerfumeControl/results_rq_3/autonomoose_{0}_configuration_{1}.dot".format("first", currentConfiguration))
        for EntityTransId in AutonomooseResults.getAllEntities():            
            summarizedResults = AutonomooseResults.extractSummaryFromParsedPerfumeResult(EntityTransId)
            
            numericTransId = int(EntityTransId[2:])
            PredictedTransitionExecutionTime  = tmpNewEstimator.estimate(currentConfiguration, numericTransId)
                                                                         
            print ("{0},{1},{2},{3},{4},{5},{6}".format(summarizedResults.configurationId, summarizedResults.transitionId, PredictedTransitionExecutionTime,  summarizedResults.resourceMean,\
                   summarizedResults.resourceStd, summarizedResults.resourceLowerBound, summarizedResults.resourceUpperBound))

    print("ConfigurationId, TransitionId, Our Estimate, Perfume Mean, Perfume STD, Perfume Lower, Perfume Upper")
    
    tmpNewEstimator = TransitionEstimator(MLConstants.x264Name, "akiyo/regressors_rep_1.pkl")
    for currentConfiguration in  selectedConfigurationsX264:
        tmpResults = PerfumeResults(currentConfiguration, "PerfumeControl/results_rq_3/x264_{0}_configuration_{1}.dot".format("akiyo", currentConfiguration))
        
        for transIdName in tmpResults.getAllEntities():
            if transIdName not in ["t_16", "t_17", "t_22"]:
                numericTransId = int(transIdName[2:])
                PredictedTransitionExecutionTime  = tmpNewEstimator.estimate(currentConfiguration, numericTransId)
                summarizedResults = tmpResults.extractSummaryFromParsedPerfumeResult(transIdName)
            
                print("{0},{1},{2},{3},{4},{5},{6}".format(currentConfiguration, numericTransId, PredictedTransitionExecutionTime, summarizedResults.resourceMean, \
                  summarizedResults.resourceStd, summarizedResults.resourceLowerBound, summarizedResults.resourceUpperBound ))                    
    # Same for X264
    
    #runFullX264()
    #calculateQualityScoreOfConfigurations()
    
    
    #print ("Selecting Best Configuration, Median Configuration, and Worst Configuration -- First")
    