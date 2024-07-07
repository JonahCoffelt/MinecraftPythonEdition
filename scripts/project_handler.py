from scripts.scene import Scene
from scripts.vao_handler import VAOHandler
from scripts.texture_handler import TextureHandler
from scripts.ui_handler import UIHandler

class ProjectHandler:
    """
    Stores, loads, and saves projects
    """
    def __init__(self, engine, project_name: str='Project', load_project: str='empty') -> None:
        """
        Initializes the specified projects
        """
        # Stores the engine
        self.engine = engine
        # Creates blank projects dictionary
        self.projects = {}

        # Loads specified projects
        match load_project:
            case 'empty':
                # Creates a blank project and saves it
                self.projects[project_name] = BlankProject(self.engine)
                self.current_project = self.projects[project_name]
            case _:
                # Load project save
                raise ValueError('ProjectHandler.__init__: Project loading not supported')

    def update(self) -> None:
        self.current_project.update()

    def render(self) -> None:
        self.current_project.render()

    def add_project(self, name: str='Project') -> None:
        """
        Adds a blank project
        """

        # Checks for duplicate names
        project_key, count = name, 1
        while project_key in self.projects:
            project_key = f'{name} ({count})'
            count += 1

        # Adds project
        self.projects[project_key] = BlankProject(self.engine)

    def load_project(self, name, directory) -> None:
        """
        Loads a project from a file
        """

        # Checks for duplicate names
        project_key, count = name, 1
        while project_key in self.projects:
            project_key = f'{name} ({count})'
            count += 1
        
        self.projects[name] = LoadProject(self.engine, 'saves/' + directory)

    def set_current_project(self, project_key: str='Project') -> None:
        """
        Sets the current project for rendering and editing
        """

        if project_key not in self.projects:
            raise KeyError('ProjectHandler.set_current_project: Given project name does not exist')

        self.current_project = self.projects[project_key]
        self.current_project.current_scene.use()

    def release(self) -> None:
        [project.release() for project in self.projects.values()]

class Project:
    """
    Stores, loads, and saves scene data
    """
    def __init__(self, engine) -> None:
        # Stores the engine
        self.engine = engine
        self.ctx = engine.ctx
        # Creates blank scenes dictionary
        self.scenes = {}
        # Creates vao handler to be used by scenes
        self.vao_handler = VAOHandler(self)
        # Creates a texture handler. Also used for writting bindless textures
        self.texture_handler = TextureHandler(self.engine)
        # Creates a UI handler
        self.ui_handler = UIHandler(self.ctx)

    def update(self) -> None:
        """
        Updates the current scene        
        """

        self.current_scene.update()

    def render(self) -> None:
        """
        Renders the current scene        
        """

        self.current_scene.render()

    def set_scene(self, scene: str) -> None:
        """
        Sets the scene being updated and rendered
        """

        self.scenes[scene].use()
        self.current_scene = self.scenes[scene]

    def release(self) -> None:
        """
        Releases all scenes in project
        """
        [scene.release() for scene in self.scenes.values()]

class BlankProject(Project):
    def __init__(self, engine) -> None:
        super().__init__(engine)

        # Adds a blank scene
        self.scenes['Scene'] = Scene(self.engine, self)
        # Set scene to be rendered and updated
        self.current_scene = self.scenes['Scene']
        # Load textures
        self.texture_handler.load_texture('grass_block_top', 'grass_block_top.png')
        self.texture_handler.load_texture('grass_block_side', 'grass_block_side.png')
        self.texture_handler.load_texture('dirt', 'dirt.png')
        self.texture_handler.load_texture('stone', 'stone.png')
        self.texture_handler.load_texture('oak_log', 'oak_log.png')
        self.texture_handler.load_texture('oak_log_top', 'oak_log_top.png')
        self.texture_handler.generate_texture_arrays()
        # Use the scene
        self.current_scene.use()

class LoadProject(Project):
    def __init__(self, engine, directory) -> None:
        super().__init__(engine)
        # Loads the project file
        self.current_scene.use()
