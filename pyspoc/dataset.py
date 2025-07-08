"""Provide dataset structures for multivariate analysis.

Code is adapted from Patricia Wollstadt's IDTxL (https://github.com/pwollstadt/IDTxl)
"""
from __future__ import annotations

import copy

import numpy as np
import pandas as pd
import os

# from scipy.stats import zscore
# from scipy.signal import detrend
from sklearn.preprocessing import RobustScaler, StandardScaler
from typing import Iterable, Union
from time import time

from pyspoc import base
from pyspoc import settings
from pyspoc.statistic import Statistic


class Dataset:

    """
    Store dataset for dependency analysis.

    Dataset takes a 2-dimensional array representing realisations of random variables.
    Indicate the arrangement of realisations (n) and variables (p) in a two-character string
    e.g. 'np' for an array with rows representing realisations and columns representing variables.

    Example:
        >>> # Initialise empty dataset object
        >>> dataset = Dataset()
        >>>
        >>> # Load a prefilled financial dataset
        >>> data_forex = Dataset.load_dataset("forex")
        >>>
        >>> # Create dataset objects with dataset of various sizes
        >>> d = np.arange(3000).reshape((3, 1000))  # 3 procs.,
        >>> data_2 = Dataset(d, dim_order='ps')        # 1000 observations

    Args:
        data (array_like, optional):
            2-dimensional array with raw dataset, defaults to None.
        dim_order (str, optional):
            Order of dimensions, accepts two combinations of the characters 'n' and 'p', defaults to 'np'.
        normalise (bool, optional):
            If True, dataset is z-scored (normalised) along the realisations dimension, defaults to True.
        name (str, optional):
            Name of the dataset
        var_names (list, optional):
            List of variable names with length the number of variables, defaults to None.
        n_realisations_subsample (int, optional):
            Truncates dataset to this many realisations, defaults to None.
        n_variables_subsample (int, optional):
            Truncates dataset to this many variables, defaults to None.
    """

    def __init__(
            self,
            data: Union[np.ndarray, pd.DataFrame, str],
            dim_order: str = "np",
            normalise: bool = True,
            name: str = None,
            var_names: Iterable[str] = None,
            n_realisations_subsample: int = None,
            n_variables_subsample: int = None):

        self.normalise = normalise
        self.name = name
        self.__dim_order = None
        self.__n = None
        self.__n_subsample = None
        self.__p = None
        self.__p_subsample = None
        self.__base_data = None
        self.__data_type = None
        self.__data = None
        self.__var_names = list()
        self.__set_data(data=data,
                        dim_order=dim_order,
                        n_realisations_subsample=n_realisations_subsample,
                        n_variables_subsample=n_variables_subsample,
                        var_names=var_names)

        self.instantiation_time = time()

    @property
    def name(self) -> str:
        """Name of the Data object."""
        return self.__name

    @name.setter
    def name(self, name: str):
        """Set the name of the Data object."""
        if name is None:
            name = ""

        base.check_type(name, str)
        self.__name = name

    @property
    def data(self) -> np.ndarray:
        return self.__data

    @property
    def data_type(self) -> type:
        return self.__data_type

    @property
    def dim_order(self) -> str:
        return self.__dim_order

    @dim_order.setter
    def dim_order(self, dim_order: str):
        base.check_type(dim_order, str)

        if len(dim_order) > 2:
            raise RuntimeError("dim_order can not have more than two entries")

        self.__dim_order = dim_order

    @property
    def normalise(self) -> bool:
        return self.__normalise

    @normalise.setter
    def normalise(self, normalise: bool):
        base.check_type(normalise, bool)
        self.__normalise = normalise

    @property
    def n_realisations(self) -> int:
        return self.__n

    @property
    def n_realisations_subsample(self) -> int:
        if not self.__n_subsample:
            return self.__n

        return self.__n_subsample

    @n_realisations_subsample.setter
    def n_realisations_subsample(self, n_realisations_subsample: int):
        if n_realisations_subsample is not None:
            base.check_type(n_realisations_subsample, int)
            base.check_natural_number(n_realisations_subsample)

        self.__n_subsample = n_realisations_subsample

    @property
    def n_variables(self) -> int:
        return self.__p

    @property
    def n_variables_subsample(self) -> int:
        if not self.__p_subsample:
            return self.__p

        return self.__p_subsample

    @n_variables_subsample.setter
    def n_variables_subsample(self, n_variables_subsample: int):
        if n_variables_subsample is not None:
            base.check_type(n_variables_subsample, int)
            base.check_natural_number(n_variables_subsample)

        self.__p_subsample = n_variables_subsample

    @property
    def var_names(self) -> Iterable[str]:
        """List of variable names."""
        return self.__var_names

    @property
    def var_names_subsample(self) -> Iterable[str]:
        return self.__var_names[:self.__p_subsample]

    def to_numpy(self,
                 realisation: int = None,
                 squeeze: bool = False) -> np.ndarray:

        """Return the numpy array."""
        if realisation is not None:
            data = self.data[realisation]
        else:
            data = self.data

        if squeeze:
            return np.squeeze(data)
        else:
            return data

    @staticmethod
    def convert_to_numpy(data: Union[np.ndarray, pd.DataFrame, str]) -> np.ndarray:
        """Converts other dataset instances to default numpy format."""

        if isinstance(data, np.ndarray):
            return data
        elif isinstance(data, pd.DataFrame):
            return data.to_numpy()
        elif isinstance(data, str):
            return Dataset.__load_data(data)
        else:
            raise TypeError(f"Unknown data type: {type(data)}")

    @staticmethod
    def __load_data(path: str) -> np.ndarray:
        ext = os.path.splitext(path)[1]
        if ext == ".npy":
            return np.load(path)
        elif ext == ".txt":
            return np.genfromtxt(path)
        elif ext == ".csv":
            return np.genfromtxt(path, ",")
        else:
            raise TypeError(f"Unknown filename extension: {ext}")

    def __set_data(self,
                   data: Union[np.ndarray, pd.DataFrame, str],
                   dim_order: str = "np",
                   n_realisations_subsample: int = None,
                   n_variables_subsample: int = None,
                   var_names: Iterable[str] = None):

        """Overwrite dataset in an existing instance.

        Args:
            data (ndarray):
                2-dimensional array of realisations

            dim_order (str, Default "np"):
                Two character string indicating the order of dimensions (n) and variables (p).

            n_realisations_subsample (str, Optional):
                Indicates the number of realisations to include in the final dataset. With no value
                specified, all observations will be used.

            n_variables_subsample (str, Optional):
                Indicates the number of variables to include in the final dataset. With no value
                specified, all variables will be used.

            var_names (Iterable[str], Optional):
                Provides a set of names for the dataset variables. Must be the same length as the number
                of variables (p).
        """

        new_data = copy.deepcopy(data)
        self.dim_order = dim_order
        self.n_realisations_subsample = n_realisations_subsample
        self.n_variables_subsample = n_variables_subsample

        if len(dim_order) != new_data.ndim:
            raise RuntimeError(
                "Data array dimension ({0}) and length of "
                "dim_order ({1}) are not equal.".format(new_data.ndim, len(dim_order))
            )

        if not self.name:
            self.name = base.retrieve_arg_name(new_data, max_steps=3)

        name = self.name
        new_data = self.convert_to_numpy(new_data)
        new_data = self.__reorder_data(new_data, dim_order)
        #data = np.atleast_3d(data)
        nans = np.isnan(new_data)

        if nans.any():
            raise ValueError(
                f"Dataset {name} contains non-numerics (NaNs) in variables: {np.unique(np.where(nans)[0])}."
            )

        self.__base_data = new_data
        self.__data_type = type(new_data[0, 0])
        self.__set_data_dim(new_data)
        new_data = self.__subsample_data(new_data)

        if self.normalise:
            new_data = self.__normalise_data(new_data)

        self.__data = new_data

        if var_names is not None:
            base.check_iterable(var_names)
            var_names_list = list(var_names)
            base.check_type(var_names_list[0], str)
            self.__var_names = var_names
        else:
            if isinstance(self.__base_data, pd.DataFrame):
                self.__var_names = self.__base_data.columns
            else:
                self.__var_names = [f"var-{i}" for i in range(self.n_variables)]

        self.__message(
            f'Dataset "{name}" now has properties: {self.n_realisations} realisations, '
            f'{self.n_variables} variables.')

    def __subsample_data(self, data: np.ndarray) -> np.ndarray:
        n_realisations = self.__n_subsample
        n_variables = self.__p_subsample
        subsampled_dataset = data

        if n_realisations is not None:
            subsampled_dataset = subsampled_dataset[:n_realisations]

        if n_variables is not None:
            subsampled_dataset = subsampled_dataset[:, :n_variables]

        return subsampled_dataset

    @staticmethod
    def __normalise_data(data: np.ndarray) -> np.ndarray:
        # TODO: FIX / CHOOSE 
        # print("Normalising the dataset using zscores \n")
        # data = zscore(data, axis=0, nan_policy="omit", ddof=1)
        # try:
        #     data = detrend(data, axis=0)
        #     return data
        # except ValueError as err:
        #     print(f"Could not detrend dataset: {err}")

        # print("Normalising the dataset using RobustScaler \n")
        # try:
        #     data = RobustScaler().fit_transform(data)
        #     return data
        # except ValueError as err:
        #     print(f"Error with RobustScaling: {err}")

        print("Normalising the dataset using StandardScaler \n")
        try:
            data = StandardScaler().fit_transform(data)
            return data
        except ValueError as err:
            print(f"Error with RobustScaling: {err}")

    @staticmethod
    def __message(message: str):
        if settings.verbose:
            print(message)

    def add_variable(self,
                     var_data: np.ndarray,
                     var_name: str = None,
                     var_index: int = None):

        """Appends a univariate process to the data.

        Args:
            var_data (ndarray):
                Univariate data to add, must be a 1d array with length equal to the number of observations.
            var_name (str, Optional):
                Name of the variable to be added.
            var_index (int, Optional):
                Index to add new variable column. When not specified, variable will be appended.
        """

        var_names = self.__var_names
        if var_name:
            base.check_type(var_name, str)
            if var_name in var_names:
                raise ValueError(f"Variable {var_name} already exists in the data.")

        if var_index:
            base.check_type(var_index, int)
        else:
            var_index = self.n_variables + 1

        base.check_type(var_data, np.ndarray)
        var_data = np.squeeze(var_data)

        if var_data.ndim != 1:
            raise TypeError("Data must be a 1D numpy array.")

        var_data_type = type(var_data[0, 0])
        base.check_type(var_data_type, self.data_type)

        var_data = np.expand_dims(var_data, axis=1)

        if self.normalise:
            var_data = self.__normalise_data(var_data)

        data = copy.deepcopy(self.__base_data)

        if var_index == self.n_variables + 1:
            data = np.append(data, var_data, axis=1)

            if not var_name:
                var_name = f"var-{var_index}"

            self.__var_names.append(var_name)
        else:
            data = np.hstack((data[:, :var_index], var_data, data[:, var_index:]))

            if not var_name:
                var_name = f"var-{var_index}"
                self.__var_names = [*var_names[:var_index],
                                    var_name,
                                    *[f"var-{j}" for j in range(var_index + 1, self.n_variables + 1)]]

        self.__base_data = data
        self.__set_data_dim(data)
        self.__data = self.__subsample_data(data)
        self.__message(f"Variable {var_name} added at position {var_index} to data {self.name} successfully.")
        self.uncache()

    def remove_variable(self,
                        var_indices: Iterable[int]):

        base.check_iterable(var_indices)
        var_indices_list = list(var_indices)
        base.check_type(var_indices_list[0], int)

        try:
            data = copy.deepcopy(self.__base_data)
            data = np.delete(data, var_indices_list, axis=1)

        except IndexError:
            print(
                f"Process {var_indices} is out of bounds of multivariate"
                f" data with size {self.n_variables}.")
            return

        self.__base_data = data
        self.__set_data_dim(data)
        self.__data = self.__subsample_data(data)
        self.__message(f"Variables removed from the data {self.name} successfully.")
        self.__set_data_dim(self.__data)

    @staticmethod
    def __reorder_data(data: np.ndarray,
                       dim_order: str):

        """Reorder dataset dimensions n realisations in p variables."""

        # reorder array dims if necessary
        if dim_order[0] != "n":
            return data.swapaxes(0, 1)

        return data

    def __set_data_dim(self,
                       data: np.ndarray):

        """Set the dataset size."""
        self.__n = data.shape[0]
        self.__p = data.shape[1]

    def uncache(self, include_gc: bool = False):
        Statistic.uncache(self, include_gc)

    @staticmethod
    def load_data(name: str):
        # TODO: MODIFY TO PARSE MY SYNTHETIC DATA NPY'S?
        basedir = os.path.join(os.path.dirname(__file__), "dataset")
        if name == "forex":
            filename = "forex.npy"
            dim_order = "pn"
        elif name == "cml":
            filename = "cml.npy"
            dim_order = "pn"
        else:
            raise NameError(f"Unknown dataset: {name}.")

        path = os.path.join(basedir, filename)
        dataset = np.load(path)
        return Dataset(data=dataset, dim_order=dim_order)

    def __getitem__(self, item: Union[int, tuple[int, ...]]):
        return self.data[item]
