import numpy as np

from pyspoc.config import Config
from pyspoc.calculator import Calculator

cfg = Config.from_yaml_file("testing", "../run_config/test_rstatistic.yaml")
data = np.random.normal(size=(100,10))
calc = Calculator(data, "me", normalise=True)
calc.compute(cfg)
print(calc.results)