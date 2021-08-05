#version 300 es
#extension GL_OES_standard_derivatives: enable

precision mediump float;

in vec3 color;
in vec3 barycentric;
in vec3 position;

out vec4 frag_color;

float edgeFactor() {
    vec3 d = fwidth(barycentric);
    vec3 a3 = smoothstep(vec3(0.0), d*1.5, barycentric);
    return min(min(a3.x, a3.y), a3.z);
}

void main() { 
    frag_color = vec4(color, (1.0-edgeFactor()*0.95));
}
