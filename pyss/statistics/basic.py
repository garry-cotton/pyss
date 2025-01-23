import inspect
from typing import Iterable

import numpy as np
from sklearn import covariance as skcov
import scipy as sp

from pyss.statistic import Statistic, PairwiseStatistic


class Covariance(Statistic):
    """
    Computes a variety of covariance statistics for static datasets (n x p) returning a p x p matrix.
    If a time series (n x p x t) is provided, dynamic covariance will be returned instead as a p x p x t tensor.
    Information on covariance estimators at: https://scikit-learn.org/stable/modules/covariance.html
    """

    __name = "Covariance"
    __identifier = "cov"
    __labels = ["basic", "unordered", "linear"]

    def __init__(self,
                 estimator: str = "EmpiricalCovariance",
                 squared: bool = False):

        if squared:
            self.__labels.append("unsigned")
            self.__identifier += ".sq"
        else:
            self.__labels.append("signed")

        self.__is_squared = squared
        self.__estimator = estimator
        super().__init__()

    @property
    def name(self) -> str:
        return self.__name

    @property
    def identifier(self) -> str:
        return self.__identifier

    @property
    def labels(self) -> Iterable[str]:
        return self.__labels

    def compute(self, dataset: np.ndarray) -> np.ndarray:
        cov = self.__fit(dataset)
        return cov.covariance_

    def __fit(self, dataset: np.ndarray):
        cov_dir = [x for x in skcov.__dir__() if inspect.isclass(getattr(skcov, x))]

        if self.__estimator not in cov_dir:
            available_estimators = ",".join(cov_dir)
            raise AttributeError(f"The {self.__name__} estimator {self.__estimator} is not supported.\n"
                                 f"Options include: {available_estimators}.")

        cov_class = getattr(skcov, self.__estimator)()
        cov = cov_class.fit(dataset)

        if self.__is_squared:
            cov = np.square(cov)

        return cov


class Precision(Covariance):

    __name = "Precision"
    __identifier = "prec"

    def __init__(self,
                 estimator: str = "EmpiricalCovariance",
                 squared: bool = False):

        super().__init__(estimator=estimator,
                         squared=squared)

    def compute(self, dataset: np.ndarray) -> np.ndarray:
        cov = self.__fit(dataset)
        return cov.precision_


class SpearmanR(PairwiseStatistic):

    __name = "Spearman's correlation coefficient"
    __identifier = "spearmanr"
    __labels = ["basic", "unordered", "rank", "linear", "undirected"]

    def __init__(self, squared: bool, pairwise_dim: str = "p"):
        self.__squared = squared

        if squared:
            self.__labels += ["unsigned"]
            self.__identifier += ".sq"
        else:
            self.__labels += ["signed"]

        super().__init__(pairwise_dim=pairwise_dim,
                         is_ordered=False)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def identifier(self) -> str:
        return self.__identifier

    @property
    def labels(self) -> Iterable[str]:
        return self.__labels

    def pairwise_compute(self,
                          x: np.ndarray,
                          y: np.ndarray):

        corr = sp.stats.spearmanr(x, y).correlation

        if self.__squared:
            return corr ** 2

        return corr


class KendallTau(PairwiseStatistic):

    __name = "Kendall's tau"
    __identifier = "kendalltau"
    __labels = ["basic", "unordered", "rank", "linear", "undirected"]

    def __init__(self, squared: bool, pairwise_dim: str = "p"):
        self.__squared = squared
        if squared:
            self.__identifier += ".sq"
            self.__labels += ["unsigned"]
        else:
            self.__labels += ["signed"]

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

        corr = sp.stats.kendalltau(x, y).correlation

        if self.__squared:
            return corr ** 2

        return corr
