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
    
    def draw_slots(self, dimensions: tuple=(0.5, 0.5, 3, 3), items: list=[[]], selection: tuple=(-1, 1)) -> None:
        """

        Draws w x h slots (for inventory or crafting menus) at a given x and y pos (ranging from 0 to 1 and centered)
        For example, draw_slots((0.5, 0.5, 3, 3)) will make a 3 x 3 grid in the center of the screen
        """
    
        x_pos, y_pos, w, h = dimensions

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
                item = items[x_slot][y_slot]

                x = (self.slot_size + self.gap_size) * x_slot + offset[0] + self.gap_size
                y = (self.slot_size + self.gap_size) * y_slot + offset[1] + self.gap_size

                if x_slot == selection[0] and y_slot == selection[1]:
                    # Slot is selected
                    gap = 8
                    color = (215, 215, 215, 150)
                else:
                    # Slot is not selected
                    gap = 16
                    color = (100, 100, 100, 150)
                
                # Draw empty slot box
                pg.draw.rect(self.ui_handler.surf, color, (x, y, self.slot_size, self.slot_size))

                if item:
                    # Get the item image surface
                    item_surf = self.ui_handler.texture_handler.texture_surfaces[item.template.texture_id]
                    item_surf = pg.transform.scale(item_surf, (self.slot_size - gap, self.slot_size - gap))
                    # Display in the slot
                    self.ui_handler.surf.blit(item_surf, (x + gap/2, y + gap/2))
                    # Render quantity
                    if item.quantity == 1: continue
                    quantity_surf, rect = self.ui_handler.font.render(str(item.quantity), (200, 200, 200))
                    quantity_surf = pg.transform.scale(quantity_surf, (rect[2] * self.slot_size / 64 / 2, rect[3] * self.slot_size / 64 / 2))
                    self.ui_handler.surf.blit(quantity_surf, (x + self.slot_size - rect[2]/2, y + self.slot_size - rect[3]/2))

    def get_mouse_grid(self, mouse_position, dimensions: tuple=(0.5, 0.5, 3, 3)) -> bool:
        """
        Returns the grid position if the given mouse position falls within the bounds of a menu, else False
        """
        
        x_pos, y_pos, w, h = dimensions

        # The total size of the slots in pixels
        total_width  = w * self.slot_size  +  (w + 1) * self.gap_size
        total_height = h * self.slot_size  +  (h + 1) * self.gap_size

        # Get the standard offset for all slots' positions
        offset = (x_pos * self.ui_handler.win_size[0] - total_width  / 2, 
                  y_pos * self.ui_handler.win_size[1] - total_height / 2)
        
        if not(offset[0] < mouse_position[0] < offset[0] + total_width - self.gap_size and offset[1] < mouse_position[1] < offset[1] + total_height - self.gap_size):
            return False
        
        mouse_position = mouse_position[0] - offset[0], mouse_position[1] - offset[1]

        return int(mouse_position[0] // (self.slot_size + self.gap_size)), int(mouse_position[1] // (self.slot_size + self.gap_size))
        
        