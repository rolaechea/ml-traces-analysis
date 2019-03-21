#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 15:25:50 2019

@author: rafaelolaechea
"""

import random

from pickleFacade import loadObjectFromPickle






        
if __name__ == "__main__":
    """
    Extracting set of traces for ten software configurations that are part of test set in AKIYO / NEWS / CONTAINER test sets.
    
    Only on run # 1 of each product -- could consider mergin from all 100 products, but then would have to sample even more sparsely.
    """        
    videoDirectories  = ["akiyo/", "news/", "container/"]
    
    chosenConfs = set([])
    trainingSetsAcrossAsSets = []
    trainingSetsAcrossAsLists = []
    
    for videoFolder in videoDirectories:
        q = loadObjectFromPickle(videoFolder + "test_conf_rep_1.pkl")
        trainingSetsAcrossAsSets.append(set(q))
        trainingSetsAcrossAsLists.append(q)

    while(len(chosenConfs) < 10):
        potentialConfiguration =  random.choice(trainingSetsAcrossAsLists[0])
        
        if (potentialConfiguration not in chosenConfs) and \
            (potentialConfiguration  in trainingSetsAcrossAsSets[1]) and \
            (potentialConfiguration  in trainingSetsAcrossAsSets[2]):
                chosenConfs.add(potentialConfiguration)
                
    print ("Chosen Configurations : {0}".format(str(chosenConfs)))
            
#        ConfTen = 104
#    
#    if ConfTen in trainingSetsAcrossAsSets[0]:
#        print ("In first Set")
#    else:
#        print ("Not In first Set")        
#        
#    if ConfTen in trainingSetsAcrossAsSets[1]:
#        print ("In Second Set")
#    else:
#        print ("Not In Second Set")        
#        
#    if ConfTen in trainingSetsAcrossAsSets[2]:
#        print ("In Third Set")
#    else:
#        print ("Not In Third Set")        



        
    
