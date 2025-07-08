import numpy as np

from pyspoc import Calculator, Config

cfg = Config.from_internal("testing")
data = np.random.randn(100, 10)
calc = Calculator(data)
calc.compute(cfg)
