#version 300 es

precision mediump float;

in vec2 tex_coords;

uniform sampler2D video_texture;

out vec4 frag_color;

void main() {
    frag_color = texture(video_texture, tex_coords);    
}
