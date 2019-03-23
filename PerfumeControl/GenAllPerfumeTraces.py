#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 15:25:50 2019

@author: rafaelolaechea
"""

import numpy as np

import argparse


from ParseTrace import setBaseTracesSourceFolder, getFilenameFromConfigurationAndRepetition

from PerfumeControl.TraceConversionUtilities import extractTracesAfterReadingFrames, \
 getNumberTracesToSample, printSingleTracePerfumeFormat
 



        
if __name__ == "__main__":
    """
    Extracting set of traces for ten software configurations that are part of test set in AKIYO / NEWS / CONTAINER test sets.
    
    Only on run # 1 of each product -- could consider mergin from all 100 products, but then would have to sample even more sparsely.
    """        
    videoDirectories  = ["akiyo/", "news/", "container/"]
    
    for videoFolder in videoDirectories:
        q = open(videoFolder + "test_conf_rep_1.pkl")
        
        print (videoFolder)

        q.close()



        
    
