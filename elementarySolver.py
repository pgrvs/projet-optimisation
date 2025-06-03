import random

from util import coversAll, isElementary

def solveElementary(M,N,sensors):
    sortedSensors = [key for key in sensors]
    random.shuffle(sortedSensors)

    print("covers all ? : ",coversAll(M,N,sensors,sortedSensors))
    print("elementary ? : ",isElementary(M,N,sensors,sortedSensors))
