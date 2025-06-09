#version 330 core

in vec3 aPosition;
in vec2 aTexture_coord;
in vec3 aNormal;

out vec2 texture_coord;
out vec3 frag_pos;
out vec3 normal;
		
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;        

void main(){
	gl_Position = projection * view * model * vec4(aPosition,1.0);
	texture_coord = vec2(aTexture_coord);
	frag_pos = vec3(  model * vec4(aPosition, 1.0));
	normal = mat3(transpose(inverse(model))) * aNormal;
}