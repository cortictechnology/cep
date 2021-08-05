#version 300 es

precision mediump float;

in vec2 a_vertex;
in vec2 a_tex_coord;

uniform mat4 u_projection_matrix;

out vec2 tex_coords;

void main() {
    tex_coords = a_tex_coord;
    gl_Position = u_projection_matrix * vec4(a_vertex, 0, 1);
}
