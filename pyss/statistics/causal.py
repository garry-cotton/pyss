import numpy as np

from sklearn.gaussian_process import GaussianProcessRegressor
from cdt.causality.pairwise import CDS, IGCI, RECI
from cdt.causality.pairwise.ANM import normalized_hsic

from pyss.statistic import PairwiseStatistic


class AdditiveNoiseModel(PairwiseStatistic):

    name = "Additive Noise Model"
    identifier = "anm"
    labels = ["unsigned", "causal", "unordered", "linear", "directed"]

    def __init__(self):
        super().__init__(pairwise_dim="p",
                         is_ordered=True)

    # monkey-patch the anm_score function
    @staticmethod
    def corrected_anm_score(x, y):
        x_2d = x.reshape(-1, 1) if x.ndim == 1 else x
        gp = GaussianProcessRegressor(random_state=42).fit(x_2d, y)
        y_predict = gp.predict(x_2d).reshape(-1, 1)
        indepscore = normalized_hsic(y_predict - y, x_2d)
        return indepscore

    anm_score = corrected_anm_score

    def pairwise_compute(self, x, y):
        return self.anm_score(x, y)


class ConditionalDistributionSimilarity(PairwiseStatistic):

    name = "Conditional Distribution Similarity Statistic"
    identifier = "cds"
    labels = ["unsigned", "causal", "unordered", "nonlinear", "directed"]

    def __init__(self):
        super().__init__(pairwise_dim="p", is_ordered=False)

    def pairwise_compute(self, x: np.ndarray, y: np.ndarray):
        return CDS().cds_score(x, y)


class RegressionErrorCausalInference(PairwiseStatistic):

    name = "Regression Error-based Causal Inference"
    identifier = "reci"
    labels = ["unsigned", "causal", "unordered", "nonlinear", "directed"]

    def __init__(self):
        super().__init__(pairwise_dim="p", is_ordered=False)

    def pairwise_compute(self, x: np.ndarray, y: np.ndarray):
        return RECI().b_fit_score(x, y)


class InformationGeometricConditionalIndependence(PairwiseStatistic):

    name = "Information-Geometric Conditional Independence"
    identifier = "igci"
    labels = ["causal", "directed", "nonlinear", "unsigned", "unordered"]

    def __init__(self, dim: str):
        super().__init__(pairwise_dim=dim, is_ordered=False)

    def pairwise_compute(self, x: np.ndarray, y: np.ndarray):
        return IGCI().predict_proba((x, y))