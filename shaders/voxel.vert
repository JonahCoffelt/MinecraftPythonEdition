#version 330 core


layout (location = 0) in ivec3 in_position;
layout (location = 1) in int in_id;
layout (location = 2) in int in_face;
layout (location = 3) in int in_ao;


out vec3 uv;
out float face_shading;


uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

uniform int textures[192];

const float ao_values[4] = float[4](
    0.45, 0.6, 0.75, 1.0
);

const vec2 uv_coords[4] = vec2[4](
    vec2(0, 0), vec2(0, 1), vec2(1, 0), vec2(1, 1)
);

const int uv_indicies[12] = int[12](
    1, 0, 2, 1, 2, 3,
    3, 0, 2, 3, 1, 0
);

const vec3 faceNormals[6] = vec3[6](
    vec3(0, 1, 0), vec3(0, -1, 0),
    vec3(1, 0, 0), vec3(-1, 0, 0),
    vec3(0, 0, 1), vec3(0, 0, -1)
);

void main() {
    int uv_index = gl_VertexID % 6 + (in_face & 1) * 6;
    uv = vec3(uv_coords[uv_indicies[uv_index]], textures[in_face + (in_id - 1) * 6]);
    face_shading = (abs(dot(normalize(vec3(.5, 1, .25)), faceNormals[in_face]))/2 + .5) * ao_values[in_ao];
    
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}