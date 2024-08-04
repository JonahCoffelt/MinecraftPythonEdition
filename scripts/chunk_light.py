import numpy as np
from numba import njit
import time


@njit
def get_sky_light(voxels):
    sky_light = np.zeros(shape=voxels.shape, dtype='i8')

    max_light_level = 15
    max_height = voxels.shape[1] - 1

    for x in range(voxels.shape[0]):
        for z in range(voxels.shape[2]):
            y = max_height
            while y > 0 and voxels[x][y][z] == 0:
                sky_light[x][y][z] = max_light_level
                y -= 1

    #while len(check_tiles):
    #    i = 0
    #    while i < len(check_tiles):
    #        x, z = check_tiles[i]
    #        y = height_levels[x][z]
#
    #        if y < 0:
    #            check_tiles.pop(0)
    #            continue
    #        if voxels[x][y][z] != 0:
    #            check_tiles.pop(0)
    #            continue
#
    #        sky_light[x][y][z] = max_light_level
    #        height_levels[x][z] = y - 1
    #        i += 1

    return sky_light

@njit
def cascade_skylight22(voxels):
    chunks_light = get_sky_light(voxels)

    max_light_level = 15

    flood_fill_light = np.zeros(shape=(1000000, 4), dtype='i8')
    flood_index = 0
    pop_index = 0

    for x in range(voxels.shape[0]):
        for y in range(voxels.shape[1]):
            for z in range(voxels.shape[2]):
                if chunks_light[x][y][z] == 0: continue

                if x + 1 < voxels.shape[0]:
                    if chunks_light[x + 1][y    ][z    ] == 0: 
                        flood_fill_light[flood_index][:] = [x + 1, y    , z    , max_light_level - 1]
                        flood_index += 1
                
                if 0 <= x - 1:
                    if chunks_light[x - 1][y    ][z    ] == 0: 
                        flood_fill_light[flood_index][:] = [x - 1, y    , z    , max_light_level - 1]
                        flood_index += 1
                
                if y + 1 < voxels.shape[1]:
                    if chunks_light[x    ][y + 1][z    ] == 0: 
                        flood_fill_light[flood_index][:] = [x    , y + 1, z    , max_light_level - 1]
                        flood_index += 1
                
                if 0 <= y - 1:
                    if chunks_light[x    ][y - 1][z    ] == 0: 
                        flood_fill_light[flood_index][:] = [x    , y - 1, z    , max_light_level - 1]
                        flood_index += 1
                
                if z + 1 < voxels.shape[2]:
                    if chunks_light[x    ][y    ][z + 1] == 0: 
                        flood_fill_light[flood_index][:] = [x    , y    , z + 1, max_light_level - 1]
                        flood_index += 1
                
                if 0 <= z - 1:
                    if chunks_light[x    ][y    ][z - 1] == 0: 
                        flood_fill_light[flood_index][:] = [x    , y    , z - 1, max_light_level - 1]
                        flood_index += 1

    while pop_index < flood_index:
        voxel = flood_fill_light[pop_index]
        pop_index += 1
        x, y, z, light_level = voxel[0], voxel[1], voxel[2], voxel[3]

        if not 0 <= x < voxels.shape[0] or not 0 <= y < voxels.shape[1] or not 0 <= z < voxels.shape[2]: continue
        if light_level <= chunks_light[x][y][z]: continue

        chunks_light[x][y][z] = light_level

        if voxels[x][y][z] != 0: continue

        light_level -= 1
        if not light_level: continue

        if x + 1 < voxels.shape[0]:
            if light_level > chunks_light[x + 1][y    ][z    ]: flood_fill_light[flood_index][:] = [x + 1, y    , z    , light_level]
            flood_index += 1

        if 0 <= x - 1:
            if light_level > chunks_light[x - 1][y    ][z    ]: flood_fill_light[flood_index][:] = [x - 1, y    , z    , light_level]
            flood_index += 1
        
        if y + 1 < voxels.shape[1]:
            if light_level > chunks_light[x    ][y + 1][z    ]: flood_fill_light[flood_index][:] = [x    , y + 1, z    , light_level]
            flood_index += 1
        
        if 0 <= y - 1:
            if light_level > chunks_light[x    ][y - 1][z    ]: flood_fill_light[flood_index][:] = [x    , y - 1, z    , light_level]
            flood_index += 1
        
        if z + 1 < voxels.shape[2]:
            if light_level > chunks_light[x    ][y    ][z + 1]: flood_fill_light[flood_index][:] = [x    , y    , z + 1, light_level]
            flood_index += 1

        if 0 <= z - 1:
            if light_level > chunks_light[x    ][y    ][z - 1]: flood_fill_light[flood_index][:] = [x    , y    , z - 1, light_level]
            flood_index += 1

    return chunks_light


