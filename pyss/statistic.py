
from __future__ import annotations

import numpy as np
import copy
import gc

from abc import abstractmethod, ABC
from typing import Union

from pyss.base import Component


class Statistic(Component, ABC):

    """
    Base abstract Statistic class intended for computing a statistic from an entire static dataset (n x p).
    Provides a square matrix (p x p) output subject to further processing by applicable Reducers.

    Required Properties:
        name (string): Readable name of the statistic.
        identifier (string): A simpler and minimalist identifier for the statistic.
        labels (list[str]): A list of labels to describe the type of statistic.

    Contracts:
        - Input: (n x p) -> Output: (p x p)
    """

    def __init__(self):
        self.__cached_results: Union[np.ndarray, None] = None
        super().__init__()

    def calculate(self, data: np.ndarray) -> np.ndarray:

        # Get result from cache if present
        result = self.get_result()

        if result is not None:
            return result

        # Else compute from scratch.

        # Assume contemporaneous data by selecting first (dummy) time component.
        data_copy = copy.deepcopy(data)
        result = self.compute(data_copy)

        # Cache result and return
        self.__cached_results = result
        return result

    def get_result(self) -> np.ndarray:
        return self.__cached_results

    def uncache(self, include_gc: bool = False):
        self.__cached_results = None

        if include_gc:
            gc.collect()

    def _get_component_type(self):
        return Statistic


class DynamicStatistic(Statistic, ABC):

    """
    Abstract Statistic class intended for computing dynamic statistics from an entire time series dataset (n x p x t).
    Provides a dynamic square matrix (p x p x t) output subject to further processing by applicable Reducers.

    Contracts:
        - Input: (n x p x t) -> Output: (p x p x t)
    """

    def calculate(self, data: np.ndarray) -> np.ndarray:

        # If data is static n x p then just return a static statistic with m x m shape.
        if data.ndim == 2:
            return super().calculate(data)

        # Else, compute the statistic for each time step.
        results = []
        t = data.shape[2]

        for s in range(t):
            z = data[:, :, s]
            result = super().calculate(z)
            results.append(result)

        # And combine as a dynamic statistic with m x m x t shape.
        S = np.stack(results, axis=2)
        return S


class PairwiseStatistic(Statistic):

    """
    Abstract Statistic class intended for computing statistics from pairwise comparisons over a static dataset (n x p)
    or time series dataset (n x p x t).

    Comparisons can be made between observations, variables or time processes based on instantiation arguments.

    Data can be ordered if required.

    Provides a square matrix (p x p, n x n, t x t) output subject to further processing by applicable Reducers.

    IMPORTANT NOTE: Pairwise statistics for time processes are incompatible with dynamic statistics. The former
    provides a statistic across ALL time points whereas the latter provides a statistic for EACH time point.

    Arguments:
        pairwise_dim (string): Declares the data axis to perform pairwise comparisons over.
            For example, if pairwise_dim="n", computation is applied to all possible observation pairings,
            resulting in n^2 comparisons and an n x n matrix result.

        is_ordered (boolean): Declares whether the statistic requires ordered data (ie: the Wilcoxon signed_rank test).
            If False, computation is performed on the data as is.
            If True, the data along the pairwise_dim axis is ordered first before computation.

    Contracts:
        - Input: (n x p), pairwise_dim: n -> Output: (n x n)
        - Input: (n x p), pairwise_dim: p -> Output: (p x p)
        - Input: (n x p), pairwise_dim: t -> Output: None
        - Input: (n x p x t), pairwise_dim: n -> Output: (n x n)
        - Input: (n x p x t), pairwise_dim: p -> Output: (p x p)
        - Input: (n x p x t), pairwise_dim: t -> Output: (t x t)
    """

    def __init__(self,
                 pairwise_dim: str,
                 is_ordered: bool):

        self.__pairwise_dim = pairwise_dim
        self.__is_ordered = is_ordered
        self.__check_temporal_compatibility(pairwise_dim)
        super().__init__()

    def __check_temporal_compatibility(self, pairwise_dim):
        if isinstance(self, DynamicStatistic) and pairwise_dim == "t":
            raise TypeError("Temporal Pairwise (Timewise) statistics and Dynamic statistics are incompatible. "
                            "Timewise methods compute a statistic for an entire time series. "
                            "Dynamic methods compute a statistic for each time point.")

    def _reshape_data(self, data: np.ndarray) -> np.ndarray:

        match self.__pairwise_dim:
            case "p":
                data = data.swapaxes(0, 1)

            case "t":
                data = data.swapaxes(0, 2)

            case _:  # Consider adding an error if pairwise_dim is not n, p, or t
                data = data

        return data

    @abstractmethod
    def pairwise_compute(self,
                         x: np.ndarray,
                         y: np.ndarray):
        pass

    def compute(self, data: np.ndarray) -> np.ndarray:
        """ Compute statistics over all pairwise permutations.
        """

        data = self._reshape_data(data)

        if self.__is_ordered:
            data.sort(axis=0)

        m = data.shape[0]
        S = np.ndarray(shape=(m, m))

        for i in range(m):
            x = data[i]

            for j in range(m):
                y = data[j]
                S[i, j] = self.pairwise_compute(x, y)

        return S


class ReducedStatistic(Statistic, ABC):

    """
    Abstract Statistic class for computing a fully reduced statistical output, acting as both a Statistic and
    Reducer in a single operation.

    Output is NOT subject to further processing by applicable Reducers and only flattened, if required.
    """

    def calculate(self, data: np.ndarray) -> np.ndarray:
        result = super().calculate(data)
        return result.flatten()
