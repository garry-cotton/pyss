import inspect
import numpy as np
import scipy as sp

from sklearn import covariance as skcov
from typing import Union

from pyspoc.statistic import Statistic, PairwiseStatistic


class Covariance(Statistic):
    """
    Computes a variety of covariance statistics for static datasets (n x p) returning a p x p matrix.
    If a time series (n x p x t) is provided, dynamic covariance will be returned instead as a p x p x t tensor.
    Information on covariance estimators can be found at: https://scikit-learn.org/stable/modules/covariance.html
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
    def labels(self) -> list[str]:
        return self.__labels

    def compute(self, data: np.ndarray) -> np.ndarray:
        cov_obj = self.__fit(data)
        cov = cov_obj.covariance_

        if self.__is_squared:
            cov = np.square(cov)

        return cov

    def __fit(self, data: np.ndarray):
        cov_dir = [x for x in skcov.__dir__() if inspect.isclass(getattr(skcov, x))]

        if self.__estimator not in cov_dir:
            available_estimators = ", ".join(cov_dir)
            raise AttributeError(f"The {self.__class__.__name__} estimator {self.__estimator} is not supported.\n"
                                 f"Options include: {available_estimators}.")

        cov_class = getattr(skcov, self.__estimator)()
        cov_obj = cov_class.fit(data)
        return cov_obj


class Precision(Covariance):

    __name = "Precision"
    __identifier = "prec"

    def __init__(self,
                 estimator: str = "EmpiricalCovariance",
                 squared: bool = False):

        super().__init__(estimator=estimator,
                         squared=squared)

    def compute(self, dataset: np.ndarray) -> np.ndarray:
        cov_obj = self.__fit(dataset)
        cov = cov_obj.precision_

        if self.__is_squared:
            cov = np.square(cov)

        return cov

class SpearmanR(PairwiseStatistic):
    # Setting the name internally.
    __name = "Spearman's correlation coefficient"

    # Setting the identifier internally.
    __identifier = "spearmanr"

    # Setting the labels internally.
    __labels = ["basic", "rank", "linear", "undirected"]

    def __init__(self, squared: bool):

        # Storing the squared argument.
        self.__squared = squared

        # If squared,
        if squared:

            # Add the "unsigned" label.
            self.__labels += ["unsigned"]

            # And the ".sq" suffix to the identifier.
            self.__identifier += ".sq"

        else:

            # Else, add the "signed" label.
            self.__labels += ["signed"]

        # Call the base class initialiser with required arguments.
        super().__init__(dim="p",
                         is_ordered=False)

    # Implementing the name property.
    @property
    def name(self) -> str:
        return self.__name

    # Implementing the identifier property.
    @property
    def identifier(self) -> str:
        return self.__identifier

    # Implementing the labels property.
    @property
    def labels(self) -> list[str]:
        return self.__labels

    # Implementing the PairwiseStatistic's pairwise_compute method.
    # Arguments:
    #  - x: A given observation as an n x 1 numpy array OR a given variable as a p x 1 numpy.
    #  - y: A given observation as an n x 1 numpy array OR a given variable as a p x 1 numpy.
    def pairwise_compute(self,
                         x: np.ndarray,
                         y: np.ndarray) -> Union[np.ndarray, float]:

        # Compute the Spearman rank correlation coefficient using Scipy library.
        corr = sp.stats.spearmanr(x, y).correlation

        # Square results if required.
        if self.__squared:
            return corr ** 2

        # Return value.
        return corr


class KendallTau(PairwiseStatistic):

    __name = "Kendall's tau"
    __identifier = "kendalltau"
    __labels = ["basic", "unordered", "rank", "linear", "undirected"]

    def __init__(self, squared: bool, dim: str = "p"):
        self.__squared = squared
        if squared:
            self.__identifier += ".sq"
            self.__labels += ["unsigned"]
        else:
            self.__labels += ["signed"]

        super().__init__(dim=dim,
                         is_ordered=False)

    def name(self) -> str:
        return self.__name

    def identifier(self) -> str:
        return self.__identifier

    def labels(self) -> list[str]:
        return self.__labels

    def pairwise_compute(self,
                          x: np.ndarray,
                         y: np.ndarray) -> Union[np.ndarray, float]:

        corr = sp.stats.kendalltau(x, y).correlation

        if self.__squared:
            return corr ** 2

        return corr
