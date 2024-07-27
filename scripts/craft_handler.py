import numpy as np

class CraftHandler:
    def __init__(self) -> None:
        self.recipes_2x2 = self.load_recipes('gamedata/2x2_recipes.txt')

    def load_recipes(self, path) -> None:
        recipes = {}
        with open(path, 'r') as file:
            file_list = list(file)
            for line in file_list[1:]:
                line = line.strip().split(';')
                result = int(line[1].strip())
                quantity = int(line[2].strip())
                recipe_id = line[3].strip()
                recipes[recipe_id] = (result, quantity)
        
        return recipes
    
    def check_recipe(self, container):
        recipe_id = ''
        container_slots = container.item_slots.ravel(order='F')
        for i in range(len(container_slots)):
            if not container_slots[i]: recipe_id += str(0)
            else: recipe_id += str(container_slots[i].template.item_id)
        
        if len(recipe_id) == 4: recipe_type = self.recipes_2x2
        else: recipe_type = None

        if recipe_id in recipe_type: return recipe_type[recipe_id]

        return None
