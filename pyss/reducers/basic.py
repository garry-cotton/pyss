import numpy as np
import scipy.stats as sp

from pyss.reducer import Reducer


class Moment(Reducer):

    name = "Moment",
    identifier = "moment"
    labels = ["vector"]

    def __init__(self, moments: list[int]):
        self.__moments = moments
        super().__init__()

    def compute(self, data: np.ndarray) -> np.ndarray:
        mom = sp.moment(data, moment = self.__moments)
        return mom

class SingularValues(Reducer):

    name = "SVD"
    identifier = "svd"
    labels = ["vector"]

    def __init__(self, num_values: int = 2):
        self.__num_values = num_values
        super().__init__()

    def compute(self, data: np.ndarray) -> np.ndarray:
        svs = np.linalg.svd(data, compute_uv=False)
        return svs[:self.__num_values]


class EigenValues(Reducer):

    name = "Eigen"
    identifier = "eig"
    labels = ["square", "vector"]

    def __init__(self, num_values: int = 2):
        self.__num_values = num_values
        super().__init__()

    def compute(self, data: np.ndarray) -> np.ndarray:
        eigs = np.linalg.eigvals(data)
        return eigs[:self.__num_values]


class Diag(Reducer):

    name = "Diag"
    identifier = "diag"
    labels = ["vector"]

    def __init__(self, num_values: int = 2):
        self.__num_values = num_values
        super().__init__()

    def compute(self, data: np.ndarray) -> np.ndarray:
        diag = np.diag(data)
        return diag[:self.__num_values]


class Trace(Reducer):

    name = "Matrix trace"
    identifier = "tr"
    labels = ["scalar"]

    def __init__(self):
        super().__init__()

    def compute(self, data: np.ndarray) -> np.ndarray:
        return np.trace(data)


class Determinant(Reducer):

    name = "Matrix determinant"
    identifier = "det"
    labels = ["square", "scalar"]

    def __init__(self, scaled: bool = True):
        self._scaled = scaled

        if scaled:
            self.identifier += "-scaled"

        super().__init__()

    def compute(self, data: np.ndarray) -> np.ndarray:
        det = np.linalg.det(data)

        if self._scaled:
            return det ** -data.ndim

        return det



