from __future__ import annotations

import numpy as np

from sklearn.decomposition import PCA
from abc import ABC

from pyspoc import ReducedStatistic
from pyspoc.dataset import Dataset

class PCABase(ReducedStatistic, ABC):

    __cached_pcas: dict[Dataset, tuple[PCA, int]] = dict()

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

class PCAVarianceExplainedRatio(PCABase):

    name = "Principal Components Analysis - Variance Explained Ratio"
    identifier = "pca-var"
    labels = ["scalar", "linear"]

    def __init__(self, components: list[int]):
        super().__init__(components=components)

    def compute(self, data: np.ndarray) -> np.ndarray:
        pca = self._get_pca(data)
        indices = [i - 1 for i in self._components]
        return pca.explained_variance_ratio_[indices]

class PCAEigenVectors(PCABase):

    name = "Principal Components Analysis - Eigen Vectors"
    identifier = "pca-eig"
    labels = ["vector", "linear"]

    def __init__(self, principal_vectors: list[int]):
        super().__init__(components=principal_vectors)

    def compute(self, data: np.ndarray) -> np.ndarray:
        pca = self._get_pca(data)
        evectors = pca.components_
        indices = [i - 1 for i in self._components]
        return evectors[indices]
    
