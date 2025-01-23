import numpy as np

from pyss.statistics.causal import AdditiveNoiseModel

np.random.seed(42)
data = np.random.randint(0, 5, size=(100, 10))
anm = AdditiveNoiseModel()
anm.calculate(data)
