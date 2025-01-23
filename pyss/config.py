from __future__ import annotations

import yaml
import warnings
import io
import os
import re
import inspect
import importlib

from typing import Union, Iterable
from types import ModuleType
from runpy import run_path
from argparse import Namespace

from pyss.base import Component, check_type, check_iterable, get_available_optional_deps, get_obj_init_args
from pyss.statistic import Statistic
from pyss.reducer import Reducer


class Config:

    """
    Provides a construct for run configurations.

    Existing configurations can be imported via:
        - a YAML configuration file.
        - a JSON configuration file.
        - an in-memory dict object.

    Configurations can be modified or new configurations constructed using provided methods.

    Current configuration state can be exported to YAML or JSON files for later use.

    Arguments:
        name (string): Unique name for the configuration. This allows a single Calculator class to serve
        multiple configurations.
    """

    TICK_CHAR = u'\u2714'
    CROSS_CHAR = u'\u2716'

    __cached_modules = dict()
    __cached_module_classes = dict()
    __available_dependencies = get_available_optional_deps()

    def __init__(self, name: str):

        self.__name = name
        self.__config_dict = dict()
        self.__config_scheme = {
            "Statistic" : dict(),
            "Reducer": dict()
        }
        self.__reducer_filters = dict()

        if "Statistic" not in self.__cached_module_classes:
            self.__cached_module_classes["Statistic"] = dict()

        if "Reducer" not in self.__cached_module_classes:
            self.__cached_module_classes["Reducer"] = dict()

    @property
    def name(self) -> str:
        return self.__name

    def scheme(self):
        return self.__config_scheme

    @property
    def statistics(self) -> dict:
        return self.__config_scheme.get("Statistic")

    @property
    def reducers(self) -> dict:
        return self.__config_scheme.get("Reducer")

    def get_reducer_filters(self, reducer: Reducer) -> dict:
        return self.__reducer_filters.get(reducer)

    @classmethod
    def from_yaml(cls, name: str, yaml: str):
        instance = cls(name)
        print("Registering YAML string.")
        instance.__config_dict = cls.__load_yaml(yaml)
        instance.__process_config_file()
        return instance

    @classmethod
    def from_yaml_file(cls, name: str, yaml_file_path: str):
        instance = cls(name)
        print("Registering YAML configuration file: {}.".format(yaml_file_path))
        instance.__config_dict = cls.__load_yaml_file(yaml_file_path)
        instance.__process_config_file()
        return instance

    @classmethod
    def __load_yaml_file(cls, yaml_path: str) -> dict:
        # Load file and pass text stream to load method
        with open(yaml_path) as f:
            return cls.__load_yaml(f)

    @staticmethod
    def __load_yaml(yaml_stream: Union[io.TextIOWrapper, str]) -> dict:
        # Parse yaml as dict object
        return yaml.load(yaml_stream, Loader=yaml.FullLoader)

    @classmethod
    def from_dict(cls, name: str, config_dict: dict):
        instance = cls(name)
        print("Registering configuration dictionary object.")
        instance.__config_dict = config_dict
        instance.__process_config_file()
        return instance

    @classmethod
    def from_json_file(cls, name: str, json_file_path: str):
        instance = cls(name)
        print("Registering YAML configuration file: {}.".format(json_file_path))
        instance.__config_dict = cls.__load_json_file(json_file_path)
        instance.__process_config_file()
        return instance

    @classmethod
    def __load_json_file(cls, json_path: str) -> dict:
        # Load file and pass text stream to load method
        with open(json_path) as f:
            return cls.__load_yaml(f)

    def add_statistic(self,
                      statistic: Statistic,
                      scheme_name: str):

        self.__add_component(statistic, Statistic, scheme_name)

    def add_reducer(self,
                    reducer: Reducer,
                    scheme_name: str,
                    statistics: Union[None, str, Iterable[str]] = None):

        self.__add_component(reducer, Reducer, scheme_name)

        if statistics:
            self.__add_reducer_statistic_filters(reducer, statistics)

    def remove_statistic(self, statistic: Statistic):
        self.__remove_component(statistic, Statistic)

    def remove_statistic_by_name(self, module_reference: str, statistic_name: str, scheme_name: str):
        self.__remove_component_by_name(Statistic, module_reference, statistic_name, scheme_name)

    def remove_reducer(self, reducer: Reducer):
        reducer = self.__remove_component(reducer, Reducer)
        self.__reducer_filters.pop(reducer, None)

    def remove_reducer_by_name(self, module_reference: str, reducer_name: str, scheme_name: str):
        reducer = self.__remove_component_by_name(Reducer, module_reference, reducer_name, scheme_name)

        if reducer:
            self.__reducer_filters.pop(reducer, None)

    def __add_component(self,
                        component: Component,
                        component_archetype: type,
                        scheme_name: str):

        module = inspect.getmodule(component)
        module_reference = self.__get_component_module_name(component)
        component_type = type(component)
        component_type_name = component_type.__name__

        if module_reference not in self.__cached_modules:
            self.__cached_modules[module_reference] = module

        component.set_scheme(scheme_name)
        component_archetype_name = component_archetype.__name__
        full_component_name = self.__get_full_component_name(module_reference, component_type_name)
        self.__cached_module_classes[component_archetype_name][full_component_name] = component_type

        full_instance_name = self.__get_full_instantiated_name(module_reference,
                                                               component_type_name,
                                                               scheme_name)

        if full_instance_name in self.__config_scheme[component_archetype_name]:
            raise ValueError(f"{component_archetype_name} {full_instance_name} already exists.")

        self.__config_scheme[component_archetype_name][full_instance_name] = component
        print(f"  {self.TICK_CHAR} {component_archetype_name} {component_type_name} scheme '{scheme_name}' "
              f"added successfully.")

    def __remove_component(self,
                           component: Component,
                           component_archetype: type):

        module_reference = self.__get_component_module_name(component)
        component_type = type(component)
        component_type_name = component_type.__name__
        scheme_name = component.scheme
        return self.__remove_component_by_name(component_archetype,
                                               module_reference,
                                               component_type_name,
                                               scheme_name)

    def __remove_component_by_name(self,
                                   component_archetype: type,
                                   module_reference: str,
                                   component_type_name: str,
                                   scheme_name: str):

        component_archetype_name = component_archetype.__name__
        full_instance_name = self.__get_full_instantiated_name(module_reference,
                                                               component_type_name,
                                                               scheme_name)
        result = self.__config_scheme[component_archetype_name].pop(full_instance_name, None)

        if result:
            component_type_name = type(result).__name__
            scheme_name = result.scheme
            print(f"  {component_archetype_name} {component_type_name} scheme '{scheme_name}' "
                  f"removed successfully.")
            return result

    # TODO: Create yaml export function for the loaded configuration.
    def get_yaml(self):
        statistics = self.statistics.values()

        if not statistics:
            warnings.warn("No Statistics have been loaded. Skipping.")
            return

        reducers = self.reducers.values()

        if not reducers:
            warnings.warn("No Reducers have been loaded. Skipping.")
            return

        yaml_dict = {
            "Statistics": dict(),
            "Reducers": dict()
        }

        for stat in statistics:
            self.__add_export_component(yaml_dict, stat, Statistic)

        for reducer in reducers:
            self.__add_export_component(yaml_dict, reducer, Reducer)
            self.__add_export_reducer_statistic_filters(yaml_dict, reducer)

        yaml_text = yaml.dump(yaml_dict, sort_keys=False)
        return yaml_text

    def export_yaml(self, export_path: str = None):
        yaml_text = self.get_yaml()

        if not yaml_text:
            return

        if export_path is None:
            export_path = os.getcwd() + f"\\{self.name}.yaml"

        with open(export_path, "w") as f:
            f.write(yaml_text)

    def __add_export_component(self, yaml_dict: dict, component: Component, component_archetype: type):
        component_archetype_name = component_archetype.__name__ + "s"
        module_name = self.__get_component_module_name(component)
        scheme_name = component.scheme
        params = component.params

        if module_name not in yaml_dict[component_archetype_name]:
            yaml_dict[component_archetype_name][module_name] = dict()

        module_dict = yaml_dict[component_archetype_name][module_name]
        component_name = type(component).__name__

        if component_name not in module_dict:
            module_dict[component_name] = dict()
            module_dict[component_name]["schemes"] = dict()

        schemes_dict = module_dict[component_name]["schemes"]
        schemes_dict[scheme_name] = params

    def __add_export_reducer_statistic_filters(self, yaml_dict: dict, reducer: Reducer):
        reducer_dict = yaml_dict["Reducers"]
        module_name = self.__get_component_module_name(reducer)
        module_dict = reducer_dict[module_name]
        reducer_name = type(reducer).__name__
        applicable_stats = self.get_reducer_filters(reducer)

        if applicable_stats:
            module_dict[reducer_name]["Statistics"] = list(applicable_stats)

    def __process_config_file(self):
        print(f"Building internal configuration.")
        stats_spec = self.__get_config_top_level("Statistics")
        reducers_spec = self.__get_config_top_level("Reducers")
        self.__build_config_scheme(stats_spec, reducers_spec)

    def __get_config_top_level(self, level_name: str):
        level_dict = self.__config_dict.get(level_name)

        if not level_dict:
            raise ValueError(f"Configuration is missing required definition for {level_name}.")

        check_type(level_dict,
                   dict,
                   custom_error_msg=f"Configuration contains incorrect format for {level_name} definition.")

        return {module.lower(): component_config for module, component_config in level_dict.items()}

    def __build_config_scheme(self, stats_spec: dict, reducers_spec: dict):

        # Initialise the config scheme
        self.__config_scheme = {
            "Statistic": dict(),
            "Reducer": dict()
        }

        # Get instantiated Statistics based on configuration
        stats_generator = self.__yield_instantiated_components(Statistic, stats_spec)

        # Store each Statistic
        for stat, scheme_name, stat_params in stats_generator:
            self.__add_component(stat, Statistic, scheme_name)

        # Get instantiated Reducers based on configuration
        reducers_generator = self.__yield_instantiated_components(Reducer, reducers_spec)

        # Store each Reducer and all viable Statistic names after filtering
        for reducer, scheme_name, reducer_params in reducers_generator:
            self.__add_component(reducer, Reducer, scheme_name)
            statistics = reducer_params.get("Statistics")
            self.__add_reducer_statistic_filters(reducer, reducer_params)

    def __yield_instantiated_components(self,
                                        component_archetype: type,
                                        component_spec: dict) -> tuple[str, Union[Statistic, Reducer], dict]:

        component_archetype_name = component_archetype.__name__

        # Cycle through modules and components
        for module_reference, module_components in component_spec.items():

            # Check module components is a dictionary
            check_type(module_components,
                       dict,
                       custom_error_msg=f"Incorrect format for {component_archetype_name}s definition.")

            module = self.__get_module(module_reference)

            # Cycle through components and component parameters
            for component_name, component_params in module_components.items():

                component_class = self.__get_component_class(component_archetype,
                                                             component_name,
                                                             component_params,
                                                             module)

                if not component_class:
                    continue

                # Check component params is a dictionary
                check_type(component_params,
                           dict,
                           custom_error_msg=f"Incorrect format for {component_archetype_name} {component_name} "
                                            f"definition under module {module_reference}.")

                # Get the component configurations
                schemes = component_params.get("schemes")

                if not schemes:
                    raise ValueError(f"{component_archetype_name} {component_name} under module {module_reference} "
                                     f"is missing 'schemes' definition.")

                # Check configs is a dictionary
                check_type(schemes,
                           dict,
                           custom_error_msg=f"Incorrect format for {component_archetype_name} {component_name} "
                                            f"'scheme' definition under module {module_reference}.")

                # Cycle config and config parameters
                for scheme_name, scheme_args in schemes.items():

                    # Check config params is a dictionary
                    check_type(scheme_args,
                               dict,
                               custom_error_msg=f"Incorrect format for {component_archetype_name} {component_name} "
                                                f"'schemes' definition under module {module_reference}.")

                    # Get component class init argument specification
                    args = get_obj_init_args(component_class)
                    missing_args = list()

                    # Check all required arguments are provided in the configuration
                    for arg, default in args.items():
                        if arg not in scheme_args and default is None:
                            missing_args.append(arg)

                    # If required arguments are missing, throw error.
                    if missing_args:
                        raise ValueError(f"{component_archetype_name} {component_name} configuration '{scheme_name}' "
                                         + f"under module '{module_reference}' is missing the arguments:"
                                         + f"\n\t"
                                         + "\n\t".join(missing_args))

                    # Instantiate the component class with configured arguments.
                    component: Component = component_class(**scheme_args)

                    # Return the component instance, scheme name and parameters.
                    yield component, scheme_name, component_params

    def __add_reducer_statistic_filters(self,
                                        reducer: Reducer,
                                        statistics: Union[None, str, Iterable[str]]):

        reducer_name = type(reducer).__name__
        filtered_stats = set()

        if not statistics:
            return

        statistic_list = self.__yaml_str_list_to_list(statistics)
        module_name = self.__get_component_module_name(reducer)

        check_iterable(statistic_list,
                       str,
                       custom_error_msg=f"Incorrect format for Reducer {reducer_name} 'Statistics' "
                                        f"definition under module {module_name}.")

        available_stat_names = self.__config_scheme["Statistic"].keys()

        for stat_name in statistic_list:
            esc_stat_name = "^" + re.escape(stat_name).replace("\\*", ".*")
            viable_stat_names = [stat for stat in available_stat_names if re.match(esc_stat_name, stat)]

            for viable_stat_name in viable_stat_names:
                filtered_stats.add(viable_stat_name)

        self.__reducer_filters[reducer] = filtered_stats

    @classmethod
    def __get_module(cls,
                     module_reference: str,
                     global_modules: Union[dict, None] = None,
                     refresh_module: bool = False) -> Union[ModuleType, Namespace]:

        if not global_modules:
            global_modules = {obj.__name__.lower(): obj for obj
                              in globals().values() if inspect.ismodule(obj)}

        # Check if module is already loaded.
        module = cls.__cached_modules.get(module_reference)

        if module:
            print(f"  {cls.TICK_CHAR} Module {module_reference} already loaded.")
            return module

        # Check package modules.
        try:
            module = importlib.import_module(module_reference)
            print(f"  {cls.TICK_CHAR} Module {module_reference} loaded successfully.")
            return module
        except ModuleNotFoundError:
            pass
        except Exception as e:
            raise e

        # Check modules loaded in memory.
        module = global_modules.get(module_reference)

        if module:
            print(f"  {cls.TICK_CHAR} Module {module_reference} loaded from global environment.")
            return module

        # Check module files.
        module = cls.__load_module_file(module_reference,
                                        refresh_module=refresh_module,
                                        suppress_warning=True)

        if module:
            return module

    @classmethod
    def __load_module_file(cls,
                           module_path: str,
                           refresh_module: bool,
                           suppress_warning: bool = False) -> Union[ModuleType, Namespace, None]:

        # Get cached module if available
        module = cls.__cached_modules.get(module_path)

        if module and not refresh_module:
            return module

        # Otherwise check if module path exists
        if not os.path.isfile(module_path) and not suppress_warning:
            warnings.warn(f"No file could be found at the following path: {module_path}")
            return

        # Load and return module
        module_dict = run_path(module_path, run_name=module_path)
        module = Namespace(**module_dict)
        cls.__cached_modules[module_path] = module
        return module

    @classmethod
    def __get_component_class(cls,
                              component_type: type,
                              component_name: str,
                              component_params: dict,
                              module: Union[Namespace, ModuleType]) -> Union[None, type]:

        component_type_name = component_type.__name__
        module_name = cls.__get_module_name(module)
        full_component_name = cls.__get_full_component_name(module_name, component_name)

        # Return cached object if present.
        component_classes = cls.__cached_module_classes.get(component_type_name)

        if component_classes:
            component_class = component_classes.get(full_component_name)

            if component_class:
                return component_class

        # Otherwise check the module directory.
        is_component_exists = component_name in module.__dir__()

        # Skip if not present.
        if not is_component_exists:
            print(f"  {cls.CROSS_CHAR} {component_type_name} {component_name} could not be found. Skipping.")
            return

        # Get object from module
        component_class = getattr(module, component_name)

        # Check object is the expected type
        if not issubclass(component_class, component_type):
            type_name = component_class.__name__
            print(f"  {cls.CROSS_CHAR} {component_type_name} {component_name} is of type {type_name} which "
                  f"is not a {component_type_name} object. Skipping.")
            return

        # Get the component dependencies
        dependencies = component_params.get("dependencies")

        if dependencies:
            dependency_list = cls.__yaml_str_list_to_list(dependencies)
            dependency_set = set(dependency_list)
            missing_dependencies = dependency_set.difference(cls.__available_dependencies)

            if missing_dependencies:
                dependency_delimited = ",".join(dependency_set)
                print(f"  {cls.CROSS_CHAR} {component_type_name} {component_name} is missing dependencies. "
                      f"Skipping")
                print(f"    (Missing dependencies: {dependency_delimited})")
                return

        return component_class

    @classmethod
    def __get_module_name(cls, module: Union[ModuleType, Namespace]):
        module_name = module.__name__
        is_internal = cls.__is_internal_module(module_name)

        if is_internal:
            return module_name

        return module.__file__

    @classmethod
    def __get_component_module_name(cls, component: Component):
        module = inspect.getmodule(component)

        if module:
            return cls.__get_module_name(module)

        return component.__module__

    @staticmethod
    def __is_internal_module(module_reference: str) -> bool:

        try:
            importlib.import_module(module_reference)
            return True
        except ModuleNotFoundError:
            return False
        except Exception as e:
            raise e

    @staticmethod
    def __get_full_component_name(module_name: str, component_type_name: str) -> str:
        return module_name + "." + component_type_name

    @staticmethod
    def __get_full_instantiated_name(module_name: str, component_type_name: str, scheme_name: str) -> str:
        return ".".join([module_name, component_type_name, scheme_name])

    @staticmethod
    def __get_component_name_parts(full_component_name) -> tuple[str, str, str]:
        component_parts = full_component_name.split(".")
        return ".".join(component_parts[:-2]), component_parts[-2], component_parts[-1]

    @staticmethod
    def __yaml_str_list_to_list(str_list: Union[str, list]):
        return re.split(r"\s+", str_list) if isinstance(str_list, str) else str_list
