import pygame as pg
from pygame import freetype
import moderngl as mgl
import numpy as np
import pyautogui
from scripts.slot_menus_handler import SlotHandler
from scripts.item_data import ItemDataHandler
from scripts.block_data import BlockDataHandler
from scripts.item import Item
from scripts.item_container import ItemContainer


class UIHandler:
    def __init__(self, project, win_size=(800, 800)) -> None:
        # Save refernece to context
        self.ctx = project.ctx
        self.engine = project.engine
        self.texture_handler = project.texture_handler
        self.craft_handler = project.craft_handler

        # Save the window size
        self.win_size = win_size

        # Create a surface for the UI
        self.surf = pg.Surface(self.win_size).convert_alpha()

        # Font
        freetype.init()
        self.font = freetype.Font('font/MinecraftTen-VGORe.ttf', 64)

        # Variables for updating
        self.update_texture = True

        # In-game menu handler
        self.slot_handler = SlotHandler(self)
        # Item data
        self.item_data_handler = ItemDataHandler()
        # Block data
        self.block_data_handler = BlockDataHandler()

        # Create a blank inventory
        self.inventory = ItemContainer((9, 4))
        self.crafter = ItemContainer((2, 2))
        self.block_container = None
        self.container_data = None
        self.hot_bar_selection = 0
        self.grabbed_item = None
        self.recipe_result_item = None
        self.dragged_slots = set()
        self.menu_state = 'hotbar'
        self.draw_func = self.draw_hotbar

        # Menu configs
        self.menus = {
            'hotbar' : (self.draw_hotbar, self.lock_mouse),
            'inventory' : (self.draw_inventory, self.center_mouse),
            'craft' : (self.draw_crafting_table, self.center_mouse),
            'chest' : (self.draw_chest, self.center_mouse),
            'furnace' : (self.draw_furnace, self.center_mouse),
        }

        self.inventory.quick_drop(Item(self.item_data_handler.item_data_templates[43], 32))
        self.inventory.quick_drop(Item(self.item_data_handler.item_data_templates[48], 32))
        self.inventory.quick_drop(Item(self.item_data_handler.item_data_templates[53], 32))
        self.inventory.quick_drop(Item(self.item_data_handler.item_data_templates[5], 64))
        self.inventory.quick_drop(Item(self.item_data_handler.item_data_templates[77], 64))
  
    def use(self, scene, frame_vao, win_size=(800, 800)):
        # Save refernece to parent scene and frame vao
        self.scene = scene
        self.frame_vao = frame_vao

        self.resize(win_size)

    def resize(self, win_size):
        """
        Resize the surface and texture if the window is resized
        """
        
        # Save the window size
        self.win_size = win_size

        # Create a surface for the UI
        self.surf = pg.Surface(win_size).convert_alpha()

        # Create a surface for the UI
        self.surf = pg.Surface(self.win_size).convert_alpha()

        # Generate an empty texture for the UI
        self.generate_ui_texture()

        # Variables for updating
        self.update_texture = True

        # Update menu handler
        self.slot_handler.set_slot_size()


    def generate_ui_texture(self):
        """
        Generates a blank texture for writing the UI surface
        """
        
        self.texture = self.ctx.texture(self.surf.get_size(), 4)
        self.texture.filter = (mgl.NEAREST, mgl.NEAREST)
        self.texture.swizzel = 'BGRA'

    def write_ui_texture(self):
        """
        Writes the UI texture as is to the frame vao program
        """
        
        self.texture.write(self.surf.get_view('1'))

        self.frame_vao.program['uiTexture'] = 1
        self.texture.use(location=1)
        
        self.update_texture = False

    def update(self):
        """
        If the UI needs to be updated, will draw and write the the texture
        """

        self.get_inputs()
        self.update_current_menu()

        if not self.update_texture: return
        
        self.draw()
        self.write_ui_texture()

    def get_inputs(self):
        """
        Checks for menu changing button presses
        """

        # Check inputs for a number press
        for num_key_code in range(pg.K_1, pg.K_9):
            if self.engine.keys[num_key_code]:
                # Get the number of the key pressed
                number_pressed = num_key_code - pg.K_1
                # Update hot bar
                self.hot_bar_selection = number_pressed
                self.update_texture = True

        for event in self.engine.events:
            if event.type == pg.MOUSEWHEEL:
                self.hot_bar_selection = min(max(self.hot_bar_selection - event.y, 0), 8)
                self.update_texture = True

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_e:
                    if self.menu_state == 'hotbar': self.set_menu('inventory')
                    else: self.set_menu('hotbar')
                    self.update_texture = True

    def lock_mouse(self):
        # Locks and hides the mouse
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        screen_res = pyautogui.size()
        pyautogui.moveTo(screen_res[0]/2, screen_res[1]/2, duration=0, _pause=False)
        pg.mouse.get_rel()

    def center_mouse(self):
        # Places the mouse in the center of the screen
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)
        screen_res = pyautogui.size()
        pyautogui.moveTo(screen_res[0]/2, screen_res[1]/2, duration=0, _pause=False)

    def set_menu(self, menu):
        # Set the current menu state for reference
        self.menu_state = menu
        # Set the update and drawing functions for the menu
        self.draw_func = self.menus[menu][0]
        # Sets or locks the mouse according to the menu
        self.menus[menu][1]()

        self.update_texture = True

        # Other menu specific updates
        if menu == 'hotbar':
            for item in self.crafter.item_slots.ravel():
                if not item: continue
                self.inventory.quick_drop(item)
            self.recipe_result_item = None
        elif menu == 'inventory':
            self.crafter = ItemContainer((2, 2))

    def draw(self):
        """
        Calls the current menu draw function
        """
        self.surf.fill((0, 0, 0, 0))
        self.draw_func()

    def draw_cross(self):
        """
        Draws the in-game cross to the center of the screen
        """
        
        cross_len = 20
        cross_width = 2
        pg.draw.rect(self.surf, (225, 225, 225, 155), (self.win_size[0]/2 - cross_len/2  , self.win_size[1]/2 - cross_width/2, cross_len, cross_width))
        pg.draw.rect(self.surf, (225, 225, 225, 155), (self.win_size[0]/2 - cross_width/2, self.win_size[1]/2 - cross_len/2  , cross_width, cross_len))

    def draw_hotbar(self):
        self.draw_cross()
        self.slot_handler.draw_slots((.5, .95, 9, 1), np.reshape(self.inventory.item_slots[:,0], (9, 1)), (self.hot_bar_selection, 0))

    def draw_inventory(self):
        self.draw_inventory_slots()
        self.draw_crafting_grid(2, (1.5, 3.5), (4, 3.5))
        self.draw_grabbed_item()

    def draw_crafting_table(self):
        self.draw_inventory_slots()
        self.draw_crafting_grid(3, (-2, 3.5), (2, 3.5))
        self.draw_grabbed_item()

    def draw_chest(self):
        self.draw_inventory_slots()
        self.draw_chest_slots()
        self.draw_grabbed_item()
    
    def draw_furnace(self):
        self.draw_inventory_slots()
        self.draw_furnace_slots()
        self.draw_grabbed_item()

    def draw_inventory_slots(self):
        self.slot_handler.draw_slots((.5, .5, 9, 3), np.reshape(self.inventory.item_slots[:,1:], (9, 3)), (-1, -1))
        self.slot_handler.draw_slots((.5, .7, 9, 1), np.reshape(self.inventory.item_slots[:,0 ], (9, 1)), (-1, -1))

    def draw_chest_slots(self):
        self.slot_handler.draw_slots((.5, .25, 9, 3), np.reshape(self.block_container.item_slots, (9, 3)), (-1, -1))
    
    def draw_furnace_slots(self):
        slot_size_normalized_x = 1 / (self.win_size[0] / (self.slot_handler.slot_size + self.slot_handler.gap_size))
        slot_size_normalized_y = 1 / (self.win_size[1] / (self.slot_handler.slot_size + self.slot_handler.gap_size))

        self.slot_handler.draw_slots((.5 - slot_size_normalized_x * 2, .5 - slot_size_normalized_y * 2.5, 1, 1), np.reshape(self.block_container.item_slots[0], (1, 1)), (-1, -1))
        self.slot_handler.draw_slots((.5 - slot_size_normalized_x * 2, .5 - slot_size_normalized_y * 4.5, 1, 1), np.reshape(self.block_container.item_slots[1], (1, 1)), (-1, -1))
        self.slot_handler.draw_slots((.5 + slot_size_normalized_x * 2, .5 - slot_size_normalized_y * 3.5, 1, 1), np.reshape(self.block_container.item_slots[2], (1, 1)), (-1, -1))

        slot_size = self.slot_handler.slot_size + self.slot_handler.gap_size
        # Smelt Progress bar
        if self.container_data[0] > 0.1:
            progress = self.container_data[0]/5
            pg.draw.rect(self.surf, (200, 200, 200, 150), (self.win_size[0]/2 - slot_size  * .75, self.win_size[1]/2 - slot_size * .75/2 - slot_size * 3.5, slot_size * 1.5 * progress, slot_size * .75))
        # Fuel progress bar
        if self.container_data[1] > 0:
            progress = self.container_data[1]/self.container_data[2]
            pg.draw.rect(self.surf, (215, 125, 75, 150), (self.win_size[0]/2 - slot_size * .75/2 - slot_size * 2, self.win_size[1]/2 - slot_size * .75/2 - slot_size * 3.5 + slot_size * .75 * (1 - progress) - 1, slot_size * .75, slot_size * .75 * progress))

        # Progress bar outlines
        pg.draw.rect(self.surf, (0, 0, 0, 150), (self.win_size[0]/2 - slot_size  * .75, self.win_size[1]/2 - slot_size * .75/2 - slot_size * 3.5, slot_size * 1.5, slot_size * .75), 2)
        pg.draw.rect(self.surf, (0, 0, 0, 150), (self.win_size[0]/2 - slot_size * .75/2 - slot_size * 2, self.win_size[1]/2 - slot_size * .75/2 - slot_size * 3.5, slot_size * .75, slot_size * .75), 2)


    def draw_grabbed_item(self):

        # Draw crafting result
        if not self.grabbed_item: return

        # Draw the current held item in the inventory
        grabbed_item_surf = self.texture_handler.texture_surfaces[self.grabbed_item.template.texture_id]
        grabbed_item_surf = pg.transform.scale(grabbed_item_surf, (self.slot_handler.slot_size - 12, self.slot_handler.slot_size - 12))
        self.surf.blit(grabbed_item_surf, self.engine.mouse_position)

        # Draw the quantity of the held item
        if self.grabbed_item.quantity == 1: return

        quantity_surf, rect = self.font.render(str(self.grabbed_item.quantity), (200, 200, 200))
        quantity_surf = pg.transform.scale(quantity_surf, (rect[2] * self.slot_handler.slot_size / 64 / 2, rect[3] * self.slot_handler.slot_size / 64 / 2))
        self.surf.blit(quantity_surf, (self.engine.mouse_position[0] + self.slot_handler.slot_size - rect[2]/2, self.engine.mouse_position[1] + self.slot_handler.slot_size - rect[3]/2))

    def draw_crafting_grid(self, dim: int, location: tuple, result_location: tuple):
        """
        Draws a crafting grid of dim x dim size at the given normalized screen location
        """
        
        slot_size_normalized_x = 1 / (self.win_size[0] / (self.slot_handler.slot_size + self.slot_handler.gap_size))
        slot_size_normalized_y = 1 / (self.win_size[1] / (self.slot_handler.slot_size + self.slot_handler.gap_size))

        self.slot_handler.draw_slots((.5 + slot_size_normalized_x * location[0], .5 - slot_size_normalized_y * location[1], dim, dim), self.crafter.item_slots, (-1, -1))
        self.slot_handler.draw_slots((.5 + slot_size_normalized_x * result_location[0], .5 - slot_size_normalized_y * result_location[1], 1, 1), [[self.recipe_result_item]], (-1, -1))

    def update_current_menu(self):
        if self.menu_state == 'hotbar': return

        if pg.mouse.get_rel() != (0, 0) and self.grabbed_item: self.update_texture = True

        if not (self.engine.mouse_buttons[0] or self.engine.mouse_buttons[2]):
            return
        
        menu, position = None, None
        mouse_position = self.engine.mouse_position

        menu, position = self.get_mouse_slot(mouse_position, menu, position, (.5, .5, 9, 3), self.inventory, (0, 1))
        menu, position = self.get_mouse_slot(mouse_position, menu, position, (.5, .7, 9, 1), self.inventory)
        if self.menu_state == 'inventory': menu, position = self.update_crafter(mouse_position, menu, position, 2, (1.5, 3.5), (4, 3.5))
        elif self.menu_state == 'craft': menu, position = self.update_crafter(mouse_position, menu, position, 3, (-2, 3.5), (2, 3.5))
        elif self.menu_state == 'chest': menu, position = self.get_mouse_slot(mouse_position, menu, position, (.5, .25, 9, 3), self.block_container)
        elif self.menu_state == 'furnace': 
            slot_size_normalized_x = 1 / (self.win_size[0] / (self.slot_handler.slot_size + self.slot_handler.gap_size))
            slot_size_normalized_y = 1 / (self.win_size[1] / (self.slot_handler.slot_size + self.slot_handler.gap_size))
            menu, position = self.get_mouse_slot(mouse_position, menu, position, (.5 - slot_size_normalized_x * 2, .5 - slot_size_normalized_y * 2.5, 1, 1), self.block_container, (0, 0))
            menu, position = self.get_mouse_slot(mouse_position, menu, position, (.5 - slot_size_normalized_x * 2, .5 - slot_size_normalized_y * 4.5, 1, 1), self.block_container, (1, 0))
            menu, position = self.get_mouse_slot(mouse_position, menu, position, (.5 + slot_size_normalized_x * 2, .5 - slot_size_normalized_y * 3.5, 1, 1), self.block_container, (2, 0))

        # Check if the click is in a menu
        if not menu: return

        self.process_menu_clicks(menu, position)

    def get_mouse_slot(self, mouse_position, menu, position, rect, container, offet=(0, 0)):
        """
        Returns the slot the mouse is in for a given slot menu rect
        """
        
        grid_position = self.slot_handler.get_mouse_grid(mouse_position, rect)
        if grid_position:
            menu = container
            position = grid_position[0] + offet[0], grid_position[1] + offet[1]
        return menu, position

    def update_crafter(self, mouse_position, menu, position, dim, craft_loc, res_loc):

        slot_size_normalized_x = 1 / (self.win_size[0] / (self.slot_handler.slot_size + self.slot_handler.gap_size))
        slot_size_normalized_y = 1 / (self.win_size[1] / (self.slot_handler.slot_size + self.slot_handler.gap_size))
        # Crafter
        grid_position = self.slot_handler.get_mouse_grid(mouse_position, (.5 + slot_size_normalized_x * craft_loc[0], .5 - slot_size_normalized_y * craft_loc[1], dim, dim))
        if grid_position:
            menu = self.crafter
            position = grid_position[0], grid_position[1]

        # Craft Result
        grid_position = self.slot_handler.get_mouse_grid(mouse_position, (.5 + slot_size_normalized_x * res_loc[0], .5 - slot_size_normalized_y * res_loc[1], 1, 1))
        if grid_position and self.engine.mouse_buttons[0] and not self.engine.prev_mouse_buttons[0] and self.recipe_result_item:
            if not self.grabbed_item:
                self.grabbed_item = Item(self.recipe_result_item.template, self.recipe_result_item.quantity)
                self.crafter.depreciate()
            elif self.recipe_result_item.template.item_id == self.grabbed_item.template.item_id and self.grabbed_item.quantity + self.recipe_result_item.quantity <= self.grabbed_item.template.max_stack:
                self.grabbed_item.quantity += self.recipe_result_item.quantity
                self.crafter.depreciate()

            self.check_crafter()
            self.update_texture = True

        return menu, position

    def process_menu_clicks(self, menu, position):

        target_slot_item = menu.get(*position)
        drop_item = False

        # Left click stack grab/drop
        if self.engine.mouse_buttons[0] and not self.engine.prev_mouse_buttons[0]:
            self.grabbed_item = menu.set(self.grabbed_item, *position)
            self.update_texture = True

        # Right click single drop
        elif self.engine.mouse_buttons[2] and not self.engine.prev_mouse_buttons[2]:
            self.dragged_slots = set([position])
            if self.grabbed_item:
                if (not target_slot_item) or (target_slot_item and target_slot_item.template.item_id == self.grabbed_item.template.item_id and target_slot_item.quantity < target_slot_item.template.max_stack):
                    drop_item = True

        # Right click single drag drop
        elif self.engine.mouse_buttons[2] and self.engine.prev_mouse_buttons[2]:
            if self.grabbed_item and position not in self.dragged_slots:
                if (not target_slot_item) or (target_slot_item and target_slot_item.template.item_id == self.grabbed_item.template.item_id and target_slot_item.quantity < target_slot_item.template.max_stack):
                    drop_item = True
                    self.dragged_slots.add(position)

        if drop_item:
            seperated_item = Item(self.grabbed_item.template, 1)
            self.grabbed_item.quantity -= 1
            menu.set(seperated_item, *position)
            if self.grabbed_item.quantity == 0: self.grabbed_item = None
            self.update_texture = True

        self.check_crafter()

    def check_crafter(self):
        # Check crafting recipees
        recipe_result = None
        recipe_result = self.craft_handler.check_recipe(self.crafter)
        if recipe_result:
            self.recipe_result_item = Item(self.item_data_handler.item_data_templates[recipe_result[0]], recipe_result[1])
        else:
            self.recipe_result_item = None