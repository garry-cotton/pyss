
import numpy as np
from pyspoc import ReducedStatistic
from typing import Union

class MyNewReducedStatistic(ReducedStatistic):

    def __init__(self):

        # Your initialisation code here.

        # Calling base class initialiser.
        super().__init__()

    @property
    def name(self) -> str:
        return "my_new_reducer_name"

    @property
    def identifier(self) -> str:
        return "my_new_reducer_identifier"

    @property
    def labels(self) -> list[str]:
        return ["my_new_reducer_label_1",
                "my_new_reducer_label_2",
                "my_new_reducer_label_n"]

    def compute(self, data: np.ndarray) -> Union[np.ndarray, float]:

        # Calculating your reducer as a reduced numpy array or float scalar.
        my_reducer = np.max(data)

        # Returning the result
        return my_reducer
