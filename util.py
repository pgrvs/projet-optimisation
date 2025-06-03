def sortByNbCoveredZones(sensors):
    sortedByNbCoveredZones = []

    for s in sensors :
        sortedByNbCoveredZones.append(s)
    
    def coveredZonesKey(s):
        return len(sensors[s]["coverage"])

    sortedByNbCoveredZones.sort(key=coveredZonesKey,reverse=True)

    return sortedByNbCoveredZones

def coversAll(M,N,sensors,chosen):
    notCovered = {f"z{i+1}" for i in range(M)}

    for s in chosen :
        for cov in sensors[s]["coverage"] :
            if(cov in notCovered) :
                notCovered.remove(cov)

    return len(notCovered) == 0

def isElementary(M,N,sensors,chosen):
    if not coversAll(M,N,sensors,chosen):
        return False

    for i in range(len(chosen)):
        copy = [s for s in chosen]
        copy.pop(i)
        if coversAll(M,N,sensors,copy):
            return False
    
    return True