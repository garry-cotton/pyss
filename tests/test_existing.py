import importlib
import pyspc.data as data
importlib.reload(data)

test_data = data.load_dataset("forex")
#test_data.n_variables

test_data.n_realisations