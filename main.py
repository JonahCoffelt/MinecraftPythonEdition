import sys
import pygame as pg
import moderngl as mgl
from scripts.project_handler import ProjectHandler


class Engine:
    """
    Instance of python engine. Stores the window, context, and projects
    """
    def __init__(self, win_size:str=(800, 800)) -> None:
        """
        Initialize the Pygame window and GL context
        """

        # Pygame initialization
        pg.init()
        # Window size
        self.win_size = win_size
        # GL attributes
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        # Pygame display init
        pg.display.set_mode(self.win_size, vsync=False, flags=pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)
        # Lock mouse in place and hide
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        # MGL context
        self.ctx = mgl.create_context()
        # Basic Gl setup
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        self.ctx.enable(flags=mgl.DEPTH_TEST)
        # Time variables
        self.clock = pg.time.Clock()
        self.time = 0
        self.dt = 0
        # Project handler
        self.project_handler = ProjectHandler(self)

    def update(self) -> None:
        """
        Updates pygame events and checks for window events
        """

        # Update time
        self.dt = self.clock.tick() / 1000
        self.time += self.dt
        pg.display.set_caption(str(round(self.clock.get_fps())))
        # Pygame events
        self.events = pg.event.get()
        self.keys = pg.key.get_pressed()
        self.mouse_position = pg.mouse.get_pos()
        self.mouse_keys = pg.mouse.get_pressed()
        # Loop through window events
        for event in self.events:
            if event.type == pg.QUIT:
                # Ends the main loop
                self.run = False
            if event.type == pg.VIDEORESIZE:
                # Updates the viewport
                self.win_size = (event.w, event.h)
                self.ctx.viewport = (0, 0, event.w, event.h)
                self.project_handler.current_project.current_scene.use()
            if event.type == pg.KEYUP:
                if event.key == pg.K_ESCAPE:
                    # Unlock mouse
                    pg.event.set_grab(False)
                    pg.mouse.set_visible(True)
                if event.key == pg.K_1:
                    scenes = list(self.project_handler.current_project.scenes.keys())
                    self.project_handler.current_project.set_scene(scenes[0])
                if event.key == pg.K_2:
                    scenes = list(self.project_handler.current_project.scenes.keys())
                    self.project_handler.current_project.set_scene(scenes[1])
            if event.type == pg.MOUSEBUTTONUP:
                # Lock mouse
                pg.event.set_grab(True)
                pg.mouse.set_visible(False)

        # Update Project
        self.project_handler.update()

    def render(self) -> None:
        """
        Renders the current project
        """

        # Clear the screen
        self.ctx.clear(color=(0.08, 0.16, 0.18))
        # Render project
        self.project_handler.render()
        # Flip display buffer
        pg.display.flip()

    def start(self) -> None:
        """
        Starts an instance of the engine
        """
        
        # Run variable allows engine to be closed from outside
        self.run = True
        # Main loop
        while self.run:
            self.update()
            self.render()

        # Closes the engine
        self.release()
        pg.quit()
        sys.exit()

    def release(self) -> None:
        """
        Collects all GL garbage in the project
        """
        self.project_handler.release()


if __name__ == '__main__':
    # Creates an engine
    engine = Engine()
    # Starts engine
    engine.start()