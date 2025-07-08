import numpy as np

from pyss.statistic import ReducedStatistic
from pyss.statistics.basic import Covariance

class ReducedCovarianceTest(Covariance, ReducedStatistic):    
        
    def compute(self, data: np.ndarray):
        result = Covariance.compute(self, data)        
        return result.diagonal().flatten()