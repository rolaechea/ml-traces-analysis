


if __name__ == "__main__":
    """
    For each transition in X264, compute its  normalized mean average error, and its normalized mean average error standard deviation.
    
    Requires CSV files akiyo.csv, container.csv, and news.csv in X264Results folder
    """
    
    csvFiles = ["x264Results/akiyo.csv",      "x264Results/container.csv",  "x264Results/news.csv"]

    perTransitionAccuracy = {}
    dctAll = {}   
    for aFilename in csvFiles:
        fResults = open(aFilename, 'r')

 
        for line in fResults:
            transitionId, timeTaken, timeTakenStd, MAE, MAEStd  = line.rstrip().split(",")
                
            if int(transitionId) in dctAll.keys():
                dctAll[int(transitionId)].append((timeTaken, timeTakenStd, MAE, MAEStd))
            else:
                dctAll[int(transitionId)] = [(timeTaken, timeTakenStd, MAE, MAEStd)]
    
    lstNMAEOverall = []
    for transitionId in dctAll.keys():
        lstTupleList = dctAll[transitionId]
        
        lstNMAE = []
        lstNMAEStd = []
        for timeTaken, timeTakenStd, MAE, MAEStd in lstTupleList:
            lstNMAEStd.append(float(MAEStd)/float(timeTaken))
            lstNMAE.append(float(MAE)/float(timeTaken))
        print ("{0},{1},{2}".format(transitionId, sum(lstNMAE)/len(lstNMAE), sum(lstNMAEStd)/len(lstNMAEStd)))
        lstNMAEOverall.append(100*sum(lstNMAE)/len(lstNMAE))
        
    print([round(x,1) for x in lstNMAEOverall])
            
