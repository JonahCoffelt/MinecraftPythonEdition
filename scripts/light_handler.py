import numpy as np
from scripts.light_functions import calculate_light
from numba import njit

@njit
def get_empty_light(x_size, world_height, z_size, chunk_size):
    return np.zeros(shape=(x_size, (world_height * 2 + 1) * chunk_size, z_size), dtype='i8') + 15

class LightHandler:
    def __init__(self, chunk_handler) -> None:
        self.chunk_handler = chunk_handler
        # Get variables from chunk_handler
        self.world_size = self.chunk_handler.world_size
        self.chunk_size = self.chunk_handler.chunk_size
        self.chunks = self.chunk_handler.chunks
        self.world_height = self.chunk_handler.world_height
        self.update_chunks = self.chunk_handler.update_chunks

    def after_init(self):
        dim = self.chunk_handler.world_size // 2

        x_range = (-dim, dim)
        z_range = (-dim, dim)

        x_size = x_range[1] - x_range[0]
        z_size = z_range[1] - z_range[0]

        if x_size <= 0 or z_size <= 0: return

        all_voxels = np.zeros(shape=((x_size + 1) * self.chunk_size, 5 * self.chunk_size, (z_size + 1) * self.chunk_size), dtype='i8')
        all_light = np.copy(all_voxels)
        for rel_x, x in enumerate(range(x_range[0], x_range[1] + 1)):
            for y in range(-2, 3):
                for rel_z, z in enumerate(range(z_range[0], z_range[1] + 1)):
                    all_voxels[(rel_x) * self.chunk_size:(rel_x + 1) * self.chunk_size, (y + 2) * self.chunk_size:(y + 3) * self.chunk_size,(rel_z) * self.chunk_size:(rel_z + 1) * self.chunk_size] = self.chunks[(x, y, z)].voxel_array

        chunks_light, placed_lights = calculate_light(all_voxels, all_light, np.copy(all_light), [(0, 0, 0, 0)])

        for rel_x, x in enumerate(range(x_range[0], x_range[1] + 1)):
            for y in range(-2, 3):
                for rel_z, z in enumerate(range(z_range[0], z_range[1] + 1)):
                    self.chunks[(x, y, z)].light = chunks_light[(rel_x) * self.chunk_size:(rel_x + 1) * self.chunk_size, (y + 2) * self.chunk_size:(y + 3) * self.chunk_size,(rel_z) * self.chunk_size:(rel_z + 1) * self.chunk_size]
        
    def bake(self, x, z, block_radius=15):
        x_range = [max(x - block_radius, -self.world_size // 2  * self.chunk_size), min(x + block_radius, (self.world_size // 2 + 1)  * self.chunk_size - 1)]
        z_range = [max(z - block_radius, -self.world_size // 2  * self.chunk_size), min(z + block_radius, (self.world_size // 2 + 1)  * self.chunk_size - 1)]

        x_chunks = [x_range[0] // self.chunk_size, x_range[1] // self.chunk_size]
        z_chunks = [z_range[0] // self.chunk_size, z_range[1] // self.chunk_size]

        rel_x_range = [x_range[0] % self.chunk_size, x_range[1] % self.chunk_size]
        rel_z_range = [z_range[0] % self.chunk_size, z_range[1] % self.chunk_size]

        if x_chunks[0] == x_chunks[1]: 
            x_chunks.pop()
            x_chunks = x_chunks
            rel_x_range = [(rel_x_range[0], rel_x_range[1])]
        else:
            rel_x_range = [(rel_x_range[0], self.chunk_size), (0, rel_x_range[1])]
        if z_chunks[0] == z_chunks[1]: 
            z_chunks.pop()
            z_chunks = z_chunks
            rel_z_range = [(rel_z_range[0], rel_z_range[1])]
        else:
            rel_z_range = [(rel_z_range[0], self.chunk_size), (0, rel_z_range[1])]

        x_size = x_range[1] - x_range[0]
        z_size = z_range[1] - z_range[0]

        all_voxels = get_empty_light(x_size, self.world_height, z_size, self.chunk_size)
        all_light = np.copy(all_voxels)
        all_placed_light = np.copy(all_voxels)

        placed_lights = [(0, 0, 0, 0)]

        all_x = 0
        for chunk_x, rel_x in zip(x_chunks, rel_x_range):
            all_z = 0
            for chunk_z, rel_z in zip(z_chunks, rel_z_range):
                for y in range(-self.world_height, self.world_height + 1):
                    all_voxels[all_x:all_x + (rel_x[1] - rel_x[0]), (y + self.world_height) * self.chunk_size:(y + self.world_height + 1) * self.chunk_size, all_z:all_z + (rel_z[1] - rel_z[0])] = self.chunks[(chunk_x, y, chunk_z)].voxel_array[rel_x[0]:rel_x[1],:,rel_z[0]:rel_z[1]]
                    all_light[all_x:all_x + (rel_x[1] - rel_x[0]), (y + self.world_height) * self.chunk_size:(y + self.world_height + 1) * self.chunk_size, all_z:all_z + (rel_z[1] - rel_z[0])] = self.chunks[(chunk_x, y, chunk_z)].light[rel_x[0]:rel_x[1],:,rel_z[0]:rel_z[1]]
                    all_placed_light[all_x:all_x + (rel_x[1] - rel_x[0]), (y + self.world_height) * self.chunk_size:(y + self.world_height + 1) * self.chunk_size, all_z:all_z + (rel_z[1] - rel_z[0])] = self.chunks[(chunk_x, y, chunk_z)].placed_light[rel_x[0]:rel_x[1],:,rel_z[0]:rel_z[1]]

                    for light in self.chunk_handler.scene.placed_light_handler.get_chunk_placed_lights((chunk_x, y, chunk_z)):
                        light_x, light_y, light_z, light_level = light
                        light_x, light_y, light_z = light_x - x_range[0], light_y + self.world_height * self.chunk_size, light_z - z_range[0]

                        if not (0 <= light_x < x_size and 0 <= light_z < z_size): continue

                        placed_lights.append((light_x, light_y, light_z, light_level))

                all_z += (rel_z[1] - rel_z[0])
            all_x += (rel_x[1] - rel_x[0])

        chunks_light, placed_light = calculate_light(all_voxels, all_light, all_placed_light, placed_lights)

        all_x = 0
        for chunk_x, rel_x in zip(x_chunks, rel_x_range):
            all_z = 0
            for chunk_z, rel_z in zip(z_chunks, rel_z_range):
                for y in range(-self.world_height, self.world_height + 1):
                    if np.array_equal(self.chunks[(chunk_x, y, chunk_z)].light[rel_x[0]:rel_x[1],:,rel_z[0]:rel_z[1]], chunks_light[all_x:all_x + (rel_x[1] - rel_x[0]), (y + self.world_height) * self.chunk_size:(y + self.world_height + 1) * self.chunk_size, all_z:all_z + (rel_z[1] - rel_z[0])]) and np.array_equal(self.chunks[(chunk_x, y, chunk_z)].placed_light[rel_x[0]:rel_x[1],:,rel_z[0]:rel_z[1]], placed_light[all_x:all_x + (rel_x[1] - rel_x[0]), (y + self.world_height) * self.chunk_size:(y + self.world_height + 1) * self.chunk_size, all_z:all_z + (rel_z[1] - rel_z[0])]): continue
                    
                    self.chunks[(chunk_x, y, chunk_z)].light[rel_x[0]:rel_x[1],:,rel_z[0]:rel_z[1]] = chunks_light[all_x:all_x + (rel_x[1] - rel_x[0]), (y + self.world_height) * self.chunk_size:(y + self.world_height + 1) * self.chunk_size, all_z:all_z + (rel_z[1] - rel_z[0])]
                    self.chunks[(chunk_x, y, chunk_z)].placed_light[rel_x[0]:rel_x[1],:,rel_z[0]:rel_z[1]] = placed_light[all_x:all_x + (rel_x[1] - rel_x[0]), (y + self.world_height) * self.chunk_size:(y + self.world_height + 1) * self.chunk_size, all_z:all_z + (rel_z[1] - rel_z[0])]
                    self.update_chunks.add(self.chunks[(chunk_x, y, chunk_z)])
                all_z += (rel_z[1] - rel_z[0])
            all_x += (rel_x[1] - rel_x[0])