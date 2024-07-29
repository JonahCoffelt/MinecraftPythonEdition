import glm
import pygame as pg

# Camera view constants
NEAR = 0.1
FAR = 250

# Camera movement constants
SPEED = 20
SENSITIVITY = 0.1

class Camera:
    """
    Camera object to get view and projection matricies. Movement built in
    """
    def __init__(self, engine, scene, position=(0, 3, 0), yaw=-90, pitch=0) -> None:
        # Stores the engine to acces viewport and inputs
        self.engine = engine
        self.scene = scene
        # The initial aspect ratio of the screen
        self.aspect_ratio = self.engine.win_size[0] / self.engine.win_size[1]
        self.fov = 90  # Degrees
        self.target_fov = 90  # Degrees
        # Position
        self.position = glm.vec3(position)
        # k vector for vertical movement
        self.UP = glm.vec3(0, 1, 0)
        # Movement vectors
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)
        # Look directions in degrees
        self.yaw = yaw
        self.pitch = pitch
        # View matrix
        self.m_view = self.get_view_matrix()
        # Projection matrix
        self.m_proj = self.get_projection_matrix()

    def update(self) -> None:
        self.move()
        if self.scene.project.ui_handler.menu_state == 'hotbar': self.rotate()
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

    def rotate(self) -> None:
        """
        Rotates the camera based on the amount of mouse movement.
        """
        rel_x, rel_y = pg.mouse.get_rel()
        self.yaw += rel_x * SENSITIVITY
        self.pitch -= rel_y * SENSITIVITY
        self.yaw = self.yaw % 360
        self.pitch = max(-89, min(89, self.pitch))

    def update_camera_vectors(self) -> None:
        """
        Computes the forward vector based on the pitch and yaw. Computes horizontal and vertical vectors with cross product.
        """
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)

        self.forward.x = glm.cos(yaw) * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = glm.sin(yaw) * glm.cos(pitch)

        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, self.UP))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def move(self) -> None:
        ...

    def use(self):
        # Updated aspect ratio of the screen
        self.aspect_ratio = self.engine.win_size[0] / self.engine.win_size[1]
        # View matrix
        self.m_view = self.get_view_matrix()
        # Projection matrix
        self.m_proj = self.get_projection_matrix()

    def get_view_matrix(self) -> glm.mat4x4:
        return glm.lookAt(self.position, self.position + self.forward, self.up)

    def get_projection_matrix(self) -> glm.mat4x4:
        return glm.perspective(glm.radians(self.fov), self.aspect_ratio, NEAR, FAR)
    

class FreeCamera(Camera):
    """
    Camera attached to nothing, and thus is completely free to move
    """
    
    def __init__(self, engine, scene, position=(0, 3, 35), yaw=-90, pitch=0) -> None:
        super().__init__(engine, scene, position, yaw, pitch)
    
    def move(self) -> None:
        """
        Checks for button presses and updates vectors accordingly. 
        """
        velocity = SPEED * self.engine.dt
        keys = self.engine.keys
        if keys[pg.K_w]:
            self.position += glm.normalize(glm.vec3(self.forward.x, 0, self.forward.z)) * velocity
        if keys[pg.K_s]:
            self.position -= glm.normalize(glm.vec3(self.forward.x, 0, self.forward.z)) * velocity
        if keys[pg.K_a]:
            self.position -= self.right * velocity
        if keys[pg.K_d]:
            self.position += self.right * velocity
        if keys[pg.K_SPACE]:
            self.position += self.UP * velocity
        if keys[pg.K_LSHIFT]:
            self.position -= self.UP * velocity


class FirstPersonCamera(Camera):
    """
    Camera that is attacted to an object with a position
    """
    
    def __init__(self, engine, scene, target, position=(0, 3, 35), yaw=-90, pitch=0) -> None:
        super().__init__(engine, scene, position, yaw, pitch)
        self.target = target
    
    def move(self) -> None:
        """
        Moves the camera to the position of the target
        """
        
        # Set the camera position
        self.position = self.target.position + glm.vec3(0, 0.72, 0)  # Adjusted to the same height as minecraft

        # Update the players look direction
        self.target.pitch, self.target.yaw = self.pitch, self.yaw
        self.target.right, self.target.forward = self.right, self.forward

        # Adjust the FOV if sprinting
        if self.target.sprint: self.target_fov = 105
        else: self.target_fov = 90
        if abs(self.target_fov - self.fov) > .1:
            self.fov += (self.target_fov - self.fov) * 9 * self.engine.dt
            self.m_proj = self.get_projection_matrix()
