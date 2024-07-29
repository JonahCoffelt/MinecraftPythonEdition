import moderngl as mgl
import glm


class OutlineHandler:
    def __init__(self, player, vao_handler) -> None:
        self.player = player
        self.vao_handler = vao_handler
    
    def render(self):
        # Check if player is looking at a block
        if not self.player.target_voxel: return

        # Upload the voxel position to the shader
        voxel_position = glm.vec3(*self.player.target_voxel[:3])
        self.vao_handler.shader_handler.programs['outline']['voxel_position'].write(voxel_position)

        # Redner
        self.vao_handler.vaos['outline'].render(mgl.LINES)