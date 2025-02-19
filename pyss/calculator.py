from __future__ import annotations

import numpy as np
import pandas as pd
import warnings

from tqdm import tqdm
from typing import Union, Iterable, Any

# From this package
from pyss.dataset import Dataset
from pyss.config import Config
from pyss.statistic import Statistic, ReducedStatistic


class Calculator:
    """
    The calculator takes in a dataset, computes and stores all selected statistical summaries based on a configuration.

    Configurations are provided using the Config class.

    Example:
         import numpy as np
         dataset = np.random.randn(5,500)    # create a random multivariate dataset
         calc = Calculator(dataset=dataset)  # Instantiate the calculator
         calc.compute()                      # Compute all statistical summaries

    Args:
        dataset (Data, np.ndarray, pd.DataFrame, str):
            A multivariate dataset typically with n realisations of p variables.
        name (str, optional):
            The name of the calculator. Mainly used for printing the results but can be useful if you have multiple
            instances, defaults to None.
        labels (array_like, optional):
            Any set of strings by which you want to label the calculator. This can be useful later for classification
            purposes, defaults to None.
        normalise (bool, optional):
            Normalise the dataset across realisations before computing statistical summaries, defaults to True.
    """

    __cached_results = dict()
    __max_calc_results = 5  # Change this to a global config setting

    def __init__(self,
                 dataset: Union[Dataset, np.ndarray, pd.DataFrame, str],
                 name: str = None,
                 labels: Iterable[str] = None,
                 normalise: bool = True):

        self._ss: dict[str, Statistic] = dict()
        self._excluded_ss: list[dict[str, Any]] = list()
        self._normalise: bool = normalise
        self._cached_configs = dict()
        self._dataset: Union[Dataset, None] = None
        self._results_dict = dict()
        self._results = None

        self._loaded_modules = dict()
        self._loaded_stat_config = dict()
        self._loaded_stats = dict()
        self._loaded_reducer_config = dict()
        self._loaded_reducers = dict()

        self.name = name
        self.labels = labels
        self.__set_dataset(dataset)

    @property
    def ss(self):
        """Dict of statistical summaries.

        Keys are the statistical summary identifier and values are their objects.
        """
        return self._ss

    @property
    def n_ss(self):
        """Number of statistical summaries in the calculator."""
        return len(self._ss)

    @property
    def dataset(self):
        """Dataset as a dataset object."""
        return self._dataset

    def __set_dataset(self,
                      dataset: Union[Dataset, np.ndarray, pd.DataFrame, str]):
        """Load new dataset into existing instance.

        Args:
            dataset (pyspc.Data, np.ndarray, pd.DataFrame, str)
                New dataset to attach to calculator.
        """
        if dataset is None:
            return

        if isinstance(dataset, Dataset):
            self._dataset = dataset
            return

        accepted_types = [np.ndarray, pd.DataFrame, str]

        for accepted_type in accepted_types:
            if isinstance(dataset, accepted_type):
                self._dataset = Dataset(data=dataset, normalise=self._normalise)
                return

        raise ValueError("dataset must be of type pyspc.Data or np.ndarray.")

    @property
    def name(self):
        """Name of the calculator."""
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def labels(self):
        """List of calculator labels."""
        return self._labels

    @labels.setter
    def labels(self, labels):
        self._labels = labels

    @property
    def results(self):
        """Results table for all pairwise interactions."""
        return self._results

    # TODO: Restrict the Statistics calculated based on a union of Reducer statistic filters.
    # Stops from computing statistics that won't be used.
    def compute(self, config: Config):
        """Compute the statistical summaries on the dataset."""

        if not hasattr(self, "_dataset"):
            raise AttributeError(
                "Dataset not loaded yet. Please provide dataset to the dataset property.")

        results_dict = dict()
        stats = config.statistics
        reducers = config.reducers
        rstats = config.reduced_statistics
        dataset = self.dataset
        elapsed = 0

        # Calculate configured Statistics.
        if stats:
            stat_pbar = tqdm(stats.keys())            

            for stat_name in stat_pbar:
                try:
                    stat_pbar.set_description(f"Processing [{self._name}: {stat_name}]")

                    # Get the next statistic.
                    stat = stats[stat_name]

                    # Get result (checks cache first before computation).
                    stat.calculate(dataset)

                    # Add the statistic reference to the results dictionary.
                    results_dict[stat_name] = dict()

                except Exception as e:
                    warnings.warn(f'Caught {type(e)} for Statistic "{stat_name}": {e}')

            stat_pbar.close()
            elapsed += stat_pbar.format_dict["elapsed"]

            # Calculate configured Reducers.        
            reducer_pbar = tqdm(reducers.keys())
            stat_names = list(results_dict.keys())

            for reducer_name in reducer_pbar:
                reducer_pbar.set_description(f"Processing [{self._name}: {reducer_name}]")
                reducer = reducers[reducer_name]
                applicable_stat_names = config.get_reducer_filters(reducer)

                if applicable_stat_names is None:
                    reducer_stat_names = stat_names
                else:
                    reducer_stat_names = [stat_name for stat_name in applicable_stat_names if stat_name in stat_names]

                for stat_name in reducer_stat_names:

                    try:
                        # Get computed statistic.
                        stat = stats[stat_name]

                        # If the Statistic is a ReducedStatistic (ie. an all-in-one) then store the result and continue.
                        if isinstance(stat, ReducedStatistic):
                            results_dict[stat_name]["self"] = stat.get_result()
                            continue

                        # Reduce the result.
                        R = reducer.calculate(stat).squeeze()

                        # Save results.
                        results_dict[stat_name][reducer_name] = R

                    except Exception as e:
                        warnings.warn(f'Caught {type(e)} for Reducer "{stat_name}-{reducer_name}": {e}')

            reducer_pbar.close()
            elapsed += reducer_pbar.format_dict["elapsed"]

        # Calculate configured ReducedStatistics.
        if rstats:
            
            rstat_pbar = tqdm(rstats.keys())            

            for rstat_name in rstat_pbar:
                try:
                    rstat_pbar.set_description(f"Processing [{self._name}: {rstat_name}]")

                    # Get the next reduced statistical summary.
                    rstat = rstats[rstat_name]

                    # Get result.
                    R = rstat.calculate(dataset).squeeze()

                    # Save results.
                    results_dict[rstat_name] = dict()
                    results_dict[rstat_name]["self"] = R

                except Exception as e:
                    warnings.warn(f'Caught {type(e)} for ReducedStatistic "{rstat_name}": {e}')

            rstat_pbar.close()
            elapsed += rstat_pbar.format_dict["elapsed"]

        print(f"\nCalculation complete. Time taken: {elapsed:.4f}s")
        self._results = self._build_results_table(results_dict)
        self._results_dict = results_dict
        # inspect_calc_results(self)

    @staticmethod
    def _build_results_table(results: dict) -> pd.DataFrame:
        summaries_vec = np.ndarray((1, 0))
        first_level = []
        second_level = []

        for stat_name, reducers in results.items():
            for reducer_name, reduced_result in reducers.items():
                size = reduced_result.size
                summary_vec = reduced_result.reshape((1, size))
                summaries_vec = np.hstack((summaries_vec, summary_vec))
                first_level.extend([stat_name] * size)
                second_level_names = [reducer_name] if size == 1 else [f"{reducer_name}_{i+1}" for i in range(size)]
                second_level.extend(second_level_names)

        columns = pd.MultiIndex.from_arrays(
            [first_level, second_level], names=["Statistic", "Reducer"]
        )
        results_table = pd.DataFrame(
            data=summaries_vec,
            columns=columns)

        # self._table.columns.name = "process"
        return results_table
