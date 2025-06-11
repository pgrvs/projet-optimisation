import random
from typing import Set

from util import coversAll, isElementary

def generateConfigsRandom(M,N,sensors,rounds = 100):

    configs = []

    for i in range(rounds):
        config = generateElementary(M,N,sensors)
        
        normalized = sorted(config)
        if normalized not in [sorted(c) for c in configs]:
            configs.append(config)
        
    for config in configs :
        print("---------------------------------------------------")
        print(config)
        print("covers all ? : ",coversAll(M,N,sensors,config))
        print("elementary ? : ",isElementary(M,N,sensors,config))
        print("---------------------------------------------------")

    print(len(configs))

    return configs

def generateElementary(M,N,sensors):
    """génère une config aléatoire élémentaire."""
    chosen : Set = set()

    while not (coversAll(M,N,sensors,chosen)):

        randomSensorIndex = random.randint(1,N)

        chosen.add(f"s{randomSensorIndex}")

    while not isElementary(M,N,sensors,chosen):
        copy = [s for s in chosen]

        randomSensorIndex = random.randint(0,len(copy)-1)

        copy.pop(randomSensorIndex)

        if coversAll(M,N,sensors,copy):
            chosen = copy

    return chosen