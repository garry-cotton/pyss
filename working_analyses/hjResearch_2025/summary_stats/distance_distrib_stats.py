from pyspoc import ReducedStatistic
import numpy as np
from scipy.stats import skew, kurtosis
from scipy.spatial.distance import cdist
from typing import Union
from abc import ABC
from pyspoc.dataset import Dataset

from scipy.stats import gaussian_kde
from scipy.signal import find_peaks

class DistanceDistributionBase(ReducedStatistic, ABC):

    VALID_METRICS = [
        'canberra', 'chebyshev', 
        'cityblock', 'correlation', 'cosine', 
        'euclidean', 'mahalanobis', 
        'minkowski 0.25', 'seuclidean', 'sqeuclidean',
        'minkowski 4.0'
    ]

    def __init__(self, metric: str = "euclidean", point = 'global_mean_centroid'):

        if metric.startswith('minkowski'):
            try:
                metricval = self.metric.split(' ')[0]
                pval = float(self.metric.split(' ')[1])
            except:
                raise ValueError(f'Invalid metric {metric} : specify as minkowski <SPACE> p')
            
        elif metric not in self.VALID_METRICS:
            raise ValueError(
                f"Invalid metric '{metric}'. Must be one of: {', '.join(self.VALID_METRICS)}"
            )

        self.metric = metric
        self.point = point

    
    def calculate(self, dataset: Dataset):
        result = super().calculate(dataset)
        return result

    def _dist_from_point(self, X: np.ndarray, point) -> np.ndarray:

        center = self._get_center_from_point(X,point)

        if self.metric.startswith('minkowski'):
            metricval = self.metric.split(' ')[0]
            pval = float(self.metric.split(' ')[1])
            return cdist(XA=X,XB=center,metric=metricval,p=pval)
        
        return cdist(XA=X,XB=center,metric=self.metric)
    
    def _get_center_from_point(self,X,point=None):

        if point==None:
            return np.zeros(shape=(1,X.shape[1]))
        
        elif point=='global_mean_centroid':
            return np.mean(X,axis=0).reshape((1,X.shape[1]))
        
        elif point=='global_median_centroid':
            return np.median(X,axis=0).reshape((1,X.shape[1]))
        
        else:
            return point
        
    # TODO: ADD SCALING FUNCTIONS IF NEEDED
    # TODO: ADD CACHING OF DISTRIBUTION SO THAT IT'S EASIER 
    # TODO: UNIT TEST

class DistanceDistributionBasicSummarize(DistanceDistributionBase):
    name = "Distance from Point - Peaks"
    identifier = "dist-point-peaks"
    labels = ["scalar", "distance"]

    summary_fns_dict = {
        "mean" : lambda dists : np.mean(dists),
        "median" : lambda dists : np.median(dists),
        "iqr" : lambda dists : np.quantile(dists,0.75) - np.quantile(dists,0.25),
        "std" : lambda dists : np.std(dists),
        "min" : lambda dists : np.min(dists),
        "max" : lambda dists : np.max(dists),
        "skew" : lambda dists : skew(dists),
        "kurtosis" : lambda dists : kurtosis(dists),
    }

    def __init__(self, metric, point, stats: list[str] = ["mean"]):
        super().__init__(metric=metric, point=point)
        self.stats = stats

    def compute(self, data: np.ndarray) -> np.ndarray:
        dists = self._dist_from_point(data, 'global_mean_centroid')

        if set(self.stats) <= (set(self.summary_fns_dict.keys())):        
            # summary.append(np.median(dists))
            summary = [self.summary_fns_dict[v](dists) for v in self.stats]            
        else:
            raise ValueError(f"Unsupported stats: {self.stats}")
            
        return np.array(summary)

