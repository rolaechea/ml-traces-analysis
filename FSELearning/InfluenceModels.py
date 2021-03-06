#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 17:34:04 2019

@author: rafaelolaechea
"""

class InfluenceModel(object):
    """
    
    vm : VariabilityModel
    
    BinaryOptionsInfluence - Dictionary -- Maps BoolOptions to a featureWrapper object.
    
    interactionInfluence -- Dictionary -- Maps Interaction to a featureWrapper object    
    """    
    def __init__(self, vm):
        self.vm = vm
        self.binaryOptionsInfluence = {}
        self.interactionInfluence = {}
        
    def estimate(self, aConfiguration):
        """
        Estimates for the given confugration the corresponding value of the non-functional property
        
        To determine the value all the influences of all configuration options and interactions are considered.
        
        Parameters
        ----------
        Configuration : Configuration
        The configuration for which the estimation should be calculated                
        
        
        Notes
        -----
        Manually tested, seems to work fine Jan. 4th 2019
        """
        prediction = 0.0

        for keyItemBinaryOption, valItemFeatureWrapper in self.binaryOptionsInfluence.items():
            if valItemFeatureWrapper.isValidConfig(aConfiguration):
                prediction += valItemFeatureWrapper.evalOnConfiguration(aConfiguration) * valItemFeatureWrapper.Constant

        for keyItemInfluence, valItemFeatureWrapper in self.interactionInfluence.items():
            if valItemFeatureWrapper.isValidConfig(aConfiguration):
                prediction += valItemFeatureWrapper.evalOnConfiguration(aConfiguration) * valItemFeatureWrapper.Constant
        
        return prediction
    
                
    
    def clearBinaryOptionsInfluence(self):
        """
        Set binaryOptionsInfluence to an empty dictionary
        """
        self.binaryOptionsInfluence = {}
        
    def clearInteractionInfluence(self):
        """
        Set interactionInfluence to an empty dictionary
        """
        self.interactionInfluence = {}        