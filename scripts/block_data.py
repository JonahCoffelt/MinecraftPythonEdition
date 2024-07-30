class BlockDataHandler:
    def __init__(self) -> None:
        # Create a dictionary to hold all block data templates
        self.block_data_templates = {}
        # Load blocks from gamedata file
        self.load_default_blocks()
    
    def load_default_blocks(self) -> None:
        with open('gamedata/block_data.txt', 'r') as block_data_file:
            block_data_list = list(block_data_file)[1:]
        
        for i, block in enumerate(block_data_list):
            block_data_list[i] = block.strip().replace(' ', '').split(';')
        
        for block in block_data_list:
            self.add_block(int(block[0]), str(block[1]), int(block[2]), float(block[3]), list(map(int, block[4][1:-1].split(', '))))

    def add_block(self, block_id: int, name: str, block_type: int, hardness: float, drops: list) -> None:
        self.block_data_templates[block_id] = BlockTemplate(block_id, name, block_type, hardness, drops)


class BlockTemplate:
    def __init__(self, block_id: int, name: str, block_type: int, hardness: float, drops: list) -> None:
        self.block_id = block_id
        self.name = name.replace('_', ' ')
        self.block_type = block_type
        self.hardness = hardness
        self.drops = drops
    
    def __repr__(self) -> str:
        return f'<Block Template | name:{self.name}, block_id:{self.block_id}, block_type:{self.block_type}>'