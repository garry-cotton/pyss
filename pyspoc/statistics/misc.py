import warnings
import numpy as np
import inspect

from sklearn.gaussian_process import kernels, GaussianProcessRegressor
from sklearn.metrics import mean_squared_error
from sklearn import linear_model
import mne.connectivity as mnec

from pyspoc.statistic import Statistic, PairwiseStatistic


class LinearModel(PairwiseStatistic):
    name = "Linear model regression"
    identifier = "lmfit"
    labels = ["misc", "unsigned", "unordered", "normal", "linear", "directed"]

    def __init__(self, model):
        self.identifier += f".{model}"
        self._model = getattr(linear_model, model)
        super().__init__(dim="p", is_ordered=False)

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
        super().__init__(dim="p", is_ordered=False)

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
    # Setting the name internally.
    __name = "Power Envelope Correlation"

    # Setting the identifier internally.
    __identifier = "pec"

    # Setting the labels internally.
    __labels = ["unsigned", "misc", "undirected"]

    def __init__(self, orth=False, log=False, absolute=False):

        # If the orthogonal argument is provided...
        if orth:
            # Store the orthogonal argument to use in the compute method.
            self.__orth = "pairwise"

            # Update the identifier.
            self.__identifier += "_orth"

        # Otherwise, default to False.
        else:
            self.__orth = False

        # Store the log argument for use in the compute method.
        self.__log = log

        # If set...
        if log:
            # Update the identifier.
            self.__identifier += "_log"

        # Store the absolute argument for use in the compute method.
        self.__absolute = absolute

        # If set...
        if absolute:
            # Update the identifier.
            self.__identifier += "_abs"

        # Call the base class initialiser.
        super().__init__()

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

    # Compute method requires implementing.
    # data: Full dataset with n observations, p variables as a numpy array.
    def compute(self, data: np.ndarray) -> np.ndarray:

        # Utilizing the envelop_correlation function provided by the MNE-Connectivity library.
        env_corr = mnec.envelope_correlation(

            # Passing through the stored arguments from the initialiser.
            data, orthogonalize=self.__orth, log=self.__log, absolute=self.__absolute
        )

        # Squeezing the result to remove any excess dimensions.
        adj = np.squeeze(env_corr)

        # Filling self/auto-correlations with NaNs.
        np.fill_diagonal(adj, np.nan)

        # Returning the p by p matrix as numpy array.
        return adj
