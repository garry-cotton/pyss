
import numpy as np
from pyspoc import ReducedStatistic
from typing import Union

class GlobalMeanMedianDiff(ReducedStatistic):

    def __init__(self):

        # Your initialisation code here.
        # self.arg1 = arg1
        # Calling base class initialiser.
        super().__init__()

    @property
    def name(self) -> str:
        return "global_mean_median_diff"

    @property
    def identifier(self) -> str:
        return "global_mean_median_diff_id"

    @property
    def labels(self) -> list[str]:
        return ["skew"]

    def compute(self, data: np.ndarray) -> Union[np.ndarray, float]:

        # Calculating your reducer as a reduced numpy array or float scalar.
        my_reducer = np.mean(data) - np.median(data)
        # Returning the result
        return my_reducer
