#version 330 core


layout (location = 0) in vec3 in_position;
layout (location = 1) in vec2 in_texcoord;

in float in_instance_id;
in vec3 in_instance_position;
in float in_instance_rotation;


uniform mat4 m_proj;
uniform mat4 m_view;


out vec3 uv;


void main() {
    uv = vec3(in_texcoord.x, -in_texcoord.y, in_instance_id);

    vec3 instance_pos = in_instance_position;
    instance_pos.y += sin(in_instance_rotation * 1.5)/8;

    float size = .2;

    mat4 m_model = mat4(
        size, 0.0, 0.0, 0.0,
        0.0, size, 0.0, 0.0,
        0.0, 0.0, size, 0.0,
        instance_pos.x, instance_pos.y, instance_pos.z, 1.0
    );

    mat4 y_rot = mat4(
        cos(in_instance_rotation), 0.0, sin(in_instance_rotation), 0.0,
        0.0, 1.0, 0.0, 0.0,
        -sin(in_instance_rotation), 0.0, cos(in_instance_rotation), 0.0,
        0.0, 0.0, 0.0, 1.0
    );

    m_model = m_model * y_rot;

    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}