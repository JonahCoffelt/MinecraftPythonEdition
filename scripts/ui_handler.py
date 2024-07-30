import pygame as pg
from pygame import freetype
import moderngl as mgl
import numpy as np
import pyautogui
from scripts.slot_menus_handler import MenuHandler
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
        self.menu_handler = MenuHandler(self)

        # Item data
        self.item_data_handler = ItemDataHandler()
        # Block data
        self.block_data_handler = BlockDataHandler()

        # Create a blank inventory
        self.inventory = ItemContainer((9, 4))
        self.crafter = ItemContainer((2, 2))
        self.hot_bar_selection = 0
        self.grabbed_item = None
        self.recipe_result_item = None
        self.dragged_slots = set()
        self.menu_state = 'hotbar'
        self.menu_func = self.draw_hotbar
        self.update_func = self.update_hotbar

        self.inventory.quick_drop(Item(self.item_data_handler.item_data_templates[43], 32))
        self.inventory.quick_drop(Item(self.item_data_handler.item_data_templates[48], 32))
        self.inventory.quick_drop(Item(self.item_data_handler.item_data_templates[53], 32))
        self.inventory.quick_drop(Item(self.item_data_handler.item_data_templates[5], 64))
#
        #for i in range(10):
        #    self.inventory.quick_drop(Item(self.item_data_handler.item_data_templates[i + 1], 32))
  
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
        self.menu_handler.set_slot_size()


    def generate_ui_texture(self):
        """
        Generates a blank texture for writing the UI surface
        """
        
        self.texture = self.ctx.texture(self.surf.get_size(), 4)
        self.texture.filter = (mgl.NEAREST, mgl.NEAREST)
        self.texture.swizzel = 'BGRA'

    def surf_to_texture(self):
        """
        Converts the UI surface to a texture
        """
        
        self.texture.write(self.surf.get_view('1'))

    def write_texture(self):
        """
        Writes the UI texture as is to the frame vao program
        """
        
        self.frame_vao.program['uiTexture'] = 1
        self.texture.use(location=1)
        
        self.update_texture = False

    def update(self):
        """
        If the UI needs to be updated, will draw and write the the texture
        """

        self.get_inputs()
        self.update_func()

        if not self.update_texture: return
        
        self.draw()
        self.surf_to_texture()
        self.write_texture()

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
                    self.update_texture = True
                    if self.menu_state == 'hotbar': self.set_menu_inventory()
                    else: self.set_menu_hotbar()

    def set_menu_hotbar(self):
        # Update inventory stare
        self.menu_state = 'hotbar'
        self.update_func = self.update_hotbar
        self.menu_func = self.draw_hotbar
        for item in self.crafter.item_slots.ravel():
            if not item: continue
            self.inventory.quick_drop(item)
        self.recipe_result_item = None
        # Update mouse
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        screen_res = pyautogui.size()
        pyautogui.moveTo(screen_res[0]/2, screen_res[1]/2, duration=0, _pause=False)
        pg.mouse.get_rel()

        self.update_texture = True
    
    def set_menu_inventory(self):
        # Update inventory stare
        self.menu_state = 'inventory'
        self.update_func = self.update_inventory
        self.menu_func = self.draw_inventory
        self.crafter = ItemContainer((2, 2))
        # Update mouse
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)
        screen_res = pyautogui.size()
        pyautogui.moveTo(screen_res[0]/2, screen_res[1]/2, duration=0, _pause=False)

        self.update_texture = True

    def set_menu_craft_table(self):
        # Update inventory stare
        self.menu_state = 'craft'
        self.update_func = self.update_crafting_table
        self.menu_func = self.draw_crafting_table
        self.crafter = ItemContainer((3, 3))
        # Update mouse
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)
        screen_res = pyautogui.size()
        pyautogui.moveTo(screen_res[0]/2, screen_res[1]/2, duration=0, _pause=False)

        self.update_texture = True

    def draw(self):
        """
        Draws all pygame elements to the UI
        """
        
        self.surf.fill((0, 0, 0, 0))

        self.menu_func()

    def draw_cross(self):
        cross_len = 20
        cross_width = 2
        pg.draw.rect(self.surf, (225, 225, 225, 155), (self.win_size[0]/2 - cross_len/2  , self.win_size[1]/2 - cross_width/2, cross_len, cross_width))
        pg.draw.rect(self.surf, (225, 225, 225, 155), (self.win_size[0]/2 - cross_width/2, self.win_size[1]/2 - cross_len/2  , cross_width, cross_len))

    def draw_hotbar(self):
        self.draw_cross()

        self.menu_handler.draw_slots((.5, .95, 9, 1), np.reshape(self.inventory.item_slots[:,0], (9, 1)), (self.hot_bar_selection, 0))

    def draw_inventory(self):
        self.draw_inventory_slots()
        self.draw_2x2_craft_grid()
        self.draw_grabbed_item()

    def draw_crafting_table(self):
        self.draw_inventory_slots()
        self.draw_3x3_craft_grid()
        self.draw_grabbed_item()

    def draw_inventory_slots(self):
        self.menu_handler.draw_slots((.5, .5, 9, 3), np.reshape(self.inventory.item_slots[:,1:], (9, 3)), (-1, -1))
        self.menu_handler.draw_slots((.5, .7, 9, 1), np.reshape(self.inventory.item_slots[:,0 ], (9, 1)), (-1, -1))

    def draw_grabbed_item(self):

        # Draw crafting result
        if not self.grabbed_item: return

        # Draw the current held item in the inventory
        grabbed_item_surf = self.texture_handler.texture_surfaces[self.grabbed_item.template.texture_id]
        grabbed_item_surf = pg.transform.scale(grabbed_item_surf, (self.menu_handler.slot_size - 12, self.menu_handler.slot_size - 12))
        self.surf.blit(grabbed_item_surf, self.engine.mouse_position)

        # Draw the quantity of the held item
        if self.grabbed_item.quantity == 1: return

        quantity_surf, rect = self.font.render(str(self.grabbed_item.quantity), (200, 200, 200))
        quantity_surf = pg.transform.scale(quantity_surf, (rect[2] * self.menu_handler.slot_size / 64 / 2, rect[3] * self.menu_handler.slot_size / 64 / 2))
        self.surf.blit(quantity_surf, (self.engine.mouse_position[0] + self.menu_handler.slot_size - rect[2]/2, self.engine.mouse_position[1] + self.menu_handler.slot_size - rect[3]/2))

    def draw_2x2_craft_grid(self):
        # Draw crafting grid
        slot_size_normalized_x = 1 / (self.win_size[0] / (self.menu_handler.slot_size + self.menu_handler.gap_size))
        slot_size_normalized_y = 1 / (self.win_size[1] / (self.menu_handler.slot_size + self.menu_handler.gap_size))
        self.menu_handler.draw_slots((.5 + slot_size_normalized_x * 1.5, .5 - slot_size_normalized_y * 3.5, 2, 2), self.crafter.item_slots, (-1, -1))
        self.menu_handler.draw_slots((.5 + slot_size_normalized_x * 4, .5 - slot_size_normalized_y * 3.5, 1, 1), [[self.recipe_result_item]], (-1, -1))
    
    def draw_3x3_craft_grid(self):
        # Draw crafting grid
        slot_size_normalized_x = 1 / (self.win_size[0] / (self.menu_handler.slot_size + self.menu_handler.gap_size))
        slot_size_normalized_y = 1 / (self.win_size[1] / (self.menu_handler.slot_size + self.menu_handler.gap_size))
        self.menu_handler.draw_slots((.5 - slot_size_normalized_x * 2, .5 - slot_size_normalized_y * 3.5, 3, 3), self.crafter.item_slots, (-1, -1))
        self.menu_handler.draw_slots((.5 + slot_size_normalized_x * 2, .5 - slot_size_normalized_y * 3.5, 1, 1), [[self.recipe_result_item]], (-1, -1))

    def update_hotbar(self): ...

    def update_inventory(self):
        """
        Update all mouse inputs in the inventory menu
        """
        
        if pg.mouse.get_rel() != (0, 0) and self.grabbed_item: self.update_texture = True

        if not (self.engine.mouse_buttons[0] or self.engine.mouse_buttons[2]):
            return

        menu, position = None, None
        mouse_position = self.engine.mouse_position

        menu, position = self.update_inventory_slots(mouse_position, menu, position)
        menu, position = self.update_2x2_crafter(mouse_position, menu, position)

        # Check if the click is in a menu
        if not menu: return

        self.process_menu_clicks(menu, position)

    def update_crafting_table(self):
        if pg.mouse.get_rel() != (0, 0) and self.grabbed_item: self.update_texture = True

        if not (self.engine.mouse_buttons[0] or self.engine.mouse_buttons[2]):
            return

        menu, position = None, None
        mouse_position = self.engine.mouse_position

        menu, position = self.update_inventory_slots(mouse_position, menu, position)
        menu, position = self.update_3x3_crafter(mouse_position, menu, position)

        # Check if the click is in a menu
        if not menu: return

        self.process_menu_clicks(menu, position)

    def update_inventory_slots(self, mouse_position, menu, position):
        # Top/Big inventory
        grid_position = self.menu_handler.get_mouse_grid(mouse_position, (.5, .5, 9, 3))
        if grid_position:
            menu = self.inventory
            position = grid_position[0], grid_position[1] + 1

        # Hotbar inventory
        grid_position = self.menu_handler.get_mouse_grid(mouse_position, (.5, .7, 9, 1))
        if grid_position:
            menu = self.inventory
            position = grid_position[0], grid_position[1]

        return menu, position

    def update_2x2_crafter(self, mouse_position, menu, position):

        slot_size_normalized_x = 1 / (self.win_size[0] / (self.menu_handler.slot_size + self.menu_handler.gap_size))
        slot_size_normalized_y = 1 / (self.win_size[1] / (self.menu_handler.slot_size + self.menu_handler.gap_size))
        # Crafter
        grid_position = self.menu_handler.get_mouse_grid(mouse_position, (.5 + slot_size_normalized_x * 1.5, .5 - slot_size_normalized_y * 3.5, 2, 2))
        if grid_position:
            menu = self.crafter
            position = grid_position[0], grid_position[1]

        # Craft Result
        grid_position = self.menu_handler.get_mouse_grid(mouse_position, (.5 + slot_size_normalized_x * 4, .5 - slot_size_normalized_y * 3.5, 1, 1))
        if grid_position and self.engine.mouse_buttons[0] and not self.engine.prev_mouse_buttons[0] and self.recipe_result_item:
            if not self.grabbed_item:
                self.grabbed_item = Item(self.recipe_result_item.template, self.recipe_result_item.quantity)
                self.crafter.depreciate()
            elif self.recipe_result_item.template.item_id == self.grabbed_item.template.item_id and self.grabbed_item.quantity + self.recipe_result_item.quantity <= self.grabbed_item.template.max_stack:
                self.grabbed_item.quantity += self.recipe_result_item.quantity
                self.crafter.depreciate()

            self.check_inv_crafter()
            self.update_texture = True

        return menu, position
    
    def update_3x3_crafter(self, mouse_position, menu, position):

        slot_size_normalized_x = 1 / (self.win_size[0] / (self.menu_handler.slot_size + self.menu_handler.gap_size))
        slot_size_normalized_y = 1 / (self.win_size[1] / (self.menu_handler.slot_size + self.menu_handler.gap_size))
        # Crafter
        grid_position = self.menu_handler.get_mouse_grid(mouse_position, (.5 - slot_size_normalized_x * 2, .5 - slot_size_normalized_y * 3.5, 3, 3))
        if grid_position:
            menu = self.crafter
            position = grid_position[0], grid_position[1]

        # Craft Result
        grid_position = self.menu_handler.get_mouse_grid(mouse_position, (.5 + slot_size_normalized_x * 2, .5 - slot_size_normalized_y * 3.5, 1, 1))
        if grid_position and self.engine.mouse_buttons[0] and not self.engine.prev_mouse_buttons[0] and self.recipe_result_item:
            if not self.grabbed_item:
                self.grabbed_item = Item(self.recipe_result_item.template, self.recipe_result_item.quantity)
                self.crafter.depreciate()
            elif self.recipe_result_item.template.item_id == self.grabbed_item.template.item_id and self.grabbed_item.quantity + self.recipe_result_item.quantity <= self.grabbed_item.template.max_stack:
                self.grabbed_item.quantity += self.recipe_result_item.quantity
                self.crafter.depreciate()

            self.check_inv_crafter()
            self.update_texture = True

        return menu, position

    def process_menu_clicks(self, menu, position):

        # Left click stack grab/drop
        if self.engine.mouse_buttons[0] and not self.engine.prev_mouse_buttons[0]:
            self.grabbed_item = menu.set(self.grabbed_item, *position)
            self.update_texture = True
        
        # Right click single drop
        elif self.engine.mouse_buttons[2] and not self.engine.prev_mouse_buttons[2]:
            self.dragged_slots = set([position])
            target_slot_item = menu.get(*position)

            if self.grabbed_item:
                if (not target_slot_item) or (target_slot_item and target_slot_item.template.item_id == self.grabbed_item.template.item_id and target_slot_item.quantity < target_slot_item.template.max_stack):
                    seperated_item = Item(self.grabbed_item.template, 1)
                    self.grabbed_item.quantity -= 1
                    menu.set(seperated_item, *position)
                    if self.grabbed_item.quantity == 0: self.grabbed_item = None
                    self.update_texture = True

        # Right click single drag drop
        elif self.engine.mouse_buttons[2] and self.engine.prev_mouse_buttons[2]:
            target_slot_item = menu.get(*position)

            if self.grabbed_item and position not in self.dragged_slots:
                if (not target_slot_item) or (target_slot_item and target_slot_item.template.item_id == self.grabbed_item.template.item_id and target_slot_item.quantity < target_slot_item.template.max_stack):
                    seperated_item = Item(self.grabbed_item.template, 1)
                    self.grabbed_item.quantity -= 1
                    menu.set(seperated_item, *position)
                    if self.grabbed_item.quantity == 0: self.grabbed_item = None
                    self.update_texture = True

                    self.dragged_slots.add(position)

        self.check_inv_crafter()

    def check_inv_crafter(self):
        # Check crafting recipees
        recipe_result = None
        recipe_result = self.craft_handler.check_recipe(self.crafter)
        if recipe_result:
            self.recipe_result_item = Item(self.item_data_handler.item_data_templates[recipe_result[0]], recipe_result[1])
        else:
            self.recipe_result_item = None