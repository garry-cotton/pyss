import warnings
import numpy as np
import inspect

from sklearn.gaussian_process import kernels, GaussianProcessRegressor
from sklearn.metrics import mean_squared_error
from sklearn import linear_model
import mne.connectivity as mnec

from pyss.statistic import Statistic, PairwiseStatistic


class LinearModel(PairwiseStatistic):
    name = "Linear model regression"
    identifier = "lmfit"
    labels = ["misc", "unsigned", "unordered", "normal", "linear", "directed"]

    def __init__(self, model):
        self.identifier += f".{model}"
        self._model = getattr(linear_model, model)
        super().__init__(pairwise_dim="p", is_ordered=False)

    def pairwise_compute(self,
                         x: np.ndarray,
                         y: np.ndarray):

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            y_raveled = np.ravel(y)
            model_params = inspect.signature(self._model).parameters
            if "random_state" in model_params:
                mdl = self._model(random_state=42).fit(x, y_raveled)
            else:
                mdl = self._model().fit(x, y_raveled)

        y_predict = mdl.predict(x)
        return mean_squared_error(y_predict, y_raveled)


class GPModel(PairwiseStatistic):
    name = "Gaussian process regression"
    identifier = "gpfit"
    labels = ["misc", "unsigned", "unordered", "normal", "nonlinear", "directed"]

    def __init__(self, kernel="RBF"):
        self.identifier += f"_{kernel}"
        self._kernel = kernels.ConstantKernel() + kernels.WhiteKernel()
        self._kernel += getattr(kernels, kernel)()
        super().__init__(pairwise_dim="p", is_ordered=False)

    def pairwise_compute(self,
                         x: np.ndarray,
                         y: np.ndarray):

        x_2d = x.reshape(-1, 1) if x.ndim == 1 else x
        y_raveled = np.ravel(y)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            gp = GaussianProcessRegressor(kernel=self._kernel).fit(x_2d, y_raveled)
        y_predict = gp.predict(x_2d)
        return mean_squared_error(y_predict, y_raveled)


class PowerEnvelopeCorrelation(Statistic):
    name = "Power Envelope Correlation"
    identifier = "pec"
    labels = ["unsigned", "misc", "undirected"]

    def __init__(self, orth=False, log=False, absolute=False):
        self._orth = False
        if orth:
            self._orth = "pairwise"
            self.identifier += "_orth"
        self._log = log
        if log:
            self.identifier += "_log"
        self._absolute = absolute
        if absolute:
            self.identifier += "_abs"

        super().__init__()

    def compute(self, data: np.ndarray) -> np.ndarray:
        adj = np.squeeze(
            mnec.envelope_correlation(
                data, orthogonalize=self._orth, log=self._log, absolute=self._absolute
            )
        )
        np.fill_diagonal(adj, np.nan)
        return adj
