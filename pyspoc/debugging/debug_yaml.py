import yaml
import os
import inspect

import importlib
import importlib.resources as imp_resources
from pyspoc import reducers


test_file = "C:/Users/Garry/Research Projects/pyss/pyspoc/run_config/testing.yaml"

with open(test_file, "r") as f:
    result = yaml.load(f, yaml.FullLoader)

print(result)

stats = result.get("Statistics")

if not stats:
    raise ValueError(f"Yaml file {test_file} is missing required definition for Statistics.")

if type(stats) is not dict:
    raise ValueError(f"Yaml file {test_file} contains incorrect format for Statistics definition.")

reducer_dict = result.get("Reducers")

if not reducer_dict:
    raise ValueError(f"Yaml file {test_file} is missing required definition for Reducers.")

if type(reducer_dict) is not dict:
    raise ValueError(f"Yaml file {test_file} contains incorrect format for Reducers definition.")

#for module, stat in stats.items():

imp_file = importlib.resources.files(reducers)
for thing in imp_file.iterdir():
    if thing.is_file():
        file_name = os.path.splitext(thing.name)[0]
        if file_name == "basic":
            module_name = "reducers." + file_name
            print(module_name)
            #importlib.import_module(module_name, __package__)