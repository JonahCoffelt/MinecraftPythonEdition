class BlockInteractionsHandler:
    def __init__(self, project) -> None:
        # Save parent references
        self.project = project
        self.ui_handler = project.ui_handler 
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

    def crafting_table(self, id, x, y, z):
        self.ui_handler.set_menu_craft_table()
    
    def chest(self, id, x, y, z):
        self.ui_handler.set_menu_craft_table()

    def furnace(self, id, x, y, z):
        self.ui_handler.set_menu_craft_table()