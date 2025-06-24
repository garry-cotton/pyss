import numpy as np

from pyspoc.statistic import ReducedStatistic
from pyspoc.statistics.basic import Covariance

class ReducedCovarianceTest(Covariance, ReducedStatistic):    
        
    def compute(self, data: np.ndarray):
        result = Covariance.compute(self, data)        
        return result.diagonal().flatten()
    
class PCABase(ReducedStatistic, ABC):

    def __init__(self, components: list[int]):
        self.__cached_pca = None
        self._components = components
        self.__n_components = max(self._components)
    
    def calculate(self, dataset: Dataset):
        cached_pca_tuple = self.__cached_pcas.get(dataset)
        cached_pca = None
        curr_n_components = 0

        if cached_pca_tuple:
            cached_pca, curr_n_components = cached_pca_tuple

        if curr_n_components >= self.__n_components:
            self.__cached_pca = cached_pca

        result = super().calculate(dataset)
        self.__cached_pcas[dataset] = (self.__cached_pca, self.__n_components)
        return result
    
    def _get_pca(self, data: np.ndarray) -> PCA:
        if self.__cached_pca is not None:
            return self.__cached_pca
        
        pca = PCA(n_components=self.__n_components)
        pca.fit(data)
        self.__cached_pca = pca
        return pca
