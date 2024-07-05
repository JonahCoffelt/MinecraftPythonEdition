#version 330 core

layout (location = 0) out vec4 fragColor;


in vec2 uv;
uniform vec2 voxelID;


struct textArray {
    sampler2DArray array;
};

uniform textArray textureArrays[3];


void main() {
    vec3 color = texture(textureArrays[int(0)].array, vec3(uv, 0)).rgb;
    //vec3 color = vec3(1.0, 1.0, 0.0) * min(max(dot(vec3(0.15, 1.0, 0.25), normal), 0) + .5, 1);
    fragColor = vec4(color, 1.0);
}