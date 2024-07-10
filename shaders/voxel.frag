#version 330 core

layout (location = 0) out vec4 frameFragColor;


in vec3 uv;
in float face_shading;


uniform sampler2DArray textureArray;



void main() {
    vec3 color = texture(textureArray, uv).rgb;
    color = color * face_shading;
    frameFragColor = vec4(color, 1.0);
}