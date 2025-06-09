#version 330 core

struct Decay {
	float constant;
	float linear;
	float quadratic;
};

struct PointLight {
    vec3 position;
	vec3 color;
	Decay decay;
};

struct ReflectionCoeff {
	float ka;
	float kd;
	float ks;
	float ns;
};

#define NR_POINT_LIGHTS 4

in vec2 texture_coord;
in vec3 frag_pos;
in vec3 normal;

uniform vec3 view_pos;
uniform PointLight pointLights[NR_POINT_LIGHTS];
uniform ReflectionCoeff reflectionCoeff;

uniform sampler2D imagem;

void main(){
	// reflexão ambiente
	vec3 ambient = reflectionCoeff.ka * vec3(1.0, 1.0, 1.0);

	vec3 diffuse = vec3(0.0, 0.0, 0.0);
	vec3 specular = vec3(0.0, 0.0, 0.0);

	vec3 norm = normalize(normal);
	vec3 light_dir; vec3 view_dir; vec3 reflect_dir;
	float diff; float spec;
	float distance; float attenuation;
	for(int i = 0; i < NR_POINT_LIGHTS; i++){
		// atenuação
		distance = length(pointLights[i].position - frag_pos);
		attenuation = pointLights[i].decay.constant;
		attenuation+= (pointLights[i].decay.linear) * distance;
		attenuation+= (pointLights[i].decay.quadratic) * (distance * distance);
		attenuation = 1 / attenuation;

		// reflexão difusa
		light_dir = normalize(pointLights[i].position - frag_pos);
		diff = max(dot(norm, light_dir), 0.0);
		diffuse += reflectionCoeff.kd * diff * attenuation * pointLights[i].color;

		// reflexão especular
		view_dir = normalize(view_pos - frag_pos);
		reflect_dir = reflect(-light_dir, norm);
		spec = pow(max(dot(view_dir, reflect_dir), 0.0), reflectionCoeff.ns);
		specular += reflectionCoeff.ks * spec * attenuation * pointLights[i].color;
	}
	
	// aplicando o modelo de iluminacao
	vec4 texture = texture2D(imagem, texture_coord);
	vec4 final_color = vec4((ambient + diffuse + specular), 1.0) * texture; // aplica iluminacao
	gl_FragColor = final_color;
}
