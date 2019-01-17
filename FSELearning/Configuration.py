#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 16:56:26 2019

@author: rafaelolaechea
"""

class Configuration(object):
    def __init__(self, binarySelection, measuremement):
        """
        Creates a configuration with the given set an binary and numeric features selected, not existing ones take default values.
        """

        #Binary options of this configuration. For each option it is stored whether the option is selceted or deselected in this configuration.
        self.dctBinaryOptionValues = binarySelection
        self.nfpValue  = measuremement
        
        
        self.identifier = self.generateIdentifier(",")
        
        
    def generateIdentifier( separator):
        """
        Returns the identifier describing the choice of binary configuration options
        """
        pass

    def getNfpValue(self):
        return self.nfpValue