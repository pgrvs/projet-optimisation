import sys

from configsGeneratorRandom import generateConfigsRandom
from reader import read_data_file


if __name__ == "__main__" :

    pathToFile = sys.argv[1]

    M, N, sensors = read_data_file(pathToFile)

    print("M : ",M,", N : ",N,", sensors : ",sensors)

    solved = generateConfigsRandom(M,N,sensors)

    print("solved : ",solved)