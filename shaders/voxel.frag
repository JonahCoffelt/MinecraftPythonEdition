#version 330 core

layout (location = 0) out vec4 fragColor;


in vec2 uv;
in vec3 normal;

struct textArray {
    sampler2DArray array;
};

uniform textArray textureArrays[3];


void main() {
    vec3 color = texture(textureArrays[int(0)].array, vec3(uv, 0)).rgb;
    color = color * (abs(dot(normalize(vec3(.5, 1, .25)), normal))/2 + .25);
    fragColor = vec4(color, 1.0);
}