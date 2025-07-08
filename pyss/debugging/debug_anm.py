import numpy as np

from pyss.statistics.causal import AdditiveNoiseModel
from pyss.dataset import Dataset

np.random.seed(42)
data = np.random.randint(0, 5, size=(100, 10))
dataset = Dataset(data)
anm = AdditiveNoiseModel()
result = anm.calculate(dataset)