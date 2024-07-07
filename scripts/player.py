import pygame as pg
import glm
from math import cos, sin


class Player:
    def __init__(self, scene, position=(0, 30, 0)) -> None:
        # Save refernce to the parent scene and the chunk handler
        self.scene = scene
        self.chunk_handler = self.scene.chunk_handler
        # Make a vector for the position
        self.position = glm.vec3(*position)
        # Set an arbitrary direction
        self.pitch, self.yaw = 0, 0
        self.forward = glm.vec3(0, 0, 0)
        self.right = glm.vec3(0, 0, 0)
        self.UP = glm.vec3(0, 1, 0)
        # Movement variables
        self.velocity = glm.vec3(0, 0, 0)  # Voxels per second
        self.target_velocity = glm.vec3(0, 0, 0)  # Voxels per second
        
        self.speed = 20  # Voxels per second
        self.acceleration = 13  # Voxels per second^2
        self.jump_speed = 8.8  # Voxels per second
        self.gravity = 31.36  # Voxels per second^2

        self.sprint = False
        self.flying = True
        self.has_jump = True
        # Player size
        self.size = glm.vec3(.6, 1.8, .6) # Voxels

    def update(self):
        # Get the voxel the player is looking at
        self.target_voxel = self.raycast()

        self.apply_inputs()
        self.move()
    
    def move(self):
        """
        Moves the player based on inputs and 
        """
        
        # Get delta time from the engine
        dt = self.scene.engine.dt

        # This corrects diagonal movement speed
        if self.target_velocity.x and self.target_velocity.z:
            self.target_velocity.xz *= .7

        # Gets projected player position based on current velocity
        projected_position = self.position + self.velocity * dt
        collide_x, collide_y, collide_z = self.collide(projected_position)

        # Updates position and velocity based on collisions. Snaps to grid if there is a collision
        if collide_x:
            # Snap tp grid on x axis
            if self.velocity.x > 0:
                self.position.x = round(projected_position.x + self.size.x / 2) - (1 + self.size.x) / 2  - .002 + .5
            if self.velocity.x < 0:
                self.position.x = round(projected_position.x - self.size.x / 2) + (1 + self.size.x) / 2  + .002 - .5
            self.sprint = False
            self.velocity.x = 0
        else: 
            # No collision, so set x to projected x
            self.position.x = projected_position.x
        if collide_y:
            # Snap tp grid on y axis
            if self.velocity.y > 0:
                self.position.y = round(projected_position.y + self.size.y / 2) - (1 + self.size.y) / 2  - .001 + .5
            if self.velocity.y < 0:
                self.position.y = round(projected_position.y - self.size.y / 2) + (1 + self.size.y) / 2  + .001 - .5
            if self.velocity.y < 3:
                self.has_jump = True
            self.velocity.y = 0
        else: 
            # No collision, so set y to projected y
            self.position.y = projected_position.y
        if collide_z:
            # Snap tp grid on z axis
            if self.velocity.z > 0:
                self.position.z = round(projected_position.z + self.size.z / 2) - (1 + self.size.z) / 2  - .001 + .5
            if self.velocity.z < 0:
                self.position.z = round(projected_position.z - self.size.z / 2) + (1 + self.size.z) / 2  + .001 - .5
            self.sprint = False
            self.velocity.z = 0
        else: 
            # No collision, so set y to projected z
            self.position.z = projected_position.z
    
    def apply_inputs(self) -> None:
        """
        Applies all needed player inputs
        """
        
        # get delta time
        dt = self.scene.engine.dt

        # Get the current input states
        keys = self.scene.engine.keys
        prev_keys = self.scene.engine.prev_keys
        mouse_buttons = self.scene.engine.mouse_buttons
        prev_mouse_buttons = self.scene.engine.prev_mouse_buttons

        # Breaking a block
        if mouse_buttons[0] and not prev_mouse_buttons[0]:
            if self.target_voxel: self.chunk_handler.set_voxel(*self.target_voxel[:3], 0)
        
        # Place a block
        if mouse_buttons[2] and not prev_mouse_buttons[2]:
            if self.target_voxel: 
                place_position = self.target_voxel[0] + self.target_voxel[3][0], self.target_voxel[1] + self.target_voxel[3][1], self.target_voxel[2] + self.target_voxel[3][2]
                if  self.can_place(glm.vec3(*place_position)): self.chunk_handler.set_voxel(*place_position, 3)


        # Reset the velocity to accelerate towards
        self.target_velocity = glm.vec3(0, self.velocity.y, 0)

        # Updates sprint state
        if keys[pg.K_CAPSLOCK]: self.sprint = True
        if not keys[pg.K_w]: self.sprint = False

        # Update flying state
        if keys[pg.K_f] and not prev_keys[pg.K_f]: self.flying = not self.flying

        # Update the movement paramters based on player state
        if self.flying: self.set_movement(speed=20, acceleration=7)
        elif not self.is_grounded(): self.set_movement(speed=4.317, acceleration=5.5)
        else: self.set_movement(speed=4.317, acceleration=12)

        # Update the target velocity based on the inputs and current state
        run_jump = 1.1 * (not self.is_grounded() and self.sprint)
        forward_speed = ((self.speed + run_jump) + (self.speed + run_jump) * self.sprint * .3)
        self.target_velocity += forward_speed * (keys[pg.K_w] - keys[pg.K_s]) * glm.normalize(glm.vec3(self.forward.x, 0, self.forward.z)) + self.speed * (keys[pg.K_d] - keys[pg.K_a]) * self.right

        # Different effects of flying
        if self.flying:
            self.target_velocity.y = (self.speed * (keys[pg.K_SPACE] - keys[pg.K_LSHIFT]) * self.UP).y
        else:
            if not self.is_grounded():
                self.velocity.y -= self.gravity * dt
            elif keys[pg.K_SPACE] and self.has_jump:
                self.velocity.y = 8.8
                self.has_jump = False
            
        # Linearly interpolates velocity toward the target velocity
        self.velocity += (self.target_velocity - self.velocity) * self.acceleration * dt

    def raycast(self, max_distance: int=5) -> tuple:
        """
        Casts a ray from the player to a voxel. Returns either a tuple with the location of the voxel or False if no voxel is hit in the given max_distance.
        """
        # Resolution
        res = 12

        # Vector of the direction of the camera
        direction = glm.normalize(glm.vec3(cos(glm.radians(self.yaw)) * cos(glm.radians(self.pitch)), sin(glm.radians(self.pitch)), sin(glm.radians(self.yaw)) * cos(glm.radians(self.pitch)))) / res
        # Starting position of the ray (camera position)
        position = self.position + glm.vec3(-0.5, 0.72 - 0.5, -0.5)
        # Face that the ray hits
        face = None

        # Loop until a hit
        for i in range(res * max_distance):
            # Increment the position in each direction
            position.x += direction.x
            if self.chunk_handler.get_voxel_id(position.x, position.y, position.z): 
                face = ((direction.x < 0) * 2 - 1, 0, 0)
                break

            position.y += direction.y
            if self.chunk_handler.get_voxel_id(position.x, position.y, position.z): 
                face = (0, (direction.y < 0) * 2 - 1, 0)
                break

            position.z += direction.z
            if self.chunk_handler.get_voxel_id(position.x, position.y, position.z): 
                face = (0, 0, (direction.z < 0) * 2 - 1)
                break

        if face: return round(position.x), round(position.y), round(position.z), face # Round to the nearest voxel
        
        # No hit
        return False

    def collide(self, projected_position: glm.vec3) -> tuple:
        """
        Returns a tuple of bools: (x_collide: bool, y_collide: bool, z_collide: bool)
        """

        collide_x, collide_y, collide_z = False, False, False

        # We check each corner of the player for collision
        hit_points = (glm.vec3(-self.size.x / 2, -self.size.y / 2, -self.size.z / 2), glm.vec3( self.size.x / 2, -self.size.y / 2, -self.size.z / 2),
                      glm.vec3(-self.size.x / 2,  self.size.y / 2, -self.size.z / 2), glm.vec3(-self.size.x / 2, -self.size.y / 2,  self.size.z / 2),
                      glm.vec3(-self.size.x / 2,  self.size.y / 2,  self.size.z / 2), glm.vec3( self.size.x / 2, -self.size.y / 2,  self.size.z / 2),
                      glm.vec3( self.size.x / 2,  self.size.y / 2, -self.size.z / 2), glm.vec3( self.size.x / 2,  self.size.y / 2,  self.size.z / 2))

        # Loop through each corner
        for hit_point in hit_points:
            # Gets the positions of the projected corner position in each axis
            x_position_check = glm.vec3(projected_position.x, self.position.y, self.position.z) + hit_point - glm.vec3(.5)
            y_position_check = glm.vec3(self.position.x, projected_position.y, self.position.z) + hit_point - glm.vec3(.5)
            z_position_check = glm.vec3(self.position.x, self.position.y, projected_position.z) + hit_point - glm.vec3(.5)
            # Checks for collisions
            if self.chunk_handler.get_voxel_id(x_position_check.x, x_position_check.y, x_position_check.z): collide_x = True
            if self.chunk_handler.get_voxel_id(y_position_check.x, y_position_check.y, y_position_check.z): collide_y = True
            if self.chunk_handler.get_voxel_id(z_position_check.x, z_position_check.y, z_position_check.z): collide_z = True
        
        return collide_x, collide_y, collide_z

    def can_place(self, place_position: glm.vec3):
        """
        Used to check if a block can be placed in a position
        """

        # We check each corner of the player for collision
        hit_points = (glm.vec3(-self.size.x / 2, -self.size.y / 2, -self.size.z / 2), glm.vec3( self.size.x / 2, -self.size.y / 2, -self.size.z / 2),
                      glm.vec3(-self.size.x / 2,  self.size.y / 2, -self.size.z / 2), glm.vec3(-self.size.x / 2, -self.size.y / 2,  self.size.z / 2),
                      glm.vec3(-self.size.x / 2,  self.size.y / 2,  self.size.z / 2), glm.vec3( self.size.x / 2, -self.size.y / 2,  self.size.z / 2),
                      glm.vec3( self.size.x / 2,  self.size.y / 2, -self.size.z / 2), glm.vec3( self.size.x / 2,  self.size.y / 2,  self.size.z / 2))

        # Loop through each corner
        for hit_point in hit_points:
            # Gets the positions of the projected corner position in each axis
            position_check = self.position + hit_point - glm.vec3(.5)
            # Round to voxel
            position_check.x = round(position_check.x)
            position_check.y = round(position_check.y)
            position_check.z = round(position_check.z)
            # Checks for collisions
            if position_check == place_position: return False
        
        return True

    def is_grounded(self) -> bool:
        """
        Returns a bool. True if the player is on the ground, else false
        """
        
        # We check each corner of the player's feet for collision
        hit_points = (glm.vec3(-self.size.x / 2, -self.size.y / 2, -self.size.z / 2), glm.vec3( self.size.x / 2, -self.size.y / 2, -self.size.z / 2),
                      glm.vec3(-self.size.x / 2, -self.size.y / 2,  self.size.z / 2), glm.vec3( self.size.x / 2, -self.size.y / 2,  self.size.z / 2))
        
        # Check each hit point
        for hit_point in hit_points:
            position_check = self.position + hit_point - glm.vec3(.5, .51, .5)
            if self.chunk_handler.get_voxel_id(position_check.x, position_check.y, position_check.z):
                # Point collided
                return True 
        
        # No point has collided
        return False 
    
    def set_movement(self, speed: float=20, acceleration: float=13, jump_speed: float=8.8, gravity: float=31.36) -> None:
        """
        Sets the movement parameters. Provide False to leave a value unchanged
        """
        
        if speed: self.speed = speed  # Voxels per second
        if acceleration: self.acceleration = acceleration  # Voxels per second^2
        if jump_speed: self.jump_speed = jump_speed  # Voxels per second
        if gravity: self.gravity = gravity  # Voxels per second^2
