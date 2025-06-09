#version 330 core

in vec2 texture_coord;

uniform vec3 color;
uniform sampler2D imagem;

void main(){
	gl_FragColor = texture2D(imagem, texture_coord) + vec4(color, 1.0);
}
