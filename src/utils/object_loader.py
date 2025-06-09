# funções associadas ao carregamento de objetos, vértices e texturas
from OpenGL.GL import *
from PIL import Image

def read_obj_from_file(filename):
    """Reads a Wavefront OBJ file. """
    obj = {
        'positions': [],
        'texture_coords': [],
        'normals': [],
        'faces': []
    }

    # abre o arquivo obj para leitura
    for line in open(filename, "r"): ## para cada linha do arquivo .obj
        if line.startswith('#'): continue ## ignora comentarios
        values = line.split() # quebra a linha por espaço
        if not values: continue

        ### recuperando posição dos vértices
        if values[0] == 'v':
            obj['positions'].append(values[1:4])

        ### recuperando normais
        if values[0] == 'vn':
            obj['normals'].append(values[1:4])

        ### recuperando coordenadas de textura
        elif values[0] == 'vt':
            obj['texture_coords'].append(values[1:3])

        ### recuperando faces
        elif values[0] == 'f':
            vertice_pos_indices = []
            texture_coord_indices = []
            normal_indices = []
            for vertex in values[1:]:
                vertex_attributes = vertex.split('/')
                vertice_pos_indices.append(int(vertex_attributes[0]))
                if len(vertex_attributes) > 1:
                    texture_coord_indices.append(int(vertex_attributes[1]))
                if len(vertex_attributes) > 2:
                    normal_indices.append(int(vertex_attributes[2]))

            obj['faces'].append(dict(vertex_pos=vertice_pos_indices, texture_coord=texture_coord_indices, normal=normal_indices))

    return obj

# --------------------------------------------------------

def load_texture_from_file(texture_id, texture_img):
    print(texture_id, texture_img)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    img = Image.open(texture_img).convert("RGBA")
    img_width = img.size[0]
    img_height = img.size[1]
    image_data = img.tobytes("raw", "RGBA", 0, -1)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

# --------------------------------------------------------

def load_cubemap_texture_from_files(texture_id, texture_imgs_list):
    print(texture_id, texture_imgs_list)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, texture_id)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    for i, texture_img in enumerate(texture_imgs_list):
        img = Image.open(texture_img)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img_width = img.size[0]
        img_height = img.size[1]
        image_data = img.tobytes("raw", "RGB", 0, -1)
        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB, img_width, img_height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

# --------------------------------------------------------

def circular_sliding_window_of_three(arr):
    # Créditos: Hélio Nogueira Cardoso e Danielle Modesti (SCC0650 - 2024/2).
    if len(arr) == 3:
        return arr
    circular_arr = arr + [arr[0]]
    result = []
    for i in range(len(circular_arr) - 2):
        result.extend(circular_arr[i:i+3])
    return result

# --------------------------------------------------------

class ObjManager:
    def __init__(self):
        self.objects = []
        self.curr_texture_id = 1

    # --------------------------------------------------------

    def load_obj(self, objFile):
        modelo = read_obj_from_file(objFile)

        new_object = {
            'positions': [],
            'texture_coords': [],
            'normals': [],
            'num_vertices': 0
        }

        for face in modelo['faces']:
            for position_id in circular_sliding_window_of_three(face['vertex_pos']):
                new_object['positions'] += modelo['positions'][position_id - 1]
            for texture_id in circular_sliding_window_of_three(face['texture_coord']):
                new_object['texture_coords'] += modelo['texture_coords'][texture_id - 1]
            for normal_id in circular_sliding_window_of_three(face['normal']):
                new_object['normals'] += modelo['normals'][normal_id - 1]
        # três vértices por face
        new_object['num_vertices'] = len(new_object['positions']) // 3

        self.objects.append(new_object)

    # --------------------------------------------------------

    def load_texture(self, texture_path, cube_map=False):
        if cube_map:
            load_cubemap_texture_from_files(self.curr_texture_id, texture_path)
        else:
            load_texture_from_file(self.curr_texture_id, texture_path)
        self.curr_texture_id += 1
        return self.curr_texture_id-1

    # --------------------------------------------------------

    def get_attribute_arrays(self):
        all_vertices = {
            'positions': [],
            'texture_coords': [],
            'normals': [],
        }
        num_vertices = 0

        for obj in self.objects:
            for attribute in all_vertices:
                all_vertices[attribute] += obj[attribute]
            num_vertices += obj['num_vertices']
        
        return all_vertices, num_vertices

    # --------------------------------------------------------

    def get_vertices_slice(self, obj_index):
        acum_len = 0
        for i in range(obj_index):
            acum_len += self.objects[i]['num_vertices']
        
        initial_vertex_index = acum_len
        num_vertices = self.objects[obj_index]['num_vertices']

        return initial_vertex_index, num_vertices

# --------------------------------------------------------
