from __future__ import annotations

import numpy as np
import copy
import gc

from abc import abstractmethod
from typing import TYPE_CHECKING

from pyss.base import Component

if TYPE_CHECKING:
    from pyss.statistic import Statistic


class Reducer(Component):

    __cached_results: dict[Statistic, dict[Reducer, np.ndarray]] = dict()

    def __init__(self):
        super().__init__()

    def calculate(self,
                  statistic: Statistic) -> np.ndarray:

        statistic_results = self.__cached_results.get(statistic)

        if statistic_results is not None:
            result = statistic_results.get(self)

            if result is not None:
                return result

        statistic_result = statistic.get_result()
        statistic_result_cp = copy.deepcopy(statistic_result)
        #statistic_result_cp = np.atleast_3d(statistic_result_cp)
        #statistic_sliced = self._slice_data(statistic_result_cp)
        result = self.compute(statistic_result_cp)
        result = np.array(result)

        if statistic_results is None:
            self.__cached_results[statistic] = {
                self: result
            }
        else:
            statistic_results[self] = result

        return result

    @classmethod
    def uncache(cls, statistic: Statistic, include_gc: bool = False):
        cached_statistic_results = cls.__cached_results.get(statistic)

        if cached_statistic_results:
            cls.__cached_results[statistic] = dict()

        if include_gc:
            gc.collect()

    @abstractmethod
    def compute(self, data: np.ndarray) -> np.ndarray:
        pass



    @staticmethod
    def _slice_data(data: np.ndarray):
        return data[:, :, 0]

    @staticmethod
    def _get_component_type() -> type:
        return Reducer