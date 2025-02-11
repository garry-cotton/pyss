from __future__ import annotations

import numpy as np

from sklearn.decomposition import PCA

from pyss import ReducedStatistic

class PCAVarianceExplainedRatio(ReducedStatistic):

    __cached_pcas: dict[int, PCA] = dict()
    name = "Principal Components Analysis - Variance Explained Ratio"
    identifier = "pca-var"
    labels = ["scalar", "linear"]

    def __init__(self, components: list[int]):
        self._components = components
        super().__init__()

    def compute(self, data: np.ndarray) -> np.ndarray:
        pca = self._get_pca(data)
        return pca.explained_variance_ratio_

    def _get_pca(self, data: np.ndarray) -> PCA:
        data_id = id(data)
        pca = self.__cached_pcas.get(data_id)

        if pca is not None:
            return pca

        n_components = max(self._components)
        pca = PCA(n_components=n_components)
        pca.fit(data)
        self.__cached_pcas[data_id] = pca
        return pca

class PCAEigenVectors(PCAVarianceExplainedRatio):

    name = "Principal Components Analysis - Eigen Vectors"
    identifier = "pca-eig"
    labels = ["vector", "linear"]

    def __init__(self, principal_vectors: list[int]):
        super().__init__(components=principal_vectors)

    def compute(self, data: np.ndarray) -> np.ndarray:
        pca = self._get_pca(data)
        return pca.components_.flatten()
