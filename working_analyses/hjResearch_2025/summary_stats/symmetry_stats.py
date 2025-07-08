
from pyspoc import ReducedStatistic, Statistic
import numpy as np
from scipy.spatial.distance import cdist
from typing import Union
from abc import ABC
from pyspoc.dataset import Dataset
from scipy.stats import special_ortho_group

# unsure if this should inherit from Statistic or ReducedStatistic 
# -> since we are calculating multiple n x n objects for this one
class RandomRotationBase(Statistic, ABC):
    # TODO: DESIGN/FIX - ON HOLD FOR NOW
    def __init__(self, metric: str = "euclidean"):
        self.metric = metric
    
    def calculate(self, dataset: Dataset):
        result = super().calculate(dataset)
        return result

    def _apply_random_rotation(self,X):
        p = X.shape[1]
        R = special_ortho_group.rvs(p)  # Random p×p orthogonal matrix
        return X @ R.T

    def _find_min_dist_rotated(X, X_rot):
        D = cdist(X, X_rot)
        min_distances = np.min(D, axis=1)
        return min_distances
    
