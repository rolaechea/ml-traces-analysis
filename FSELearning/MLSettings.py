#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 14 11:05:29 2019

@author: rafaelolaechea
"""

class MLSettings(object):
    def __init__(self, useBackward=True, numberOfRounds=10, limitFeatureSize=True, featureSizeTrehold=3):
        """
        Constructor to a class that holds settings.
        """
        self.useBackward = useBackward
        self.numberOfRounds = numberOfRounds
        self.limitFeatureSize = limitFeatureSize
        self.featureSizeTrehold = featureSizeTrehold