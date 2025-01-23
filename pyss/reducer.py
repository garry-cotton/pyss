from __future__ import annotations

import numpy as np
import copy
import gc

from abc import abstractmethod
from typing import Union, TYPE_CHECKING

from pyss.statistic import Statistic
from pyss.base import Component

if TYPE_CHECKING:
    from pyss.config import Config


class Reducer(Component):

    def __init__(self):
        self.__cached_result: dict[Statistic, np.ndarray] = dict()
        self.__cfg: Union[Config, None] = None
        super().__init__()

    def calculate(self,
                  statistic: Statistic) -> np.ndarray:

        summary_result = self.__cached_result.get(statistic)

        if summary_result is not None:
            return summary_result

        statistic_result = statistic.get_result()
        statistic_result_cp = copy.deepcopy(statistic_result)
        statistic_result_cp = np.atleast_3d(statistic_result_cp)
        statistic_sliced = self._slice_data(statistic_result_cp)
        summary_result = self.compute(statistic_sliced)
        summary_result = np.array(summary_result)
        self.__cached_result[statistic] = summary_result
        return summary_result

    def uncache(self, include_gc: bool = False):
        self.__cached_result = None

        if include_gc:
            gc.collect()

    @abstractmethod
    def compute(self, data: np.ndarray) -> np.ndarray:
        pass

    @staticmethod
    def _slice_data(data: np.ndarray):
        return data[:, :, 0]

    def _get_component_type(self):
        return Reducer
