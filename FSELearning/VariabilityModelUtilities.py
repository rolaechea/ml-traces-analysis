#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 16:00:48 2019

@author: rafaelolaechea
"""
from FSELearning import BinaryOption
from FSELearning import VariabilityModel

def createChildOption(varMod, optionName):
    """
    Generates a child feature and adds it to the given variability model
    """
    
    binOp1 =  BinaryOption.BinaryOption(varMod, optionName)
    
    binOp1.optional = True
   
    binOp1.defaultValue = BinaryOption.BINARY_VALUE_DESELECTED
    
    varMod.addConfigurationOption(binOp1)

    
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
    
# Deblock
    createChildOption(vmX264, "deblock")    

    return vmX264

    