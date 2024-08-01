from scripts.item_container import BlockContainerHandler, ItemContainer
from scripts.furnace_handler import FurnaceHandler


class BlockInteractionsHandler:
    def __init__(self, project) -> None:
        # Save parent references
        self.project = project
        self.ui_handler = project.ui_handler 
        # Handler for blocks with containers (chest, furnace, ...)
        self.block_container_handler = BlockContainerHandler()
        # Furnace fuels and recipes
        self.furnace_handler = FurnaceHandler(self, self.ui_handler)
        # Map block interactions
        self.interactions = {
            6 : self.crafting_table,
            34 : self.chest,
            33 : self.furnace,
        }

    def interact(self, id, x, y, z):
        if id in self.interactions:
            self.interactions[id](id, x, y, z)
            return True
        return False

    def place(self, id, x, y, z):
        if id == 34:
            self.block_container_handler.add(x, y, z, (9, 3))
        elif id == 33:
            self.block_container_handler.add(x, y, z, (3, 1))
            self.furnace_handler.furnaces[(x, y, z)] = [0, 0, 1]

    def crafting_table(self, id, x, y, z):
        self.ui_handler.crafter = ItemContainer((3, 3))
        self.ui_handler.set_menu('craft')
    
    def chest(self, id, x, y, z):
        container = self.block_container_handler.get(x, y, z)
        self.ui_handler.block_container = container
        self.ui_handler.set_menu('chest')

    def furnace(self, id, x, y, z):
        container = self.block_container_handler.get(x, y, z)
        self.ui_handler.block_container = container
        self.ui_handler.current_block_opened = (x, y, z)
        self.ui_handler.set_menu('furnace')