import sys
import numpy as np
from numba import njit


np_struct = np.dtype([('id', 'i8'), ('facing', 'i4'), ('waterlogged', 'bool'), ('durability', 'i4')])

np_var = np.array([(3, 0, False, 3) for i in range(100)], dtype=np_struct)


@njit
def test_func(np_array):
    print(np_array[0]['id'])


test_func(np_var)
print(f'Numpy : {sys.getsizeof(np_var)}')