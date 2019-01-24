#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 15:41:13 2019

@author: rafaelolaechea
"""
import BinaryOption
import Configuration
import random
#from BinaryOption. BinaryOption import BinaryOption. BinaryOption

    
class VariabilityModel(object):
    pass

    def __init__(self, name):
        """
        Central model to store all configuration options and their constraints.
        """
        self.name  = name
                
        self.binaryOptions = []
                
        self.root = BinaryOption.BinaryOption(self, "root")
        
        self.binaryOptions.append(self.root) 
        
    
    def addConfigurationOption(self, newOption):
        """
        Adds a configuration option to the variability model.
        
        Checks whether an option with the same name already exists and whether invalid characters are within the name. 
        If no such option exists, then adds it. If no parent is set, then set parent to root option.
        
        Parameters
        ----------
        newOption : ConfigurationOption
        The option to be added to the variability model.
        
        Returns
        -------
        True if option was added or is root. False otherwise.        
        """
        # no need to add root -- return true
        if newOption.name == "root":
            return True
        
        # if it already exists return true.
        for existingOption in self.binaryOptions:
            if existingOption.name == newOption.name:
                return False
        
        # Set parent to root.
        if newOption.parent == None:
            newOption.parent = self.root
            
        self.binaryOptions.append(newOption)
        
        return True
        
    def initOptions(self):
        """
    
        After loading all options, we can replace the names for children, the parent, etc. with the actual objects.
        
        Only required when reading from XML or after initializing.
        """
        pass
        
    def getBinaryOption(self, name):
        """
        Searches for a binary option with the given name
        
        Returns
        -------        
        Either the binary option with the given name or None if not found
        
        """
        for varOption  in self.binaryOptions:
            if varOption.name == name:
                return varOption
    
        return None
    
    def getBinaryOptions(self):
         return self.binaryOptions
        
    def configurationIsValid(self, ConfigurationC):
        """
        Determine whether ConfigurationC violates any constraints or not.
        """
        return True # no constraints for now.
    
    def getRoot(self):
        """
        Returns the BinaryOption. BinaryOption representing root.
        """
        return self.root
    
    
def createChildOption(varMod, optionName):
    binOp1 =  BinaryOption.BinaryOption(varMod, optionName)
    
    binOp1.optional = True
   
    binOp1.defaultValue = BinaryOption.BINARY_VALUE_DESELECTED
    
    varMod.addConfigurationOption(binOp1)
    
def generateX264VariabilityModel():
    """
    Hard code generation of X264 Var model.
    
    NOTES
    -----
    Will later transform to load from XML.

    Parameters.    
    """
    vmX264 = VariabilityModel("x264_model")

# Reference frames.

    createChildOption(vmX264, "ref_1")
    
    createChildOption(vmX264, "ref_2")

    createChildOption(vmX264, "ref_3")

# BFRAMES.
    createChildOption(vmX264, "bframes_1")

    createChildOption(vmX264, "bframes_2")

    createChildOption(vmX264, "bframes_3")
    
# Deblocl
    createChildOption(vmX264, "deblock")    
    
    return vmX264


# Test that generate Candidates is working properly.
    


def generateLearningAndValidationSetX264(vmX264):    
    """
    Generates (say 5) learning and validation configurations to to test FeatureSubsetSelection 
    
    """
    lstLearningMeasurements = []    
    lstValidationsMeasurements = []
    
    tmpRoot = vmX264.getBinaryOption("root")
    
    random.seed(2000)
   
    count = 0
    for i in range(1,4):
        for j in range(1,4):
            for k in range(0,2):
                refOptionToUse = vmX264.getBinaryOption("ref_" + str(i))
                bframeOptionToUse = vmX264.getBinaryOption("bframes_" + str(j))
                if k == 0:
                    useDeblockOption = True
                    deblockOptionToUse = vmX264.getBinaryOption("deblock")
                else:
                    useDeblockOption = False 
                count = count + 1
                
                if useDeblockOption:
                    dctCurrent = {tmpRoot:BinaryOption.BINARY_VALUE_SELECTED , refOptionToUse:BinaryOption.BINARY_VALUE_SELECTED, bframeOptionToUse:BinaryOption.BINARY_VALUE_SELECTED, deblockOptionToUse:BinaryOption.BINARY_VALUE_SELECTED } 
                else:
                    dctCurrent = {tmpRoot:BinaryOption.BINARY_VALUE_SELECTED, refOptionToUse: BinaryOption.BINARY_VALUE_SELECTED, bframeOptionToUse : BinaryOption.BINARY_VALUE_SELECTED}
                
                if i == 1:
                    if k == 1:
                        measuredNFP = 100.0
                    else:
                        measuredNFP = 80
                else:
                    if k == 1:
                        measuredNFP = 40
                    else:
                        measuredNFP = 20
                    
                tmpCurrentConfiguration = Configuration.Configuration(dctCurrent, measuredNFP)
                
                tmpChoice = random.choice([0, 1])
                if (tmpChoice  == 0):
                    lstLearningMeasurements.append(tmpCurrentConfiguration)
                else:
                    lstValidationsMeasurements.append(tmpCurrentConfiguration)
                    
    return lstLearningMeasurements, lstValidationsMeasurements