import numpy as np

from typing import Iterable
from sklearn.metrics import pairwise_distances
from hyppo.independence import (
    MGC,
    Dcorr,
    HHG,
    Hsic,
)

from pyss.statistic import Statistic, PairwiseStatistic


class PairwiseDistance(Statistic):

    __name = "Pairwise distance"
    __identifier = "pdist"
    __labels = ["unsigned", "distance", "unordered", "nonlinear", "undirected"]

    def __init__(self, metric="euclidean"):
        self.__metric = metric
        self.__identifier += f".{metric}"
        super().__init__()

    def name(self) -> str:
        return self.__name

    def identifier(self) -> str:
        return self.__identifier

    def labels(self) -> Iterable[str]:
        return self.__labels

    def compute(self, data: np.ndarray):
        return pairwise_distances(data, metric=self.__metric)


""" TODO: include optional kernels in each method
"""


class HilbertSchmidtIndependenceCriterion(PairwiseStatistic):
    """Hilbert-Schmidt Independence Criterion (HSIC)"""

    __name = "Hilbert-Schmidt Independence Criterion"
    __identifier = "hsic"
    __labels = ["unsigned", "distance", "unordered", "nonlinear", "undirected"]

    def __init__(self, dim, biased):
        self.__biased = biased

        if biased:
            self.__identifier += ".biased"

        super().__init__(pairwise_dim=dim,
                         is_ordered=False)

    def name(self) -> str:
        return self.__name

    def identifier(self) -> str:
        return self.__identifier

    def labels(self) -> Iterable[str]:
        return self.__labels

    def pairwise_compute(self,
                         x: np.ndarray,
                         y: np.ndarray):

        stat = Hsic(bias=self.__biased).statistic(x, y)
        return stat


class HellerHellerGorfine(PairwiseStatistic):
    """Heller-Heller-Gorfine independence criterion"""

    __name = "Heller-Heller-Gorfine Independence Criterion"
    __identifier = "hhg"
    __labels = ["unsigned", "distance", "unordered", "nonlinear", "directed"]

    def __init__(self, dim):
        super().__init__(pairwise_dim=dim,
                         is_ordered=False)

    def name(self) -> str:
        return self.__name

    def identifier(self) -> str:
        return self.__identifier

    def labels(self) -> Iterable[str]:
        return self.__labels

    def pairwise_compute(self,
                         x: np.ndarray,
                         y: np.ndarray):

        stat = HHG().statistic(x, y)
        return stat


class DistanceCorrelation(PairwiseStatistic):
    """Distance correlation"""

    __name = "Distance correlation"
    __identifier = "dcorr"
    __labels = ["unsigned", "distance", "unordered", "nonlinear", "undirected"]

    def __init__(self, dim, biased):
        self.__biased = biased

        if biased:
            self.__identifier += ".biased"

        super().__init__(pairwise_dim=dim,
                         is_ordered=False)

    def name(self) -> str:
        return self.__name

    def identifier(self) -> str:
        return self.__identifier

    def labels(self) -> Iterable[str]:
        return self.__labels

    def pairwise_compute(self,
                         x: np.ndarray,
                         y: np.ndarray):

        stat = Dcorr(bias=self.__biased).statistic(x, y)
        return stat


class MultiscaleGraphCorrelation(PairwiseStatistic):
    """Multiscale graph correlation"""

    __name = "Multiscale graph correlation"
    __identifier = "mgc"
    __labels = ["distance", "unsigned", "unordered", "nonlinear", "undirected"]

    def __init__(self, pairwise_dim="p"):
        super().__init__(pairwise_dim=pairwise_dim,
                         is_ordered=False)

    def name(self) -> str:
        return self.__name

    def identifier(self) -> str:
        return self.__identifier

    def labels(self) -> Iterable[str]:
        return self.__labels

    def pairwise_compute(self,
                         x: np.ndarray,
                         y: np.ndarray):

        stat = MGC().statistic(x, y)
        return stat


class GromovWasserstainTau(PairwiseStatistic):
    """Gromov-Wasserstain distance (GWTau)"""

    name = "Gromov-Wasserstain Distance"
    identifier = "gwtau"
    labels = ["unsigned", "distance", "unordered", "nonlinear", "undirected"]

    def __init__(self):
        super().__init__(pairwise_dim="p",
                         is_ordered=False)

    @staticmethod
    def vec_geo_dist(x):
        diffs = np.diff(x, axis=0)
        distances = np.linalg.norm(diffs, axis=1)
        return np.cumsum(distances)
    
    @staticmethod
    def wass_sorted(x1, x2):
        x1 = np.sort(x1)[::-1]  # sort in descending order
        x2 = np.sort(x2)[::-1] 

        if len(x1) == len(x2):
            res = np.sqrt(np.mean((x1 - x2) ** 2))
        else:
            N, M = len(x1), len(x2)
            i_ratios = np.arange(1, N + 1) / N
            j_ratios = np.arange(1, M + 1) / M
        
            min_values = np.minimum.outer(i_ratios, j_ratios)
            max_values = np.maximum.outer(i_ratios - 1/N, j_ratios - 1/M)
        
            lam = np.where(min_values > max_values, min_values - max_values, 0)
        
            diffs_squared = (x1[:, None] - x2) ** 2
            my_sum = np.sum(lam * diffs_squared)
        
            res = np.sqrt(my_sum)

        return res
    
    @staticmethod
    def gwtau(xi, xj):
        timei = np.arange(len(xi))
        timej = np.arange(len(xj))
        traji = np.column_stack([timei, xi])
        trajj = np.column_stack([timej, xj])

        vi = GromovWasserstainTau.vec_geo_dist(traji)
        vj = GromovWasserstainTau.vec_geo_dist(trajj)
        gw = GromovWasserstainTau.wass_sorted(vi, vj)
    
        return gw

    def pairwise_compute(self,
                         x: np.ndarray,
                         y: np.ndarray):

        stat = self.gwtau(x, y)
        return stat
