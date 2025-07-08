from __future__ import annotations
#
import numpy as np
import warnings
import pandas as pd
import os
import yaml
import inspect

from scipy.stats import zscore
from typing import Iterable, Union, Generator, Any, TYPE_CHECKING
from abc import ABC, abstractmethod
from textwrap import dedent

if TYPE_CHECKING:
    from pyspoc.config import Config

# GLOBAL SETTINGS
IGNORE_IMPORT_WARNINGS = False

# URLs
PYSS_GITHUB_ISSUES_URL = "https://github.com/cosmicbhejafry/py-spoc/issues/"
CUSTOM_COMPONENTS_URL = "https://github.com/cosmicbhejafry/py-spoc/blob/main/README.md"
STATISTIC_FILTERING_URL = ""

class Component(ABC):

    """
    Base object for both Statistic and Reducer components.

    Provides functionality for constructing configuration files.
    """

    def __init__(self):

        name = self.__get_property_val(self.name)
        check_type(name, str)

        labels = self.__get_property_val(self.labels)
        check_iterable(labels, str)

        self.__cfg: Union[Config, None] = None
        self.__scheme: Union[str, None] = None

    def __new__(cls, *args, **kwargs):

        # Get class arguments
        arg_dict = dict()
        arg_list = list(args)
        arg_spec = inspect.getfullargspec(cls.__init__)
        arg_names = [arg for arg in arg_spec.args if arg != "self"]
        arg_defaults = list(arg_spec.defaults) if arg_spec.defaults else list()
        n_args = len(arg_names)

        # Set defaults in dict
        for i in range(n_args, 0, -1):
            arg_name = arg_names[i - 1]
            default = arg_defaults.pop() if arg_defaults else None
            arg_dict[arg_name] = default

        if arg_spec.kwonlydefaults:
            arg_dict.update(arg_spec.kwonlydefaults)

        # Get arg values
        for i, arg in enumerate(arg_list):
            arg_name = arg_names[i]
            arg_dict[arg_name] = arg

        # Get kwarg values
        for kwarg_name, kwarg in kwargs.items():
            arg_dict[kwarg_name] = kwarg

        instance = super().__new__(cls)
        instance.__params = arg_dict
        return instance

    def set_config(self, cfg: Config):
        self.__cfg = cfg

    @property
    def cfg(self):
        return self.__cfg

    def set_scheme(self, scheme: str):
        self.__scheme = scheme

    @property
    def scheme(self):
        return self.__scheme

    @property
    def params(self) -> dict:
        return self.__params

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def identifier(self) -> str:
        pass

    @property
    @abstractmethod
    def labels(self) -> list[str]:
        pass

    @staticmethod
    def __get_property_val(prop: Any) -> Any:
        while callable(prop):
            prop = prop()

        return prop

    @staticmethod
    @abstractmethod
    def _get_component_type() -> type:
        pass

    @abstractmethod
    def compute(self, data: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def calculate(self, data: np.ndarray) -> np.ndarray:
        pass

    def __str__(self):
        self_type = type(self)
        full_name = get_fully_qualified_type_name(self_type)
        cfg_name = self.cfg.name if self.cfg is not None else "None"
        component_type_name = self._get_component_type().__name__

        return dedent(
            f"""
            {component_type_name}: {full_name}
            Name: {self.name}
            Active Parameters: {self.params}
            Associated Configuration: {cfg_name}
            """)

    @classmethod
    def __info__(cls):
        self_type = type(cls)
        full_name = get_fully_qualified_type_name(self_type)
        component_type_name = cls._get_component_type().__name__
        args = get_obj_init_args(self_type)
        required_args = list()
        optional_args = dict()

        for arg, default in args.items():
            if default:
                optional_args[arg] = default
            else:
                required_args.append(arg)

        return dedent(
            f"""
            {component_type_name}: {full_name}
            Name: {cls.name}
            Required Parameters: {required_args}
            Optional Parameters: {optional_args}
            """)


def info(component: Component):
    if getattr(component, "__info__"):
        print(component.__info__())


def get_fully_qualified_type_name(type_obj: type):

    try:
        module_name = type_obj.__module__ + "."
    finally:
        pass

    if not module_name:
        return type_obj.__name__

    return module_name + type_obj.__name__


def has_required_func_args(func: function) -> bool:
    pars = inspect.signature(func).parameters

    for arg_name, par in pars.items():
        if arg_name == "self":
            continue

        if par.default is inspect._empty:
            return True
        
    return False


def get_obj_init_args(class_obj: type) -> dict[str, Any]:

    # Get class init argument specification
    arg_spec = inspect.getfullargspec(class_obj.__init__)
    args = dict()

    # Add standard args
    n_defaults = len(arg_spec.defaults) if arg_spec.defaults else 0

    optional_args = arg_spec.args[-n_defaults:] if n_defaults > 0 else list()
    required_args = arg_spec.args[:-n_defaults] if n_defaults > 0 else arg_spec.args

    for arg in required_args:
        args[arg] = None
    
    for i, arg in enumerate(optional_args):
        args[arg] = arg_spec.defaults[i]

    # Add keyword arguments
    has_defaults = arg_spec.kwonlydefaults is not None

    for i, arg in enumerate(arg_spec.kwonlyargs):
        args[arg] = arg_spec.kwonlydefaults.get(arg) if has_defaults else None

    args.pop("self", None)
    return args


def retrieve_arg_name(var, max_steps: int = 2):
    frame = inspect.currentframe()
    steps = 0
    var_name = None

    while steps < max_steps:
        frame = frame.f_back
        local_vars = frame.f_locals.items()
        var_names = [var_name for var_name, var_val in local_vars if var_val is var]
        steps += 1

        if var_names:
            var_name = var_names[0]
        else:
            break

    return var_name


def get_type_name(arg_val):
    return type(arg_val).__name__


def check_type(arg_val: object,
               arg_types: Union[type, Iterable[type]],
               arg_name: str = None,
               is_try: bool = False,
               custom_error_msg: str = None) -> Union[None, bool]:

    if not arg_name:
        arg_name = retrieve_arg_name(arg_val)

    if not isinstance(arg_types, Iterable):
        arg_types = [arg_types]
    
    type_names = list()

    for arg_type in arg_types:    
        type_name = arg_type.__name__
        type_names.append(type_name)
    
        if isinstance(arg_val, arg_type):
            return True
            
    if is_try:
        return False

    actual_type = get_type_name(arg_val)

    if custom_error_msg is not None:
        raise TypeError(custom_error_msg)

    raise TypeError(f"{arg_name} should be one of {type_names} types, received {actual_type}.")

    if is_try:
        return True


def check_iterable(iterable: Iterable,
                   iterable_type: Union[type, None] = None,
                   arg_name: str = None,
                   is_try: bool = False,
                   custom_error_msg: str = None) -> Union[None, bool]:

    if not arg_name:
        arg_name = retrieve_arg_name(iterable)

    try:
        iterator = iter(iterable)

    except TypeError:
        if is_try:
            return False

        if custom_error_msg is not None:
            raise TypeError(custom_error_msg)

        raise TypeError(f"{arg_name} should be an iterable type but type {type(iterable)} does not support iteration.")

    if not iterable_type:
        if is_try:
            return True

        return

    element = iterator.__next__()
    is_correct_type = check_type(arg_name=arg_name, arg_types=iterable_type, arg_val=element, is_try=True)

    if not is_correct_type:
        if is_try:
            return False

        expected_type = iterable_type.__name__
        actual_type = get_type_name(element)
        raise TypeError(f"{arg_name} should be an Iterable[{expected_type}] type but got Iterable[{actual_type}]")

    if is_try:
        return True


def check_natural_number(arg_value: int,
                         arg_name: str = None,
                         is_try: bool = False) -> Union[None, bool]:

    if not arg_name:
        arg_name = retrieve_arg_name(arg_value)

    if arg_value < 1:
        if is_try:
            return False

        raise ValueError(f"{arg_name} should be a positive integer value, received {arg_value}.")

    if is_try:
        return True


def _contains_nan(a, nan_policy='propagate'):
    policies = ['propagate', 'raise', 'omit']
    if nan_policy not in policies:
        raise ValueError("nan_policy must be one of {%s}" %
                         ', '.join("'%s'" % s for s in policies))
    try:
        # Calling np.sum to avoid creating a huge array into memory
        # e.g. np.isnan(a).any()
        with np.errstate(invalid='ignore'):
            contains_nan = np.isnan(np.sum(a))
    except TypeError:
        # If the check cannot be properly performed we fall back to omitting
        # nan values and raising a warning. This can happen when attempting to
        # sum things that are not numbers (e.g. as in the function `mode`).
        contains_nan = False
        nan_policy = 'omit'
        warnings.warn("The input array could not be properly checked for nan "
                      "values. nan values will be ignored.", RuntimeWarning)

    if contains_nan and nan_policy == 'raise':
        raise ValueError("The input contains nan values")

    return contains_nan, nan_policy


def strshort(instr,mlength):
    """Shorten a string using ellipsis
    """
    if isinstance(instr,list):
        outstr = []
        for i in range(len(instr)):
            cstr = instr[i]
            outstr.append((cstr[:mlength-6] + '...' + cstr[-3:]) if len(cstr) > mlength else cstr)
    else:
        outstr = (instr[:mlength-6] + '...' + instr[-3:]) if len(instr) > mlength else instr
    return outstr


def acf(x,mode='positive'):
    """Return the autocorrelation function
    """
    if x.ndim > 1:
        x = np.squeeze(x)

    x = zscore(x)
    acf = np.correlate(x,x,mode='full')
    acf = acf / acf[acf.size//2]

    if mode == 'positive':
        return acf[acf.size//2:]
    else:
        return acf


def swap_chars(s, i_1, i_2):
    """Swap to characters in a string.

    Example:
        >>> print(swap_chars('heLlotHere', 2, 6))
        'heHlotLere'
    """
    if i_1 > i_2:
        i_1, i_2 = i_2, i_1
    return ''.join([s[0:i_1], s[i_2], s[i_1+1:i_2], s[i_1], s[i_2+1:]])


def normalise(a, axis=0, nan_policy='propogate'):

    contains_nan, nan_policy = _contains_nan(a, nan_policy)

    if contains_nan and nan_policy == 'omit':
        return (a - np.nanmin(a,axis=axis)) / (np.nanmax(a,axis=axis) - np.nanmin(a,axis=axis))
    else:
        return (a - np.min(a,axis=axis)) / (np.max(a,axis=axis) - np.min(a,axis=axis))


def standardise(a, dimension=0, df=1):
    """Z-standardise a numpy array along a given dimension.

    Standardise array along the axis defined in dimension using the denominator
    (N - df) for the calculation of the standard deviation.

    Args:
        a : numpy array
            dataset to be standardised
        dimension : int [optional]
            dimension along which array should be standardised
        df : int [optional]
            degrees of freedom for the denominator of the standard derivation

    Returns:
        numpy array
            standardised dataset
    """
    # Avoid division by standard deviation if the process is constant.
    a_sd = a.std(axis=dimension, ddof=df)

    if np.isclose(a_sd, 0):
        return a - a.mean(axis=dimension)
    else:
        return (a - a.mean(axis=dimension)) / a_sd


def convert_mdf_to_ddf(df):
    ddf = pd.pivot_table(data=df.stack(dropna=False).reset_index(),index='Dataset',columns=['SPI-1', 'SPI-2'],dropna=False).T.droplevel(0)
    return ddf


def is_jpype_jvm_available():
    """Check whether a JVM is accessible via Jpype"""
    try:
        import jpype as jp
        if not jp.isJVMStarted():
            jarloc = (os.path.dirname(os.path.abspath(__file__)) + "/lib/jidt/infodynamics.jar")
            # if JVM not started, start a session
            print(f"Starting JVM with java class {jarloc}.")
            jp.startJVM(jp.getDefaultJVMPath(), "-ea", "-Djava.class.path=" + jarloc)
        return True
    except Exception as e:
        print(f"Jpype JVM not available: {e}")
        return False


def is_octave_available():
    """Check whether octave is available"""
    try:
        from oct2py import Oct2Py
        oc = Oct2Py()
        oc.exit()
        return True
    except Exception as e:
        print(f"Octave not available: {e}")
        return False


def get_available_optional_deps():
    """Bundle all the optional dependency checks together."""

    optional_deps = list()
    if is_octave_available():
        optional_deps.append("octave")

    if is_jpype_jvm_available():
        optional_deps.append("java")

    return optional_deps


def filter_spis(keywords, output_name = None, configfile= None):
    """
    Filter a YAML using a list of keywords, and save the reduced set as a new
    YAML with a user-specified name (or a random one if not provided) in the
    current directory.

    Args:
        keywords (list): A list of keywords (as strings) to filter the YAML.
        output_name (str, optional): The desired name for the output file. Defaults to a random name. 
        configfile (str, optional): The path to the input YAML file. Defaults to the `config.yaml' in the pyspi dir. 

    Raises:
        ValueError: If `keywords` is not a list or if no SPIs match the keywords.
        FileNotFoundError: If the specified `configfile` or the default `config.yaml` is not found.
        IOError: If there's an error reading the YAML file.
    """
    # handle invalid keyword input
    if not keywords:
        raise ValueError("At least one keyword must be provided.")
    if not all(isinstance(keyword, str) for keyword in keywords):
        raise ValueError("All keywords must be strings.")
    if not isinstance(keywords, list):
        raise ValueError("Keywords must be provided as a list of strings.")

    # if no configfile and no keywords are provided, use the default 'config.yaml' in pyspi location
    if configfile is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_config = os.path.join(script_dir, 'config.yaml')
        if not os.path.isfile(default_config):
            raise FileNotFoundError(f"Default 'config.yaml' file not found in {script_dir}.")
        configfile = default_config
        source_file_info = f"Default 'config.yaml' file from {script_dir} was used as the source file."
    else:
        source_file_info = f"User-specified config file '{configfile}' was used as the source file."

    # load in user-specified yaml
    try:
        with open(configfile) as f:
            yf = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file '{configfile}' not found.")
    except Exception as e:
        # handle all other exceptions
        raise IOError(f"An error occurred while trying to read '{configfile}': {e}")

    # new dictionary to be converted to final YAML
    filtered_subset = {}
    spis_found = 0
    
    for module in yf:
        module_spis = {}
        for spi in yf[module]:
            spi_labels = yf[module][spi].get('labels')
            if all(keyword in spi_labels for keyword in keywords):
                module_spis[spi] = yf[module][spi]
                if yf[module][spi].get('configs'):
                    spis_found += len(yf[module][spi].get('configs'))
                else:
                    spis_found += 1
    
        if module_spis:
            filtered_subset[module] = module_spis
    
    # check that > 0 SPIs found
    if spis_found == 0:
        raise ValueError(f"0 SPIs were found with the specific keywords: {keywords}.")
    
    # construct output file path
    if output_name is None:
        # use a unique name
        output_name = "config_" + os.urandom(4).hex()

    output_file = os.path.join(os.getcwd(), f"{output_name}.yaml")
    
    # write to YAML
    with open(output_file, "w") as outfile:
        yaml.dump(filtered_subset, outfile, default_flow_style=False, sort_keys=False)

    # output relevant information
    print(f"""\nOperation Summary:
-----------------
- {source_file_info}
- Total SPIs Matched: {spis_found} SPI(s) were found with the specific keywords: {keywords}.
- New File Created: A YAML file named `{output_name}.yaml` has been saved in the current directory: `{output_file}'
- Next Steps: To utilise the filtered set of SPIs, please initialise a new Calculator instance with the following command:
`Calculator(configfile='{output_file}')`
""")


def inspect_calc_results(calc):
    total_num_spis = calc.n_ss
    num_vars = calc.dataset.n_variables_subsample
    ss_results = dict({'Successful': list(), 'NaNs': list(), 'Partial NaNs': list()})
    for key in calc.ss.keys():
        if calc.results[key].isna().all().all():
            ss_results['NaNs'].append(key)

        elif calc.results[key].isnull().values.sum() > num_vars:
            # off-diagonal NaNs
            ss_results['Partial NaNs'].append(key)

        else:
            # returned numeric values (i.e., not NaN)
            ss_results['Successful'].append(key)
    
    # print summary
    double_line_60 = "="*60
    single_line_60 = "-"*60
    print("\nSPI Computation Results Summary")
    print(double_line_60)
    print(f"\nTotal number of SPIs attempted: {total_num_spis}")
    print(f"Number of SPIs successfully computed: {len(ss_results['Successful'])} "
          f"({len(ss_results['Successful']) / total_num_spis * 100:.2f}%)")
    print(single_line_60)
    print("Category       | Count | Percentage")
    print(single_line_60)

    for category, spis in ss_results.items():
        count = len(spis)
        percentage = (count / total_num_spis) * 100
        print(f"{category:14} | {count:5} | {percentage:6.2f}%")

    print(single_line_60)

    if ss_results['NaNs']:
        print(f"\n[{len(ss_results['NaNs'])}] SPI(s) produced NaN outputs:")
        print(single_line_60)
        for i, spi in enumerate(ss_results['NaNs']):
            print(f"{i+1}. {spi}")
        print(single_line_60 + "\n")

    if ss_results['Partial NaNs']:
        print(f"\n[{len(ss_results['Partial NaNs'])}] SPIs which produced partial NaN outputs:")
        print(single_line_60)
        for i, spi in enumerate(ss_results['Partial NaNs']):
            print(f"{i+1}. {spi}")
        print(single_line_60 + "\n")
    