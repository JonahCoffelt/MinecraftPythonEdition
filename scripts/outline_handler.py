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

        # Render
        self.vao_handler.vaos['outline'].render(mgl.LINES)

        if not self.player.mining_timer: return
        
        m_model = glm.mat4()
        m_model = glm.translate(m_model, glm.vec3(*self.player.current_mine_block[:3]) + glm.vec3(0.501))
        m_model = glm.scale(m_model, glm.vec3(.502))
        
        mining_progress = 86 + int((self.player.mining_timer / self.player.mining_duration) * 7)

        self.vao_handler.shader_handler.programs['default']['m_model'].write(m_model)
        self.vao_handler.shader_handler.programs['default']['texture_id'].write(glm.int32(mining_progress))

        self.vao_handler.vaos['mining'].render()