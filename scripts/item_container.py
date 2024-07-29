import numpy as np


class ItemContainer:
    def __init__(self, dimensions: tuple) -> None:
        # Number of slots in the container
        self.dimensions = dimensions
        # Set empty slots, access with (x, y)/[x][y] convention
        self.item_slots = np.array([[None for y in range(dimensions[1])] for x in range(dimensions[0])])

    def set(self, item, x, y):
        """
        Sets an item slot to the passed in item. Returns leftover/swapped items
        """

        old_item = None

        if not item:
            old_item = self.item_slots[x][y]
        elif self.item_slots[x][y]:
            old_item = self.item_slots[x][y]

            if old_item.template.item_id == item.template.item_id:
                combined_quantity = old_item.quantity + item.quantity

                if combined_quantity <= item.template.max_stack: 
                    old_item = None
                    item.quantity = combined_quantity
                else:
                    old_item.quantity = combined_quantity - item.template.max_stack
                    item.quantity = item.template.max_stack

        self.item_slots[x][y] = item

        return old_item

    def remove(self, x, y):
        """
        Sets a slot to empty. Returns what was in the slot
        """
        
        item = self.item_slots[x][y]

        self.item_slots[x][y] = None

        return item
    
    def get(self, x, y):
        """
        Returns the item at a slot
        """

        return self.item_slots[x][y]
    
    def quick_drop(self, item):
        # Drop to same-id stacks
        for y in range(self.dimensions[1]):
            for x in range(self.dimensions[0]):
                if not self.item_slots[x][y]: continue
                if self.item_slots[x][y].template.item_id != item.template.item_id: continue

                difference = min(item.template.max_stack - self.item_slots[x][y].quantity, item.quantity)

                self.item_slots[x][y].quantity += difference
                item.quantity -= difference

                if item.quantity <= 0: return

        # Drop to empty slots
        for y in range(self.dimensions[1]):
            for x in range(self.dimensions[0]):
                if self.item_slots[x][y]: continue
                self.item_slots[x][y] = item
                return
            
        # Return leftovers
        return item

    def depreciate(self, amount: int=1):
        for x, x_level in enumerate(self.item_slots):
            for y, item in enumerate(x_level):
                if not item: continue
                item.quantity -= amount
                if item.quantity <= 0:
                    self.item_slots[x][y] = None