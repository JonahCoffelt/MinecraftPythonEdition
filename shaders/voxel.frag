#version 330 core

layout (location = 0) out vec4 frameFragColor;


in vec3 uv;
in float face_shading;


uniform sampler2DArray textureArray;


// Fog Variables
float NEAR = 0.1;
float FAR = 250.0;
float density = 1.5;
vec3 fog_color = vec3(0.8, 0.9, 1.0);


void main() {
    vec3 color = texture(textureArray, uv).rgb;
    color = color * face_shading;
    frameFragColor = vec4(color, 1.0);
    float depth = (1 - FAR / NEAR) * gl_FragCoord.z + (FAR / NEAR);
    depth = 1.0 / depth;
    float fog_factor = pow(2, -pow(depth * density, 2));
    frameFragColor.rgb = mix(fog_color, frameFragColor.rgb, fog_factor);
}