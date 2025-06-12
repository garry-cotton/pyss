import numpy as np

from pyspoc.statistic import ReducedStatistic
from pyspoc.statistics.basic import Covariance

class ReducedCovarianceTest(Covariance, ReducedStatistic):    
        
    def compute(self, data: np.ndarray):
        result = Covariance.compute(self, data)        
        return result.diagonal().flatten()