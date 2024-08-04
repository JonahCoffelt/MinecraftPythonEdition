import numpy as np
import moderngl as mgl
from scripts.item import Item
import glm
from numba import njit
from math import floor


@njit
def compress(array):
    i = 0

    while i + 1 < len(array) and array[i][0]:
        i += 1

    while i + 1 < len(array) and array[i + 1][0]:
        array[i] = array[i + 1]
        i += 1

    array[i] = [0, 0, 0, 0, 0, 0, 0, 0, 0]

@njit
def update_items(items, add_index, dt):
    items[:add_index,1:4] += items[:add_index,5:8] * dt
    items[:add_index,6] -= 9 * dt
    return items

@njit
def distance(player_pos, items, add_index):
    return np.sqrt(np.power(items[:add_index,1] - player_pos[0], 2) + np.power(items[:add_index,2] - player_pos[1], 2) + np.power(items[:add_index,3] - player_pos[2], 2))
    return np.sqrt(np.abs(np.power(items, 2) - np.power(player_pos, 2)))

@njit
def get_item_hit_points(items, add_index):
    item_points = items[:add_index,1:4] + np.array([.15, -.9, .15])
    item_points[:,0] = np.floor(item_points[:,0])
    item_points[:,2] = np.floor(item_points[:,2])
    return item_points

class ItemEntityHandler:
    def __init__(self, scene) -> None:
        self.scene = scene
        self.ctx = self.scene.ctx

        # Item : [tex, x, y, z, rotation, vel x, vel y, vel z, id]
        self.max_items = 1000
        self.add_index = 0
        self.items = np.zeros(shape=(1000, 9), dtype='f4')
        self.buffer = self.ctx.buffer(self.items)

        # Compile
        compress(np.zeros(shape=(3, 9)))

        vao_handler = self.scene.vao_handler
        vbo = vao_handler.vbo_handler.vbos['quad']
        self.vao = self.ctx.vertex_array(vao_handler.shader_handler.programs['item_entity'], [(vbo.vbo, vbo.format, *vbo.attribs), (self.buffer, '1f 3f 1f /i', 'in_instance_id', 'in_instance_position', 'in_instance_rotation')], skip_errors=True)
        
    def render(self):
        self.buffer.write(np.array(self.items[:self.add_index,:5], order='C'))

        self.ctx.disable(flags=mgl.CULL_FACE)
        self.vao.render(instances=self.add_index)
        self.ctx.enable(flags=mgl.CULL_FACE)

    def update(self):
        dt = self.scene.engine.dt

        # Rotate the item
        self.items[:self.add_index,4] += 1.5 * dt
        
        update_items(self.items, self.add_index, dt)

        # Check if the item needs to fall or be collected

        hit_points = get_item_hit_points(self.items, self.add_index)

        for i, item in enumerate(hit_points):
            if self.items[i][6] <= 0 and self.scene.chunk_handler.get_voxel_id(item[0], item[1], item[2]): self.items[i][6] = 0; continue

        player_pos = self.scene.player.position
        player_pos = np.array([player_pos.x, player_pos.y, player_pos.z], dtype='f4')
        distances = distance(player_pos, self.items, self.add_index)

        removes = np.where(distances < 2)[0]
        for index in removes:
            item = self.items[index]
            self.scene.project.ui_handler.inventory.quick_drop(Item(self.scene.project.ui_handler.item_data_handler.item_data_templates[int(item[-1])], 1))
            self.scene.project.ui_handler.update_texture = True
        
        for index in removes:
            self.remove(index)

    def add(self, item_id, tex_id, x, y, z, x_vel=0, y_vel=0, z_vel=0) -> None:
        self.items[self.add_index] = [tex_id , x, y, z, 0, x_vel, y_vel, z_vel, item_id]
        self.add_index += 1

    def remove(self, index) -> None:
        self.items[index] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        compress(self.items)
        self.add_index -= 1
        