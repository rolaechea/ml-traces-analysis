#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 14 11:05:29 2019

@author: rafaelolaechea
"""

# LOSS FUNCTION ENUM.

RELATIVE = 0
LEASTSQUARES = 1
ABSOLUTE = 2

class MLSettings(object):
    """
    Class that stores ML settings.
    """
    def __init__(self, lossFunction=RELATIVE, useBackward=True, abortError=1, limitFeatureSize=True, \
                 featureSizeTrehold=4, crossValidation=False, numberOfRounds=10, backwardErrorDelta=1, minImprovementPerRound=0.1, \
                 withHierarchy=True):
        """
        Constructor for the class that holds settings.
        """
        self.lossFunction = lossFunction
        self.useBackward = useBackward
        self.abortError = abortError
        
        self.limitFeatureSize = limitFeatureSize         
        self.featureSizeTrehold = featureSizeTrehold
        self.crossValidation = crossValidation
        
        self.numberOfRounds = numberOfRounds
        self.backwardErrorDelta = backwardErrorDelta
        self.minImprovementPerRound = minImprovementPerRound
        self.withHierarchy = withHierarchy
