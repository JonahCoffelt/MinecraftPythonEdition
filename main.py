import sys
import pygame as pg
import moderngl as mgl
from scripts.project_handler import ProjectHandler
import cudart


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
        self.dt = self.clock.tick(120) / 1000
        self.time += self.dt
        pg.display.set_caption(str(round(self.clock.get_fps())))
        # Pygame events
        self.events = pg.event.get()
        self.keys = pg.key.get_pressed()
        self.mouse_position = pg.mouse.get_pos()
        self.mouse_buttons = pg.mouse.get_pressed()
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
                self.project_handler.current_project.texture_handler.generate_frame_buffer()
                self.project_handler.current_project.ui_handler.resize(self.win_size)

        # Update Project
        self.project_handler.update()

        # Input states
        self.prev_keys = self.keys
        self.prev_mouse_buttons = self.mouse_buttons

    def render(self) -> None:
        """
        Renders the current project
        """

        # Clear the screen
        self.ctx.clear(color=(0.3, 0.75, 0.9))
        # Render project
        self.project_handler.render()
        # Flip display buffer
        pg.display.flip()

    def start(self) -> None:
        """
        Starts an instance of the engine
        """
        
        # Input states
        self.prev_keys = pg.key.get_pressed()
        self.prev_mouse_buttons = pg.mouse.get_pressed()

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