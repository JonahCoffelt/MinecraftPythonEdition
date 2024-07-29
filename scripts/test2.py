import numpy as np
from numba import njit


@njit
def compress(array):
    i = 0

    while i + 1 < len(array) and array[i][0]:
        i += 1

    while i + 1 < len(array) and array[i + 1][0]:
        array[i] = array[i + 1]
        i += 1

    array[i] = [0, 0, 0, 0]

    return array

my_array = np.zeros(shape=(4, 4))

my_array[0] = [1, 1, 1, 1]
my_array[1] = [1, 1, 1, 1]
my_array[2] = [3, 3, 3, 3]

my_array = compress(my_array)

print(my_array)