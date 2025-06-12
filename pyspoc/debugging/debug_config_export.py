from pyspoc.config import Config

cfg = Config.from_yaml_file("tehe", "..\\run_config\\testing.yaml")
cfg.export_yaml("..\\run_config\\woohoo.yaml")