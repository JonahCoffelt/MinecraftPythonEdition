#version 330 core

layout (location = 0) out vec4 fragColor;


in vec3 uv;
in vec3 normal;


uniform sampler2DArray textureArray;



void main() {
    vec3 color = texture(textureArray, uv).rgb;
    color = color * (abs(dot(normalize(vec3(.5, 1, .25)), normal))/2 + .5);
    fragColor = vec4(color, 1.0);
}