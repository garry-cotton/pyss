from pyspoc.config import Config

#cfg = Config.from_archetypes(
#    "boom",
#    statistic_archetypes=["basic", "causal"],
#    reducer_archetypes=["basic"]
#)
#print(cfg.to_yaml())

yaml = """Statistics:
  pyspoc.statistics.basic:
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
  pyspoc.statistics.causal:
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
  pyspoc.reducers.basic:
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