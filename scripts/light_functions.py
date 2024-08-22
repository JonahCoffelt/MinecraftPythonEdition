import numpy as np
from numba import njit


@njit (fastmath=True)
def get_sky_light(voxels) -> np.ndarray:
    """
    Cascades sky light down given the voxels
    Returns an array of light values in same shape as voxels
    """
    
    sky_light = np.zeros(shape=voxels.shape, dtype='i8')

    max_light_level = 15
    max_height = voxels.shape[1] - 1

    for x in range(voxels.shape[0]):
        for z in range(voxels.shape[2]):
            y = max_height
            while y > 0 and voxels[x][y][z] == 0:
                y -= 1
            sky_light[x,y+1:,z] = max_light_level

    return sky_light


@njit
def flood_light(voxels, chunks, flooders):
    """
    Flood fills all lights in the flooders queue
    Updates the chunks array in place
    """
    
    pop_index = 1
    while pop_index < len(flooders):
        x, y, z, light_level = flooders[pop_index]
        pop_index += 1

        if voxels[x][y][z] not in {0, 36}: continue
        
        if not (0 <= x < voxels.shape[0] and 0 <= y < voxels.shape[1] and 0 <= z < voxels.shape[2]): continue
        if light_level <= chunks[x][y][z]: continue


        chunks[x][y][z] = light_level

        if light_level == 1: continue

        if x + 1 < voxels.shape[0]:
            if light_level > chunks[x + 1][y    ][z    ]: flooders.append((x + 1, y    , z    , light_level - 1))

        if 0 <= x - 1:
            if light_level > chunks[x - 1][y    ][z    ]: flooders.append((x - 1, y    , z    , light_level - 1))
        
        if y + 1 < voxels.shape[1]:
            if light_level > chunks[x    ][y + 1][z    ]: flooders.append((x    , y + 1, z    , light_level - 1))

        if 0 <= y - 1:
            if light_level > chunks[x    ][y - 1][z    ]: flooders.append((x    , y - 1, z    , light_level - 1))
        
        if z + 1 < voxels.shape[2]:
            if light_level > chunks[x    ][y    ][z + 1]: flooders.append((x    , y    , z + 1, light_level - 1))

        if 0 <= z - 1:
            if light_level > chunks[x    ][y    ][z - 1]: flooders.append((x    , y    , z - 1, light_level - 1))


@njit
def calculate_light(voxels, existing_sky_light, existing_placed_lights, placed_lights):
    # Cascade skylight
    chunks_sky_light = get_sky_light(voxels)
    # Empty array for placed light
    chunks_placed_light = np.zeros(shape=voxels.shape, dtype='i8')

    # Add existing sky lights to the edge of the sky light array we will be working with
    chunks_sky_light[0,:,:]  = existing_sky_light[0,:,:]
    chunks_sky_light[-1,:,:] = existing_sky_light[-1,:,:]
    chunks_sky_light[:,:,0]  = existing_sky_light[:,:,0]
    chunks_sky_light[:,:,-1] = existing_sky_light[:,:,-1]

    # Add existing placed lights to the edge of the placed light array we will be working with
    chunks_placed_light[0,:,:]  = existing_placed_lights[0,:,:]
    chunks_placed_light[-1,:,:] = existing_placed_lights[-1,:,:]
    chunks_placed_light[:,:,0]  = existing_placed_lights[:,:,0]
    chunks_placed_light[:,:,-1] = existing_placed_lights[:,:,-1]

    flood_sky = [(0, 0, 0, 0)]
    flood_placed = placed_lights

    for x in range(voxels.shape[0]):
        for z in range(voxels.shape[2]):
            for y in range(voxels.shape[1]):
                # Add sky light flooders
                if chunks_sky_light[x][y][z] != 0:
                    if x + 1 < voxels.shape[0]:
                        if chunks_sky_light[x + 1][y    ][z    ] == 0: flood_sky.append((x + 1, y    , z    , chunks_sky_light[x][y][z] - 1))
                    
                    if 0 <= x - 1:
                        if chunks_sky_light[x - 1][y    ][z    ] == 0: flood_sky.append((x - 1, y    , z    , chunks_sky_light[x][y][z] - 1))
                    
                    if y + 1 < voxels.shape[1]:
                        if chunks_sky_light[x    ][y + 1][z    ] == 0: flood_sky.append((x    , y + 1, z    , chunks_sky_light[x][y][z] - 1))
                    
                    if 0 <= y - 1:
                        if chunks_sky_light[x    ][y - 1][z    ] == 0: flood_sky.append((x    , y - 1, z    , chunks_sky_light[x][y][z] - 1))

                    if z + 1 < voxels.shape[2]:
                        if chunks_sky_light[x    ][y    ][z + 1] == 0: flood_sky.append((x    , y    , z + 1, chunks_sky_light[x][y][z] - 1))
                    
                    if 0 <= z - 1:
                        if chunks_sky_light[x    ][y    ][z - 1] == 0: flood_sky.append((x    , y    , z - 1, chunks_sky_light[x][y][z] - 1))
                
                # Add placed light flooders
                if chunks_placed_light[x][y][z] != 0:
                    if x + 1 < voxels.shape[0]:
                        if chunks_placed_light[x + 1][y    ][z    ] == 0: flood_placed.append((x + 1, y    , z    , chunks_placed_light[x][y][z] - 1))
                    
                    if 0 <= x - 1:
                        if chunks_placed_light[x - 1][y    ][z    ] == 0: flood_placed.append((x - 1, y    , z    , chunks_placed_light[x][y][z] - 1))
                    
                    if y + 1 < voxels.shape[1]:
                        if chunks_placed_light[x    ][y + 1][z    ] == 0: flood_placed.append((x    , y + 1, z    , chunks_placed_light[x][y][z] - 1))
                    
                    if 0 <= y - 1:
                        if chunks_placed_light[x    ][y - 1][z    ] == 0: flood_placed.append((x    , y - 1, z    , chunks_placed_light[x][y][z] - 1))

                    if z + 1 < voxels.shape[2]:
                        if chunks_placed_light[x    ][y    ][z + 1] == 0: flood_placed.append((x    , y    , z + 1, chunks_placed_light[x][y][z] - 1))
                    
                    if 0 <= z - 1:
                        if chunks_placed_light[x    ][y    ][z - 1] == 0: flood_placed.append((x    , y    , z - 1, chunks_placed_light[x][y][z] - 1))


    flood_light(voxels, chunks_sky_light, flood_sky)
    flood_light(voxels, chunks_placed_light, flood_placed)

    return chunks_sky_light, chunks_placed_light