import numpy as np

from typing import Literal, Union

from pyspoc.reducer import Reducer


class Norm(Reducer):

    name = "Norm"
    identifier = "norm"
    labels = ["scalar"]

    def __init__(self, order: Union[Literal[0],
                                    Literal[1], Literal[-1],
                                    Literal[2], Literal[-2],
                                    Literal["fro"], Literal["nuc"]]):
        self._order = order
        super().__init__()

    def compute(self, data: np.ndarray) -> np.ndarray:
        return np.array(np.linalg.norm(x=data, ord=self._order))


class EntryWiseMatrixNorm(Reducer):

    name = "Entry Wise Norm (L_p,q)"
    identifier = "ew-norm"
    labels = ["scalar"]

    def __init__(self, p: int, q: int):
        self.__p = p
        self.__q = q
        super().__init__()

    def compute(self, data: np.ndarray) -> np.ndarray:
        component_wise_power = abs(data)**self.__p
        inner_sums = component_wise_power.sum(axis=1)**(self.__p / self.__q)
        outer_sum = inner_sums.sum()**(1 / self.__q)
        return outer_sum


class SchattenNorm(Reducer):

    name = "Schatten Norm"
    identifier = "sch-norm"
    labels = ["scalar"]

    def __init__(self, p: int):
        self.__p = p
        super().__init__()

    def compute(self, data: np.ndarray) -> np.ndarray:
        svs = np.linalg.svd(data, compute_uv=False)
        svs_power_sum = (svs**self.__p).sum()
        return svs_power_sum**(1 / self.__p)
