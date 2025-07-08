import copy

import numpy as np

mat1 = np.ones(shape=(3,3))
mat2 = copy.deepcopy(mat1)

hash_test = {
    id(mat1): "ye",
    id(mat2): "yo"
}

hash_test.get(id(mat2))