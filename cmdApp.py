import sys

from reader import read_data_file


if __name__ == "__main__" :

    pathToFile = sys.argv[1]

    read_data_file(pathToFile)