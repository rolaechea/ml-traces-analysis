#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 16:00:48 2019

@author: rafaelolaechea
"""
from FSELearning import BinaryOption
from FSELearning import VariabilityModel
from FSELearning import Configuration

def createChildOption(varMod, optionName):
    """
    Generates a child feature and adds it to the given variability model
    """
    
    binOp1 =  BinaryOption.BinaryOption(varMod, optionName)
    
    binOp1.optional = True
   
    binOp1.defaultValue = BinaryOption.BINARY_VALUE_DESELECTED
    
    varMod.addConfigurationOption(binOp1)


def generateFullAutonomooseVariabilityModel():
    """
    Generates all the features corresponding to Autonomooose.
    
    
    BooleanOptions = [("BEHAVIOR", 4 ), \
                      ("OCCUPANCY", 2),
                      ("WAYPOINTS", 1)]

        Behavior Planner
        Occupancy or Mockupancy Planner
        Waypoints Collection
        Dyn. Object Tracking
        Dyn. Car Tracking.
        Dyn. Person Tracking
        
    """
    vmAutonomoose = VariabilityModel.VariabilityModel("autonomoose_model")

    createChildOption(vmAutonomoose, "behavior")
    
    createChildOption(vmAutonomoose, "occupancy")

    createChildOption(vmAutonomoose, "waypoints")

    createChildOption(vmAutonomoose, "dyn_tracking_obj")
  
    createChildOption(vmAutonomoose, "dyn_tracking_car")

    createChildOption(vmAutonomoose, "dyn_tracking_person")
    
    return vmAutonomoose

def generateFullX264VariabilityModel():
    """
    Generates all the feature corresponding to case X264.
    """
    vmX264 = VariabilityModel.VariabilityModel("x264_model")

# Reference frames.

    createChildOption(vmX264, "ref_1")
    
    createChildOption(vmX264, "ref_2")

    createChildOption(vmX264, "ref_3")

# BFRAMES.
    createChildOption(vmX264, "bframes_1")

    createChildOption(vmX264, "bframes_2")

    createChildOption(vmX264, "bframes_3")
    
# Frame Analysis Options (binaries, but combined in special ways).
    
    createChildOption(vmX264, "analysis_psub8")    
#
    createChildOption(vmX264, "analysis_psub16")    
#   
    createChildOption(vmX264, "analysis_i4")    

# Binaries, starting with Deblock
    createChildOption(vmX264, "deblock")    

    createChildOption(vmX264, "mixed_refs")    
    
    createChildOption(vmX264, "weighted_prediction")    
    
    createChildOption(vmX264, "pskip")    
    
    createChildOption(vmX264, "cavlc")    
#
#        BooleanOptions = [("DEBLOCK", 16, [" --nf", ""]), \
#                      ("MIXED_REFS", 8, ["", " --mixed-refs"]), \
#                      ("WEIGHTED_PREDICTION", 4, ["", " --weightb"]), \
#                      ("PSKIP", 2, [" --no-fast-pskip", ""]),
#                  ("CAVLC", 1, [" --cabac", ""])]
        
    return vmX264

    
BITSET_FIRST_ONE = [1,0,0]  
BITSET_SECOND_ONE  = [0, 1,0]
BITSET_THIRD_ONE =  [0,0,1]  



def transformSingleConfigurationToX264FSE(configurationId, configuarationBitset, vmX264):
    """
    Given a configuratin id transform to FSE format -- works for x264 for now
    
    Extract bit by bit inverse of the code in xxx.    
    
    Parameters
    ----------
    vmX264 : Variability Model describing X264.    
    
    
    Returns
    -------
    Equivalent X264 Configurations in FSE Format and measured NFP Value of 0.
    """
    lstSelectedOptions = []
    REF_STR = "ref_"
    if configuarationBitset[0:3] == BITSET_FIRST_ONE:
        REF_STR += "1"
    elif configuarationBitset[0:3] == BITSET_SECOND_ONE :
        REF_STR += "2"    
    elif  configuarationBitset[0:3] == BITSET_THIRD_ONE:
        REF_STR += "3"    
    else:
        raise Exception("Unexpected configuration Value for ref in a configurations bitset")

    BFRAMES_STR = "bframes_"
    if configuarationBitset[3:6] == BITSET_FIRST_ONE:
        BFRAMES_STR += "1"
    elif configuarationBitset[3:6] == BITSET_SECOND_ONE :
        BFRAMES_STR += "2"    
    elif  configuarationBitset[3:6] == BITSET_THIRD_ONE:
        BFRAMES_STR += "3"    
    else:
        raise Exception("Unexpected configuration Value for BFRAMES_STR in a configurations bitset")

    refOptionToUse = vmX264.getBinaryOption(REF_STR)

    lstSelectedOptions.append(refOptionToUse)
    
    bframeOptionToUse = vmX264.getBinaryOption(BFRAMES_STR)    
    
    lstSelectedOptions.append(bframeOptionToUse)
    
    binaryConfNames = ["analysis_psub8",   "analysis_psub16",  "analysis_i4", "deblock", "mixed_refs", "weighted_prediction" , \
                       "pskip", "cavlc"]

    startOffset = 6 # Skip first two string of size 3 -- skip positions 0 ... 5

    for aBit, relativePosition in zip(configuarationBitset[startOffset:], \
                                      range(len(configuarationBitset[startOffset:]))):
       if aBit == 1:
           lstSelectedOptions.append(vmX264.getBinaryOption(binaryConfNames[relativePosition]))
         

#    print ("{0}, {1}, {2}".format(str(refOptionToUse.name), str(bframeOptionToUse.name), str([x.name for x in lstSelectedOptions])))

    tmpRoot = vmX264.getBinaryOption("root")
    
    dctCurrent = {tmpRoot: BinaryOption.BINARY_VALUE_SELECTED}
    
    for aSelectedConfigurationOption in lstSelectedOptions:
        dctCurrent[aSelectedConfigurationOption] =  BinaryOption.BINARY_VALUE_SELECTED
        
     
    tmpCurrentConfiguration = Configuration.Configuration(dctCurrent, 0.0)

    return tmpCurrentConfiguration


def transformSingleConfigurationToAutonomooseFSE(configurationId, configuarationBitset, vm):
    """
    Given a configuratin id transform to FSE format -- works for Autonomoose 
    
    Extract bit by bit inverse of the code that generates bitsets for autonomooose (in AutonomooseTraces)    
    
    Parameters
    ----------
    vm : Variability Model describing Autonomoose    
    
    
    Returns
    -------
    Equivalent Autonomoose Configurations in FSE Format and measured NFP Value of 0.
    
    TODO integrate with transformSingleConfigurationToX264FSE.
    """
    
    lstSelectedOptions =  []
    
    binaryConfNames = ["behavior",   "occupancy",  "waypoints", "dyn_tracking_obj", "dyn_tracking_car", "dyn_tracking_person"]
    
    for aBit, relativePosition in zip(configuarationBitset, range(len(configuarationBitset))):
       if aBit == 1:
           lstSelectedOptions.append(vm.getBinaryOption(binaryConfNames[relativePosition]))        
        
    tmpRoot = vm.getBinaryOption("root")
    
    dctCurrent = {tmpRoot: BinaryOption.BINARY_VALUE_SELECTED}
    
    for aSelectedConfigurationOption in lstSelectedOptions:
        dctCurrent[aSelectedConfigurationOption] =  BinaryOption.BINARY_VALUE_SELECTED
        
        
    tmpCurrentConfiguration = Configuration.Configuration(dctCurrent, 0.0)

    return tmpCurrentConfiguration        
    