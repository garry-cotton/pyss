import numpy as np

from pyss import Calculator, Config

#yaml_path = "C:/Users/Garry/Research Projects/pyss/pyss/run_config/testing.yaml"
cfg = Config.from_internal("testing")
data = np.random.randn(100, 10)
calc = Calculator(data)
calc.compute(cfg)
