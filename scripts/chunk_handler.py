import numpy as np
import glm
import random
from scripts.chunk import Chunk


class ChunkHandler:
    def __init__(self, scene) -> None:
        # Stores the scene
        self.scene = scene
        # Create an empty dictionary to hold the chunks. Keys will be the chunk's position
        self.chunks = {}
        self.update_chunks = set()
        # Set chunk parameters
        self.chunk_size = 32
        self.world_size = 4

        # Create all chunks
        dim = self.world_size//2
        for x in range(-dim, dim + 1):
            for y in range(-dim, dim + 1):
                for z in range(-dim, dim + 1):
                    self.add_chunk(x, y, z)
        
        self.generate()

    def update(self):
        for chunk in self.update_chunks:
            chunk.build_vao()
        self.update_chunks = set()

    def render(self) -> None:
        for chunk in self.chunks.values():
            chunk.render()

    def add_chunk(self, x: int, y: int, z: int) -> None:
        """
        Adds a blank chunk to the dictionary
        """
        chunk_key = f'{x},{y},{z}'
        self.chunks[chunk_key] = Chunk(self.scene, self, x, y, z, self.chunk_size)
        self.chunks[chunk_key].build_vao()

    def get_neighbor_chunk_arrays(self, x: int, y: int, z: int):
        """
        Returns a list of the neighboring chunk's arrays of a given chunk position
        """

        neighbors = np.zeros(shape=(3, 3, 3, self.chunk_size, self.chunk_size, self.chunk_size))

        for rel_x, rel_y, rel_z in zip((0, 0, 1, -1, 0, 0, 0, 0, 0), (0, 0, 0, 0, 1, -1, 0, 0), (0, 0, 0, 0, 0, 0, 1, -1)):
            
            chunk_key = f'{int(x + rel_x)},{int(y + rel_y)},{int(z + rel_z)}'
            if chunk_key not in self.chunks: continue

            neighbors[rel_x + 1][rel_y + 1][rel_z + 1] = self.chunks[chunk_key].voxel_array
        
        return neighbors

    def get_voxel_id(self, x: int, y: int, z: int) -> bool:
        """
        Returns the id of the voxel at the given global position
        """
        
        x, y, z = round(x), round(y), round(z)

        # Get the key of the chunk based on the given global position
        chunk_pos = x // self.chunk_size, y // self.chunk_size, z // self.chunk_size
        chunk_key = f'{chunk_pos[0]},{chunk_pos[1]},{chunk_pos[2]}'

        # Check that the chunk exists
        if chunk_key not in self.chunks: return 0

        # Get the position of the voxel in the chunk
        local_pos = x % self.chunk_size, y % self.chunk_size, z % self.chunk_size

        return self.chunks[chunk_key].voxel_array[local_pos[0]][local_pos[1]][local_pos[2]]

    def set_voxel(self, x: int, y: int, z: int, id: int=0) -> None:
        """
        Sets a voxel given in global coordinates to the given voxel id
        """
        
        # Get the key of the chunk based on the given global position
        chunk_pos = x // self.chunk_size, y // self.chunk_size, z // self.chunk_size
        chunk_key = f'{chunk_pos[0]},{chunk_pos[1]},{chunk_pos[2]}'

        # Check that the chunk exists
        if chunk_key not in self.chunks: return

        # Get the position of the voxel in the chunk
        local_pos = x % self.chunk_size, y % self.chunk_size, z % self.chunk_size

        # Set the voxel
        self.chunks[chunk_key].set_voxel(*local_pos, id)

        # Add effected chucks to the update list
        possible_updates = [chunk_key]
        if local_pos[0] == 0: possible_updates.append(f'{chunk_pos[0]-1},{chunk_pos[1]},{chunk_pos[2]}')
        if local_pos[1] == 0: possible_updates.append(f'{chunk_pos[0]},{chunk_pos[1]-1},{chunk_pos[2]}')
        if local_pos[2] == 0: possible_updates.append(f'{chunk_pos[0]},{chunk_pos[1]},{chunk_pos[2]-1}')
        if local_pos[0] == self.chunk_size - 1: possible_updates.append(f'{chunk_pos[0]+1},{chunk_pos[1]},{chunk_pos[2]}')
        if local_pos[1] == self.chunk_size - 1: possible_updates.append(f'{chunk_pos[0]},{chunk_pos[1]+1},{chunk_pos[2]}')
        if local_pos[2] == self.chunk_size - 1: possible_updates.append(f'{chunk_pos[0]},{chunk_pos[1]},{chunk_pos[2]+1}')
        
        for chunk_key in possible_updates:
            if not chunk_key in self.chunks: continue
            self.update_chunks.add(self.chunks[chunk_key])

    
    def generate(self):
        seed = random.randrange(10000)
        dim = (self.world_size//2) * self.chunk_size
        for x in range(-dim, dim + 1):
            for z in range(-dim, dim + 1):
                height = int((glm.simplex(glm.vec3(x + seed, 1.5 + seed, z + seed) * 0.05) + 1) * 10)

                for y in range(-dim, height + 1):
                    if (glm.simplex(glm.vec3(x + seed, y + seed, z + seed) * 0.05) + 1 - y/200) > 1.4: continue

                    if y == height: self.set_voxel(x, height, z, 1)
                    else: self.set_voxel(x, y, z, 2)
        
        for chunk in self.chunks.values():
            chunk.build_vao()