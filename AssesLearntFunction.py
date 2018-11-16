#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 16:37:41 2018

@author: rafaelolaechea
"""
from ParseTrace import getTransitionToBagOfTimesForAllRepsForAProduct, getSamplingRatiosDict

from TransitionDictionaryManipulations import downSampleSingleDictionary, calculatePerTransitionsCounts

import numpy as np
import sys

import pickle

if __name__ == "__main__":
#    x.py sampled.pkl conf_train.pkl cv_input.csv assesmentInput.pkl  assment_output_filename   
    if   len(sys.argv) > 5:
        
        sampleTrainFilename = sys.argv[1]
        
        
        confTrainFilename = sys.argv[2]
        
        
        CvResultsFilename = sys.argv[3]
        
        AssementInputFilename = sys.argv[4]
        
        OutFilename = sys.argv[5]        
    else:
        print("Incorrect usage -  requires 5 filenames parameters")
        exit(0)
        
    dictRatios =  getSamplingRatiosDict()