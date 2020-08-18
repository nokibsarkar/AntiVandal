import numpy as np
import pickle
from mathplotlib import pyplot
X = None
with open("data","rb") as fp:
    X = pickle.load(fp)
