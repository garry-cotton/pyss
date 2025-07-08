from __future__ import annotations

import runpy

import numpy as np
import copy
import gc
import importlib
import pkgutil

from abc import abstractmethod, ABC
from typing import Union, TYPE_CHECKING
from pathlib import Path

from pyspoc.base import Component
from pyspoc.reducer import Reducer

if TYPE_CHECKING:
    from pyspoc.dataset import Dataset

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

    __cached_results: dict[Dataset, dict[Statistic, np.ndarray]] = dict()

    def __init__(self):
        self.__cached_result = None
        super().__init__()

    def calculate(self, dataset: Dataset) -> np.ndarray:

        # temporarily uncache results, TODO: fix caching mechanisms        
        self.uncache(dataset)

        # Get result from class cache if present.
        dataset_results = self.__cached_results.get(dataset)

        if dataset_results is not None:
            result = dataset_results.get(self)

            if result is not None:
                return result

        # Else compute from scratch.
        data = dataset.data

        # Take a deep copy of the data.
        data_copy = copy.deepcopy(data)
        result = self.compute(data_copy)

        # Cache result in the hierarchy.
        if dataset_results is None:
            self.__cached_results[dataset] = {
                self: result
            }
        else:
            dataset_results[self] = result

        # Cache result locally.
        self.__cached_result = result
        return result

    @classmethod
    def uncache(cls, dataset: Dataset, include_gc: bool = False):
        cached_dataset_results = cls.__cached_results.get(dataset)

        if cached_dataset_results:
            for statistic in cached_dataset_results.keys():
                Reducer.uncache(statistic, include_gc)

            cls.__cached_results[dataset] = dict()

        if include_gc:
            gc.collect()

    def get_result(self) -> Union[None, np.ndarray]:
        return self.__cached_result

    @classmethod
    def available_statistics(cls):
        glb_copy = globals()
        stats = set()

        for obj in glb_copy.values():
            obj_cls = type(obj)

            if issubclass(obj_cls, cls):
                stats.add(obj_cls)

        this_path = Path(__file__)
        dir_path = this_path.parent
        paths = [str(dir_path / "statistics")]

        while paths:
            path = paths.pop()
            mods = list(pkgutil.iter_modules([path]))

            for mod in mods:
                mod_path = path / (mod.name + ".py")
                loaded_mod = runpy.run_path(str(mod_path))

                for obj, val in loaded_mod.items():
                    print(obj, val)

    @staticmethod
    def _get_component_type() -> type:
        return Statistic


class DynamicStatistic(Statistic, ABC):

    """
    Abstract Statistic class intended for computing dynamic statistics from an entire time series dataset (n x p x t).
    Provides a dynamic square matrix (p x p x t) output subject to further processing by applicable Reducers.

    Contracts:
        - Input: (n x p x t) -> Output: (p x p x t)
    """

    def calculate(self, dataset: Dataset) -> np.ndarray:

        # If data is static n x p then just return a static statistic with m x m shape.
        if dataset.data.ndim == 2:

            # temporarily uncache results, TODO: fix caching mechanisms        
            self.uncache(dataset)
            return super().calculate(dataset)

        # Else, compute the statistic for each time step. #TODO: THIS NEEDS TO BE EDITED OUT
        data = dataset.data
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
        dim (string): Declares the data axis to perform pairwise comparisons over.
            For example, if dim="n", computation is applied to all possible observation pairings,
            resulting in n^2 comparisons and an n x n matrix result.

        is_ordered (boolean): Declares whether the statistic requires ordered data (ie: the Wilcoxon signed-rank test).
            If False, computation is performed on the data as is.
            If True, the data along the dim axis is ordered first before computation.

    Contracts:
        - Input: (n x p), dim: n -> Output: (n x n)
        - Input: (n x p), dim: p -> Output: (p x p)
        - Input: (n x p), dim: t -> Output: None
        - Input: (n x p x t), dim: n -> Output: (n x n)
        - Input: (n x p x t), dim: p -> Output: (p x p)
        - Input: (n x p x t), dim: t -> Output: (t x t)
    """

    def __init__(self,
                 dim: str,
                 is_ordered: bool):

        self.__dim = dim
        self.__is_ordered = is_ordered
        self.__check_temporal_compatibility(dim)
        super().__init__()

    def __check_temporal_compatibility(self, dim):
        if isinstance(self, DynamicStatistic) and dim == "t":
            raise TypeError("Temporal Pairwise (Timewise) statistics and Dynamic statistics are incompatible. "
                            "Timewise methods compute a statistic for an entire time series. "
                            "Dynamic methods compute a statistic for each time point.")

    def _reshape_data(self, data: np.ndarray) -> np.ndarray:

        match self.__dim:
            case "p":
                data = data.swapaxes(0, 1)

            case "t":
                data = data.swapaxes(0, 2)

            case _:  # Consider adding an error if dim is not n, p, or t
                data = data

        return data

    @abstractmethod
    def pairwise_compute(self,
                         x: np.ndarray,
                         y: np.ndarray) -> Union[np.ndarray, float]:
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

    def calculate(self, dataset: Dataset) -> np.ndarray:
        # temporarily uncache results, TODO: fix caching mechanisms        
        self.uncache(dataset)

        result = super().calculate(dataset)
        return result.flatten()
