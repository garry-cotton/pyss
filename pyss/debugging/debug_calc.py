import numpy as np

from pyss.calculator import Calculator
from pyss.config import Config

yaml_path = "C:/Users/Garry/Research Projects/pyss/pyss/run_config/testing.yaml"
cfg = Config.from_yaml_file("boom", yaml_path)
data = np.random.randn(100, 10)
calc = Calculator(data)
calc.compute(cfg)
