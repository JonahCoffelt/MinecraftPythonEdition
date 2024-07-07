#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv;

uniform sampler2D frameTexture;
uniform sampler2D uiTexture;

void main() {
    vec4 ui = texture(uiTexture, uv * vec2(1.0, -1.0));
    fragColor = texture(frameTexture, uv);

    vec3 final_color = ui.bgr * ui.w + fragColor.rgb * (1 - ui.w);
    fragColor.rgb = final_color;
}