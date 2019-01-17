#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 17:32:07 2019

@author: rafaelolaechea
"""

class LearningRound(object):
    
    def __init__(self, featureSet=[],  learningError=float("inf"),  validationError=float("inf"),  roundNum=0):
        """
        Initializes erorr values and the list of features selected to defaults or to arguments given.
        
        Parameters
        ----------
        featureSet : Array of features
            Features selected up until this round
        learningError: float
            Error with respect to the learning/traininig set.
        validationError: float
            Error with respect to the validation set.
        roundNum: int
            The number of round this learning round is generated in (e.g, 0, 1, 2 .. etc)
        """

        self.featureSet = featureSet
        self.learningError = learningError
        self.validationError = validationError
        self.roundNum = roundNum

        # default class variables.        
        self.bestCandidate = None
        self.bestCandidateSize = 1
        self.bestCandidateScore = 0.0
        self.terminationReason = None


        self.learningError_relative = float("inf")
        self.validationError_relative = float("inf")