class DistanceDistributionModesSummarize(DistanceDistributionBase):
    name = "Distance from Point - Summary Stats"
    identifier = "dist-point-summ"
    labels = ["scalar", "distance"]

    def __init__(self, metric, point,type='kde'):
        super().__init__(metric=metric, point=point)
        self.type = type

    def compute(self, data: np.ndarray) -> np.ndarray:

        dists = self._dist_from_point(data, 'global_mean_centroid')

        dists1 = dists.flatten()

        if self.type == 'kde':
            kde = gaussian_kde(dists1, bw_method='silverman')
            xs = np.linspace(min(dists1), max(dists1), 1000)
            ys = kde(xs)
            peaks, _ = find_peaks(ys)
            n_modes = len(peaks)

        elif self.type == 'max_line_intersections':
            # TODO: implement
            n_modes = -1.0

        # TODO: USE DERIVATIVES AND INFLECTION POINTS?
        # dy = np.gradient(y, x)        # First derivative
        # d2y = np.gradient(dy, x)      # Second derivative

        else:
            raise ValueError()

        return np.array(n_modes)


# class ARCHIVED_DistanceDistributionSummariesFromPoint(ReducedStatistic):

#     name = "Distance from Point - Summary Stats"
#     identifier = "dist-point-summ"
#     labels = ["scalar", "distance"]

#     VALID_METRICS = [
#         'canberra', 'chebyshev', 
#         'cityblock', 'correlation', 'cosine', 
#         'euclidean', 'mahalanobis', 
#         'minkowski 0.25', 'seuclidean', 'sqeuclidean',
#         'minkowski 4.0'
#     ]

#     def __init__(self, metric: str = "euclidean", stats: str = "mean"):

#         if metric.startswith('minkowski'):
#             try:
#                 metricval = self.metric.split(' ')[0]
#                 pval = float(self.metric.split(' ')[1])
#             except:
#                 raise ValueError(f'Invalid metric {metric} : specify as minkowski <SPACE> p')
            
#         elif metric not in self.VALID_METRICS:
#             raise ValueError(
#                 f"Invalid metric '{metric}'. Must be one of: {', '.join(self.VALID_METRICS)}"
#             )

#         self.metric = metric
#         self.stats = stats

#     def compute(self, data: np.ndarray) -> Union[np.ndarray, float]:

#         dists = self._dist_from_point(data, 'global_mean_centroid')


#         # Summary statistics
#         # TODO: I THINK THERE IS A BETTER WAY TO IMPLEMENT THIS ??
#         summary = []
#         if self.stats == "mean":
#             summary.append(np.mean(dists))
#         elif self.stats == "std":
#             summary.append(np.std(dists))
#         elif self.stats == "min":
#             summary.append(np.min(dists))
#         elif self.stats == "max":
#             summary.append(np.max(dists))
#         elif self.stats == "skew":
#             summary.append(skew(dists))
#         elif self.stats == "kurtosis":
#             summary.append(kurtosis(dists))
#         elif self.stats == "median":
#             summary.append(np.median(dists))
#         else:
#             raise ValueError(f"Unsupported stat: {self.stats}")
            
#         return np.array(summary)

#     def _dist_from_point(self, X: np.ndarray, point) -> np.ndarray:

#         center = self._get_center_from_point(X,point)

#         if self.metric.startswith('minkowski'):
#             metricval = self.metric.split(' ')[0]
#             pval = float(self.metric.split(' ')[1])
#             return cdist(XA=X,XB=center,metric=metricval,p=pval)
        
#         return cdist(XA=X,XB=center,metric=self.metric)
#         # pass

#     ## PROBABLY REALLY BAD DESIGN: because point can be both str and float
#     # hacky for now but fix this / find a better way
#     def _get_center_from_point(self,X,point=None):

#         if point==None:
#             return np.zeros(shape=(1,X.shape[1]))
        
#         elif point=='global_mean_centroid':
#             return np.mean(X,axis=0).reshape((1,X.shape[1]))
        
#         elif point=='global_median_centroid':
#             return np.median(X,axis=0).reshape((1,X.shape[1]))
        
#         else:
#             return point
#         # pass


