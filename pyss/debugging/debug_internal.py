from pyss.config import Config

#cfg = Config.from_archetypes(
#    "boom",
#    statistic_archetypes=["basic", "causal"],
#    reducer_archetypes=["basic"]
#)
#print(cfg.to_yaml())

yaml = """Statistics:
  pyss.statistics.basic:
    Covariance:
      schemes:
        std:
          squared: false
          estimator: EmpiricalCovariance
    Precision:
      schemes:
        std:
          squared: false
          estimator: EmpiricalCovariance
  pyss.statistics.causal:
    AdditiveNoiseModel:
      schemes:
        std: 
    ConditionalDistributionSimilarity:
      schemes:
        std:
    RegressionErrorCausalInference:
      schemes:
        std:
Reducers:
  pyss.reducers.basic:
    Moment:
      schemes:
        std:
          moments:
          - 2
          - 4
    SingularValues:
      schemes:
        std:
          num_values: 2
    EigenValues:
      schemes:
        std:
          num_values: 2
    Diag:
      schemes:
        std:
          num_values: 2
    Trace:
      schemes:
        std: null
    Determinant:
      schemes:
        std:
          scaled: true
"""

Config.from_yaml("test", yaml)