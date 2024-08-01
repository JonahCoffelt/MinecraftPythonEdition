from scripts.item import Item


class FurnaceHandler:
    def __init__(self, block_interaction_handler, ui_handler) -> None:
        self.block_container_handler = block_interaction_handler.block_container_handler
        self.ui_handler = ui_handler

        self.load_fuels()
        self.load_recipes()

        self.furnaces = {}
    
    def load_fuels(self): 
        self.fuels = {}
        with open('gamedata/fuels.txt', 'r') as file:
            file_lines = list(file)[1:]
            for line in file_lines:
                attribs = line.strip().split(';')
                item_id = int(attribs[1].strip())
                quantity_smelted = int(attribs[2].strip())

                self.fuels[item_id] = quantity_smelted

    def load_recipes(self):
        self.recipes = {}
        with open('gamedata/furnace_recipes.txt', 'r') as file:
            file_lines = list(file)[1:]
            for line in file_lines:
                attribs = line.strip().split(';')
                base_item_id = int(attribs[1].strip())
                result_item_id = int(attribs[2].strip())

                self.recipes[base_item_id] = result_item_id

    def update(self):
        for furnace_location in self.furnaces:
            furnace = self.block_container_handler.get(*furnace_location).item_slots

            if self.furnaces[furnace_location][1] >= 0:
                self.furnaces[furnace_location][1] -= self.ui_handler.engine.dt
            else:
                self.furnaces[furnace_location][1] = 0

            if self.block_container_handler.get(*furnace_location) == self.ui_handler.block_container:
                self.ui_handler.container_data = self.furnaces[furnace_location]
                self.ui_handler.update_texture = True

            if not furnace[1][0]:
                self.furnaces[furnace_location][0] = 0
                continue

            if not furnace[0][0] and self.furnaces[furnace_location][1] < 0:
                self.furnaces[furnace_location][0] = 0
                continue
        
            if not furnace[1][0].template.item_id in self.recipes:
                self.furnaces[furnace_location][0] = 0
                continue

            if not(not furnace[2][0] or furnace[2][0].template.item_id == self.recipes[furnace[1][0].template.item_id]):
                self.furnaces[furnace_location][0] = 0
                continue

            if furnace[0][0]:
                if furnace[0][0].template.item_id in self.fuels and self.furnaces[furnace_location][1] < 0:
                    self.furnaces[furnace_location][1] = self.fuels[furnace[0][0].template.item_id] * 5 + .1
                    self.furnaces[furnace_location][2] = self.fuels[furnace[0][0].template.item_id] * 5 + .1
                    furnace[0][0].quantity -= 1
                    if furnace[0][0].quantity <= 0: furnace[0][0] = None
                elif furnace[0][0].template.item_id not in self.fuels and self.furnaces[furnace_location][1] < 0:
                    self.furnaces[furnace_location][0] = 0
                    continue

            self.furnaces[furnace_location][0] += self.ui_handler.engine.dt
            if self.furnaces[furnace_location][0] >= 5:
                if not furnace[2][0]:
                    furnace[2][0] = Item(self.ui_handler.item_data_handler.item_data_templates[self.recipes[furnace[1][0].template.item_id]], 1)
                else:
                    furnace[2][0].quantity += 1

                furnace[1][0].quantity -= 1
                if furnace[1][0].quantity <= 0: furnace[1][0] = None

                self.furnaces[furnace_location][0] = 0
                continue