import numpy as np
from numba import njit
import array


@njit (fastmath=True)
def get_sky_light(voxels):
    sky_light = np.zeros(shape=voxels.shape, dtype='i8')

    max_light_level = 15
    max_height = voxels.shape[1] - 1
    min_terrain_height = voxels.shape[1]

    for x in range(voxels.shape[0]):
        for z in range(voxels.shape[2]):
            y = max_height
            while y > 0 and voxels[x][y][z] == 0:
                y -= 1
            sky_light[x,y+1:,z] = max_light_level
            min_terrain_height = min(min_terrain_height, y)

    return sky_light, min_terrain_height


@njit
def cascade_skylight(voxels):
    chunks_light, min_terrain_height = get_sky_light(voxels)

    max_light_level = 15

    flood_fill_light = [(0, 0, 0, 0)]

    pop_index = 1

    for x in range(voxels.shape[0]):
        for z in range(voxels.shape[2]):
            for y in range(min_terrain_height, voxels.shape[1]):
                if chunks_light[x][y][z] == 0: continue
                
                do_break = True

                if x + 1 < voxels.shape[0]:
                    if chunks_light[x + 1][y    ][z    ] == 0: flood_fill_light.append((x + 1, y    , z    , max_light_level - 1))
                    if chunks_light[x + 1][y    ][z    ] != 15: do_break = False
                
                if 0 <= x - 1:
                    if chunks_light[x - 1][y    ][z    ] == 0: flood_fill_light.append((x - 1, y    , z    , max_light_level - 1))
                    if chunks_light[x - 1][y    ][z    ] != 15: do_break = False
                
                if z + 1 < voxels.shape[2]:
                    if chunks_light[x    ][y    ][z + 1] == 0: flood_fill_light.append((x    , y    , z + 1, max_light_level - 1))
                    if chunks_light[x    ][y    ][z + 1] != 15: do_break = False
                
                if 0 <= z - 1:
                    if chunks_light[x    ][y    ][z - 1] == 0: flood_fill_light.append((x    , y    , z - 1, max_light_level - 1))
                    if chunks_light[x    ][y    ][z - 1] != 15: do_break = False

                if do_break: break

    while pop_index < len(flood_fill_light):
        x, y, z, light_level = flood_fill_light[pop_index]
        pop_index += 1

        if voxels[x][y][z] != 0: continue
        
        if not (0 <= x < voxels.shape[0] and 0 <= y < voxels.shape[1] and 0 <= z < voxels.shape[2]): continue
        if light_level <= chunks_light[x][y][z]: continue


        chunks_light[x][y][z] = light_level

        if light_level == 1: continue

        if x + 1 < voxels.shape[0]:
            if light_level > chunks_light[x + 1][y    ][z    ]: flood_fill_light.append((x + 1, y    , z    , light_level - 1))

        if 0 <= x - 1:
            if light_level > chunks_light[x - 1][y    ][z    ]: flood_fill_light.append((x - 1, y    , z    , light_level - 1))
        
        if y + 1 < voxels.shape[1]:
            if light_level > chunks_light[x    ][y + 1][z    ]: flood_fill_light.append((x    , y + 1, z    , light_level - 1))

        if 0 <= y - 1:
            if light_level > chunks_light[x    ][y - 1][z    ]: flood_fill_light.append((x    , y - 1, z    , light_level - 1))
        
        if z + 1 < voxels.shape[2]:
            if light_level > chunks_light[x    ][y    ][z + 1]: flood_fill_light.append((x    , y    , z + 1, light_level - 1))

        if 0 <= z - 1:
            if light_level > chunks_light[x    ][y    ][z - 1]: flood_fill_light.append((x    , y    , z - 1, light_level - 1))

    return chunks_light