import pygame as pg
from pygame import freetype
from math import sin, cos, tan, atan2, degrees

class App:
    def __init__(self) -> None:
        self.win = pg.display.set_mode((800, 800))
        freetype.init()

        self.font = freetype.SysFont('arial', 20)

        self.r = 250

    def update(self):
        self.win.fill((0, 0, 0, 255))

        grid_color = (20, 20, 20)

        # Draw grid lines
        pg.draw.line(self.win, grid_color, (400, 0), (400, 800), 2) # Up/Down
        pg.draw.line(self.win, grid_color, (400 - self.r, 0), (400 - self.r, 800), 2) # Up/Down
        pg.draw.line(self.win, grid_color, (400 + self.r, 0), (400 + self.r, 800), 2) # Up/Down

        pg.draw.line(self.win, grid_color, (0, 400), (800, 400), 2) # Left/Right
        pg.draw.line(self.win, grid_color, (0, 400 - self.r), (800, 400 - self.r), 2) # Left/Right
        pg.draw.line(self.win, grid_color, (0, 400 + self.r), (800, 400 + self.r), 2) # Left/Right

        # Draw unit circle
        pg.draw.circle(self.win, (255, 255, 255), (401, 401), 2)
        pg.draw.circle(self.win, (100, 100, 255), (400, 400), self.r, 2)

        # Get mouse vector
        mouse_vector = pg.Vector2(self.mouse_pos) - pg.Vector2(400, 400)
        if mouse_vector.length() > 0: mouse_vector = pg.Vector2.normalize(mouse_vector)

        # Get the angle
        theta = atan2(mouse_vector.y, mouse_vector.x)

        # The cosest point on the circle to the mouse
        point = mouse_vector * self.r + pg.Vector2(400, 400)

        # Get triangle points
        p_a = pg.Vector2(400, 400)
        p_b = pg.Vector2(point.x, 400)
        p_c = point

        # Triangle bg
        pg.draw.polygon(self.win, (25, 25, 25, 100), (p_a, p_b, p_c))

        # Angle
        circumference = self.r / 4
        pg.draw.arc(self.win, (150, 150, 150), (400 - circumference / 2, 400 - circumference / 2, circumference, circumference), 0, -theta, 1)

        # Line to point
        pg.draw.line(self.win, (200, 200, 200), p_a, p_c, 2)

        # Triangle
        pg.draw.line(self.win, (200, 200, 200), p_b, p_c, 2)
        pg.draw.line(self.win, (200, 200, 200), p_a, p_b, 2)

        # Draw closest point
        pg.draw.circle(self.win, (255, 100, 100), point, 6)

        if theta < 0:
            theta = -theta
        else:
            theta = 6.28 - theta

        # Render text

        # Angle disp
        angle_surf = self.font.render(f'{int(degrees(theta))}', (255, 255, 255), (0, 0, 0))
        self.win.blit(angle_surf[0], (400 - angle_surf[1][2]/2, 400 - angle_surf[1][3]/2))

        # Coord disp
        coord_surf = self.font.render(f'({mouse_vector.x:.3}, {-mouse_vector.y:.3})', (255, 255, 255))
        self.win.blit(coord_surf[0], (p_c.x + 20, p_c.y - 40))

        # All data
        text_surf = self.font.render(f'θ : {int(degrees(theta))}', (255, 255, 255), (0, 0, 0))
        self.win.blit(text_surf[0], (10, 10 + 0 * (text_surf[1][3] + 10)))

        text_surf = self.font.render(f'Coord : ({mouse_vector.x:.3}, {-mouse_vector.y:.3})', (255, 255, 255), (0, 0, 0))
        self.win.blit(text_surf[0], (10, 10 + 1 * (text_surf[1][3] + 10)))

        text_surf = self.font.render(f'cos(θ) : {mouse_vector.x:.3}', (255, 255, 255), (0, 0, 0))
        self.win.blit(text_surf[0], (10, 10 + 2 * (text_surf[1][3] + 10)))

        text_surf = self.font.render(f'sin(θ) : {-mouse_vector.y:.3}', (255, 255, 255), (0, 0, 0))
        self.win.blit(text_surf[0], (10, 10 + 3 * (text_surf[1][3] + 10)))

        pg.display.flip()

    def start(self):
        self.run = True
        while self.run:
            self.mouse_pos = pg.mouse.get_pos()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                

            self.update()


app = App()
app.start()