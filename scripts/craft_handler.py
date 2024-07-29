import numpy as np

class CraftHandler:
    def __init__(self) -> None:
        self.load_recipes()
    
    def load_recipes(self):
        self.recipes = {}
        with open('gamedata/recipes.txt', 'r') as file:
            file_list = list(file)
            for line in file_list[1:]:
                # Split components of recipe from the line
                line = line.strip().split(';')
                # Isolate components
                result = int(line[1].strip())
                quantity = int(line[2].strip())
                recipe_id = line[3].strip().split(',')
                recipe_id = list(map(int, recipe_id))

                self.recipes[tuple(recipe_id)] = (result, quantity)

                # Convert 1x1 recipes to 2x2 and 3x3
                if len(recipe_id) == 1:
                    for corner in range(4):
                        recipe = []
                        for prefix in range(corner): recipe += [0]
                        recipe += recipe_id
                        for sufix in range(3 - corner): recipe += [0]

                        self.recipes[tuple(recipe)] = (result, quantity)
                    
                    for corner in range(9):
                        recipe = []
                        for prefix in range(corner): recipe += [0]
                        recipe += recipe_id
                        for sufix in range(8 - corner): recipe += [0]

                        self.recipes[tuple(recipe)] = (result, quantity)
                
                # Convert 2x2 recipes to 3x3
                elif len(recipe_id) == 4:
                    template = np.array([[int(recipe_id[0]), int(recipe_id[1])], [int(recipe_id[2]), int(recipe_id[3])]])
                    for y in range(2):
                        for x in range(2):
                            recipe_array = np.zeros(shape=(3, 3), dtype='int')
                            recipe_array[y:y+2,x:x+2] = template
                            recipe = recipe_array.ravel()

                            self.recipes[tuple(recipe)] = (result, quantity)

    def check_recipe(self, container):
        container_slots = container.item_slots.ravel(order='F')
        for i in range(len(container_slots)): 
            if not container_slots[i]: container_slots[i] = 0
            else: container_slots[i] = container_slots[i].template.item_id
        recipe_id = tuple(map(int, container_slots))

        if recipe_id in self.recipes: return self.recipes[recipe_id]

        return None