@njit 
def cascade_skylight2(voxels):
    chunks_light = get_sky_light(voxels)

    max_light_level = 15

    flood_fill_light = [(0, 0, 0, 0)]

    pop_index = 1

    for x in range(voxels.shape[0]):
        for y in range(voxels.shape[1]):
            for z in range(voxels.shape[2]):
                if chunks_light[x][y][z] == 0: continue

                if x + 1 < voxels.shape[0]:
                    if chunks_light[x + 1][y    ][z    ] == 0: flood_fill_light.append((x + 1, y    , z    , max_light_level - 1))
                
                if 0 <= x - 1:
                    if chunks_light[x - 1][y    ][z    ] == 0: flood_fill_light.append((x - 1, y    , z    , max_light_level - 1))
                
                if y + 1 < voxels.shape[1]:
                    if chunks_light[x    ][y + 1][z    ] == 0: flood_fill_light.append((x    , y + 1, z    , max_light_level - 1))
                
                if 0 <= y - 1:
                    if chunks_light[x    ][y - 1][z    ] == 0: flood_fill_light.append((x    , y - 1, z    , max_light_level - 1))
                
                if z + 1 < voxels.shape[2]:
                    if chunks_light[x    ][y    ][z + 1] == 0: flood_fill_light.append((x    , y    , z + 1, max_light_level - 1))
                
                if 0 <= z - 1:
                    if chunks_light[x    ][y    ][z - 1] == 0: flood_fill_light.append((x    , y    , z - 1, max_light_level - 1))

    #i = 0
    #while i < len(flood_fill_light):
    #    x, y, z, light_level = flood_fill_light[i]
    #    
    #    if x + 1 < voxels.shape[0]:
    #        if not chunks_light[x + 1][y    ][z    ] == 15: 
    #            i += 1
    #            continue
#
    #    if 0 <= x - 1:
    #        if not chunks_light[x - 1][y    ][z    ] == 15: 
    #            i += 1
    #            continue
    #    
    #    if y + 1 < voxels.shape[1]:
    #        if not chunks_light[x    ][y + 1][z    ] == 15: 
    #            i += 1
    #            continue
#
    #    if 0 <= y - 1:
    #        if not chunks_light[x    ][y - 1][z    ] == 15: 
    #            i += 1
    #            continue
    #    
    #    if z + 1 < voxels.shape[2]:
    #        if not chunks_light[x    ][y    ][z + 1] == 15: 
    #            i += 1
    #            continue
#
    #    if 0 <= z - 1:
    #        if not chunks_light[x    ][y    ][z - 1] == 15: 
    #            i += 1
    #            continue
#
    #    flood_fill_light.pop(i)

    while pop_index < len(flood_fill_light):
        x, y, z, light_level = flood_fill_light[pop_index]
        pop_index += 1

        if not 0 <= x < voxels.shape[0] or not 0 <= y < voxels.shape[1] or not 0 <= z < voxels.shape[2]: continue
        if light_level <= chunks_light[x][y][z]: continue

        chunks_light[x][y][z] = light_level

        if voxels[x][y][z] != 0: continue

        light_level -= 1
        if not light_level: continue

        if x + 1 < voxels.shape[0]:
            if light_level > chunks_light[x + 1][y    ][z    ]: flood_fill_light.append((x + 1, y    , z    , light_level))

        if 0 <= x - 1:
            if light_level > chunks_light[x - 1][y    ][z    ]: flood_fill_light.append((x - 1, y    , z    , light_level))
        
        if y + 1 < voxels.shape[1]:
            if light_level > chunks_light[x    ][y + 1][z    ]: flood_fill_light.append((x    , y + 1, z    , light_level))

        if 0 <= y - 1:
            if light_level > chunks_light[x    ][y - 1][z    ]: flood_fill_light.append((x    , y - 1, z    , light_level))
        
        if z + 1 < voxels.shape[2]:
            if light_level > chunks_light[x    ][y    ][z + 1]: flood_fill_light.append((x    , y    , z + 1, light_level))

        if 0 <= z - 1:
            if light_level > chunks_light[x    ][y    ][z - 1]: flood_fill_light.append((x    , y    , z - 1, light_level))

    return chunks_light