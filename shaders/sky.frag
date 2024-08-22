#version 330 core

layout (location = 0) out vec4 frag_color;

uniform vec3 fogColor;
uniform vec3 planeColor;

in vec3 v_viewpos;

float NEAR = 0.1;
float FAR = 250.0;

void main() {
    float fog = smoothstep(NEAR, FAR, length(v_viewpos));
    frag_color = vec4(mix(planeColor, fogColor, fog).rgb, 1.0);
}