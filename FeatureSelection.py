#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 15:09:14 2018

@author: rafaelolaechea
"""

class MlFeature:
    def __init__(self, isBasicFeature, transitionSet):
         
        self.isBasicFeature = isBasicFeature
         
        self.transitionSet = transitionSet
     
    def __eq__():
        pass
    
    def getTransitionId(self):
        
        return self.transitionSet

    def isBasicFeature(self): 
        
        return self.isBasicFeature
    
    def GenerateCrossProductMultiplier(self, otherMLFeature):
        """
        GIven another feature, then generate a cross product of compound features self X otherMLFEature.
        Note if self X otherMLFeature would include a multiplicatin of feature with itself, then we don't include it.
        """
        
        return 0
    