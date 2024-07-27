class ItemDataHandler:
    def __init__(self) -> None:
        # Create a dictionary to hold all item data templates
        self.item_data_templates = {}
        # Load items from gamedata file
        self.load_default_items()
    
    def load_default_items(self) -> None:
        with open('gamedata/item_data.txt', 'r') as item_data_file:
            item_data_list = list(item_data_file)[1:]
        
        for i, item in enumerate(item_data_list):
            item_data_list[i] = item.strip().replace(' ', '').split(';')
        
        for item in item_data_list:
            self.add_item(int(item[0]), int(item[1]), int(item[2]), str(item[3]), item[4]=='True', int(item[5]), int(item[6]), int(item[7]), list(map(int, item[8][1:-1].split(','))))

    def add_item(self, item_id: int, block_id:int, texture_id:int, name: str, placeable: bool, block_type: int, max_stack: int, max_durability: int, breaking_multipliers: list) -> None:
        self.item_data_templates[item_id] = ItemTemplate(item_id, block_id, texture_id, name, placeable, block_type, max_stack, max_durability, breaking_multipliers)


class ItemTemplate:
    def __init__(self, item_id: int, block_id:int, texture_id:int, name: str, placeable: bool, block_type: int, max_stack: int, max_durability: int, breaking_multipliers: list) -> None:
        self.item_id = item_id
        self.block_id = block_id
        self.texture_id = texture_id
        self.name = name.replace('_', ' ')
        self.placeable = placeable
        self.block_type = block_type
        self.max_stack = max_stack
        self.max_durability = max_durability
        self.breaking_multipliers = breaking_multipliers

    def __repr__(self) -> str:
        return f'<Item Template | name:{self.name}, item_id:{self.item_id}, block_id:{self.block_id}>'