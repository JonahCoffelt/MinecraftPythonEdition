import pygame as pg


class MenuHandler:
    def __init__(self, ui_handler) -> None:
        # Reference to the UI handler
        self.ui_handler = ui_handler
        # Set the slot size
        self.set_slot_size()

    def set_slot_size(self) -> None:
        self.slot_size = self.ui_handler.win_size[1] / 14
        self.gap_size = 2
    
    def draw_slots(self, x_pos: float, y_pos: float, w: int, h: int) -> None:
        """
        Draws w x h slots (for inventory or crafting menus) at a given x and y pos (ranging from 0 to 1 and centered)
        For example, draw_slots(0.5, 0.5, 3, 3) will make a 3 x 3 grid in the center of the screen
        """
        
        # The total size of the slots in pixels
        total_width  = w * self.slot_size  +  (w + 1) * self.gap_size
        total_height = h * self.slot_size  +  (h + 1) * self.gap_size

        # Get the standard offset for all slots' positions
        offset = (x_pos * self.ui_handler.win_size[0] - total_width  / 2, 
                  y_pos * self.ui_handler.win_size[1] - total_height / 2)

        pg.draw.rect(self.ui_handler.surf, (30, 30, 30, 200), (offset[0], offset[1], total_width + 1, total_height + 1))

        # Loop through each slot and draw it
        for x_slot in range(w):
            for y_slot in range(h):
                x = (self.slot_size + self.gap_size) * x_slot + offset[0] + self.gap_size
                y = (self.slot_size + self.gap_size) * y_slot + offset[1] + self.gap_size

                pg.draw.rect(self.ui_handler.surf, (100, 100, 100, 150), (x, y, self.slot_size, self.slot_size))