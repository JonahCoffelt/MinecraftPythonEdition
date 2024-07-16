from scripts.item_data import *


class Inventory:
    def __init__(self) -> None:
        # List of all inventory slots
        self.inventory = [[None for y in range(4)] for x in range(9)]
        # Item data handler
        self.item_data = ItemDataHandler()
    
    def add_existing_item(self, item, x, y):
        self.inventory[x][y] = item


class Item:
    def __init__(self, template, quantity) -> None:
        self.template = template
        self.quantity = quantity