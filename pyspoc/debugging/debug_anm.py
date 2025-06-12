import numpy as np

from pyspoc.statistics.causal import AdditiveNoiseModel
from pyspoc.dataset import Dataset

np.random.seed(42)
data = np.random.randint(0, 5, size=(100, 10))
dataset = Dataset(data)
anm = AdditiveNoiseModel()
result = anm.calculate(dataset)