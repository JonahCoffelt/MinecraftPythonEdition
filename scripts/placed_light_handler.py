class PlacedLightHandler:
    def __init__(self, scene) -> None:
        self.scene = scene
        
        self.chunks = {}

        self.block_light_levels = {
            36: 15
        }

    def get_chunk_placed_lights(self, chunk_key: tuple):
        if chunk_key in self.chunks:
            return self.chunks[chunk_key]
        return set([])
    
    def place(self, x, y, z, id):
        chunk_size = self.scene.chunk_handler.chunk_size
        chunk = (x // chunk_size, y // chunk_size, z // chunk_size)
        
        if chunk not in self.scene.chunk_handler.chunks:
            return
        
        if id not in self.block_light_levels:
            return

        if chunk not in self.chunks:
            self.chunks[chunk] = set()

        light = (x, y, z, self.block_light_levels[id])

        self.chunks[chunk].add(light)
