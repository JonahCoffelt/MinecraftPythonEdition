#version 330 core

layout (location = 0) out vec4 fragColor;

in vec3 uv;

uniform sampler2DArray textureArray;


void main() {
    fragColor = texture(textureArray, uv);
    if (fragColor.a <= 0.1) {
        discard;
    }
}