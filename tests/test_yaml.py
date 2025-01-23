import yaml
import os

yaml_dict = yaml.load("""
name : John
age : 30
automobiles:
- brand: Honda
  type: Odyssey
  year: 2018
- brand: Toyota
  type: Sienna
  year: 2015
""", yaml.FullLoader)

print(yaml_dict)

with open(os.getcwd() + "\\pyspc\\run_config\\fabfour_config.yaml") as f:
    yaml_dict = yaml.load(f, yaml.FullLoader)
    print(type(f))

print(yaml_dict)