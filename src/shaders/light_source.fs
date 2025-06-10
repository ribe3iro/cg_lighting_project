#version 330 core

in vec2 texture_coord;

uniform vec4 color;
uniform sampler2D imagem;

void main(){
	gl_FragColor = vec4(vec3(texture2D(imagem, texture_coord)), 0) + color;
}
