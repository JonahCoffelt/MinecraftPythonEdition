import pygame as pg
import numpy as np
from numba import njit
import sys


block_colors = {
    0 : pg.Color(50, 75, 225),
    1 : pg.Color(50, 225, 50),
}


@njit
def get_sky_light(map, placed_lights=None):
    sky_light = np.zeros(shape=map.shape)

    light_levels = 15

    dim = map.shape[0]

    check_tiles = [(x, 0) for x in range(dim)]

    while len(check_tiles):
        x, y = check_tiles.pop(0)

        if y >= dim: continue
        if map[x][y] != 0: continue

        sky_light[x][y] = light_levels

        check_tiles.append((x, y + 1))

    flood_fill_light = placed_lights

    for x in range(dim):
        for y in range(dim):
            if sky_light[x][y] == 0: continue
            if sky_light[x + 1][y    ] == 0: flood_fill_light.append((x + 1, y    , light_levels - 1))
            if sky_light[x - 1][y    ] == 0: flood_fill_light.append((x - 1, y    , light_levels - 1))
            if sky_light[x    ][y + 1] == 0: flood_fill_light.append((x    , y + 1, light_levels - 1))
            if sky_light[x    ][y - 1] == 0: flood_fill_light.append((x    , y - 1, light_levels - 1))

    while len(flood_fill_light):
        x, y, light_level = flood_fill_light.pop(0)

        if not 0 <= x < dim or not 0 <= y < dim: continue
        if light_level <= sky_light[x][y]: continue

        sky_light[x][y] = light_level

        light_level -= 1

        if not light_level: continue

        if map[x][y] != 0: continue

        if light_level > sky_light[x + 1][y    ]: flood_fill_light.append((x + 1, y    , light_level))
        if light_level > sky_light[x - 1][y    ]: flood_fill_light.append((x - 1, y    , light_level))
        if light_level > sky_light[x    ][y + 1]: flood_fill_light.append((x    , y + 1, light_level))
        if light_level > sky_light[x    ][y - 1]: flood_fill_light.append((x    , y - 1, light_level))

    return sky_light


class App:
    def __init__(self) -> None:
        self.win_size = (800, 800)

        self.win = pg.display.set_mode(self.win_size)

        self.dim = 30
        self.map = np.zeros(shape=(self.dim, self.dim))
        self.tile_size = self.win_size[0] / self.dim


        self.placed_lights = set([(-1, -1, 0)])
        self.sky_light = get_sky_light(self.map, list(self.placed_lights))
        self.light_levels = 15
    
    def draw(self):
        self.win.fill((0, 0, 0))

        for x in range(self.dim):
            for y in range(self.dim):
                block_color = block_colors[self.map[x][y]]
                light_level = self.sky_light[x][y]
                color = block_color * (light_level/self.light_levels * .75 + .25)
                pg.draw.rect(self.win, color, (self.tile_size * x, self.tile_size * y, self.tile_size - 1, self.tile_size - 1))

        for light in self.placed_lights:
            pg.draw.rect(self.win, (225, 175, 50), (self.tile_size * light[0], self.tile_size * light[1], self.tile_size - 1, self.tile_size - 1))

        pg.display.flip()

    def update(self):
        mouse_grid_pos = int(self.mouse_pos[0] // self.tile_size), int(self.mouse_pos[1] // self.tile_size)
        if 0 <= mouse_grid_pos[0] < self.dim and 0 <= mouse_grid_pos[1] < self.dim:
            if self.mouse_buttons[0]:
                self.map[mouse_grid_pos[0]][mouse_grid_pos[1]] = 1
                self.sky_light = get_sky_light(self.map, list(self.placed_lights))
            if self.mouse_buttons[1]:
                self.placed_lights.add((mouse_grid_pos[0], mouse_grid_pos[1], 14))
                self.sky_light = get_sky_light(self.map, list(self.placed_lights))
            if self.mouse_buttons[2]:
                self.map[mouse_grid_pos[0]][mouse_grid_pos[1]] = 0
                self.sky_light = get_sky_light(self.map, list(self.placed_lights))

        self.draw()

    def start(self):
        self.run = True
        while self.run:
            self.mouse_buttons = pg.mouse.get_pressed()
            self.mouse_pos = pg.mouse.get_pos()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            self.update()


app = App()
app.start()