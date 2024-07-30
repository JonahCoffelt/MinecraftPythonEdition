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
    return items


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
        removes = []
        for i, item in enumerate(self.items[:self.add_index]):

            player_pos = self.scene.player.position
            pos = glm.vec3(item[1:4])

            if glm.length(player_pos - pos) < 1.3:
                removes.append(i)
                self.scene.project.ui_handler.inventory.quick_drop(Item(self.scene.project.ui_handler.item_data_handler.item_data_templates[int(item[-1])], 1))
                self.scene.project.ui_handler.update_texture = True
                continue

            if item[6] <= 0 and self.scene.chunk_handler.get_voxel_id(floor(item[1] + .15), item[2] - .9, floor(item[3] + .15)): item[6] = 0; continue
            item[6] -= 9 * dt

        for index in removes: self.remove(index)

    def add(self, item_id, tex_id, x, y, z, x_vel=0, y_vel=0, z_vel=0) -> None:
        self.items[self.add_index] = [tex_id , x, y, z, 0, x_vel, y_vel, z_vel, item_id]
        self.add_index += 1

    def remove(self, index) -> None:
        self.items[index] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        compress(self.items)
        self.add_index -= 1
        