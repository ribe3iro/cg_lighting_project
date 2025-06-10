"""
Projeto 3 - Iluminação de ambientes
Disciplina SCC0250 - Computação Gráfica

----------------------------------------------------------

João Pedro Ribeiro da Silva - 12563727
Miller Matheus Lima Anacleto Rocha - 13727954

Código baseado naqueles desenvolvidos e disponibilizados pelo professor
"""

# bibliotecas
import glfw
from OpenGL.GL import *
import numpy as np
import math
import glm
from numpy import random
import os
path_join = os.path.join

# códigos externos
from shaders.shader_s import Shader
from utils.object_loader import ObjManager
from utils.transformations_pipeline import model, view, projection

# funções auxiliares
def model_objeto(program, t_x=0, t_y=0, t_z=0, s_x=1, s_y=1, s_z=1, r_x=0, r_y=0, r_z=0):
    # aplica a matriz model
    mat_model = model(t_x, t_y, t_z,  # translação
                    s_x, s_y, s_z,  # escala
                    r_x, r_y, r_z)  # rotação
    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)

# --------------------------------------------------------

def desenha_objeto(vertice_inicial, num_vertices, shader, color=None, alpha=1, texture_id=-1, ka=0.2, kd=0.8, ks=0.3, ns=10, cube_map=False, light_source=False, brightness=1):
    # texture
    if texture_id >= 0:
        shader.setVec4('color', *[0,0,0,alpha])
        if cube_map:
            glBindTexture(GL_TEXTURE_CUBE_MAP, texture_id)
        else:
            glBindTexture(GL_TEXTURE_2D, texture_id)
    # color
    elif color is not None:
        shader.setVec4('color', *color)
    else:
        return

    if light_source:
        shader.setFloat('brightness', brightness)
    else:
        shader.setFloat('reflectionCoeff.ka', max(0, min(1, ka)))
        shader.setFloat('reflectionCoeff.kd', max(0, min(1, kd)))
        shader.setFloat('reflectionCoeff.ks', max(0, min(1, ks)))
        shader.setFloat('reflectionCoeff.ns', max(0, min(1, ns)))
    
    # desenha o objeto
    glDrawArrays(GL_TRIANGLES, vertice_inicial, num_vertices) ## renderizando

# --------------------------------------------------------

def camera_movement_handler():
    global window, cameraFront, cameraUp 
    global cameraVel, CAMERA_SPEED_WALKING, CAMERA_SPEED_RUNNING, flying_state
    global haunter_t, deltaTime

    OBJ_MOVE_SPEED = 1
    camera_speed = CAMERA_SPEED_WALKING

    if flying_state:
        frontDir = cameraFront
    else:
        frontDir = glm.vec3(cameraFront.x, 0.0, cameraFront.z)

    # W - mover câmera (frente)
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        cameraVel += glm.normalize(frontDir)
    # S - mover câmera (trás)
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        cameraVel -= glm.normalize(frontDir)
    # A - mover câmera (esquerda)
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        cameraVel -= glm.normalize(glm.cross(frontDir, cameraUp))
    # D - mover câmera (direita)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        cameraVel += glm.normalize(glm.cross(frontDir, cameraUp))
    # SHIFT - correr
    if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
        camera_speed = CAMERA_SPEED_RUNNING

    if glm.length(cameraVel) > 0:
        cameraVel = glm.normalize(cameraVel) * camera_speed

    ###################################    
    if glfw.get_key(window, glfw.KEY_G) == glfw.PRESS:
        haunter_t += OBJ_MOVE_SPEED * deltaTime
          
    if glfw.get_key(window, glfw.KEY_H) == glfw.PRESS:
        haunter_t -= OBJ_MOVE_SPEED * deltaTime
        
    

# funções callback
def key_event(window,key,scancode,action,mods):
    global cameraPos
    global papelPos, papelEscala, pegandoPapel, papelVisivel
    global ka_offset, kd_offset, ks_offset
    global lights_on
    global show_lines, flying_state, mostrar_corpo
    # ESC - fechar janela
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)
    
    # ESPAÇO - mostrar corpo do fantasma
    if key == glfw.KEY_SPACE and action == glfw.PRESS:
        mostrar_corpo = not mostrar_corpo

    # P - toggle malha poligonal
    if key == glfw.KEY_P and action == glfw.PRESS:
        show_lines = not show_lines
        if show_lines:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # F - toggle voar
    if key == glfw.KEY_F and action == glfw.PRESS:
        flying_state = not flying_state
        if not flying_state:
            cameraPos.y = CAMERA_HEIGHT

    # E - pegar nota
    if key == glfw.KEY_E and action == glfw.PRESS:
        distToNote = glm.distance(cameraPos, papelPos)
        if distToNote < 2:
            pegandoPapel = True
            papelVisivel = not papelVisivel

    # 1 - toggle luz dos olhos
    if key == glfw.KEY_1 and action == glfw.PRESS:
        lights_on['olhos'] = not lights_on['olhos']

    # 2 - toggle luz do portal
    if key == glfw.KEY_2 and action == glfw.PRESS:
        lights_on['portal'] = not lights_on['portal']

    # 3 - toggle luz da lanterna
    if key == glfw.KEY_3 and action == glfw.PRESS:
        lights_on['lantern'] = not lights_on['lantern']

    # 4 - toggle luz do fantasma
    if key == glfw.KEY_4 and action == glfw.PRESS:
        lights_on['fantasma'] = not lights_on['fantasma']

    # Z - diminuir coeficiente de reflexão ambiente base
    if key == glfw.KEY_Z and action == glfw.PRESS:
        ka_offset -= 0.05
    
    # X - aumentar coeficiente de reflexão ambiente base
    if key == glfw.KEY_X and action == glfw.PRESS:
        ka_offset += 0.05
    ka_offset = max(-1, min(ka_offset, 1))

    # C - diminuir coeficiente de reflexão difusa base
    if key == glfw.KEY_C and action == glfw.PRESS:
        kd_offset -= 0.05
    
    # V - aumentar coeficiente de reflexão difusa base
    if key == glfw.KEY_V and action == glfw.PRESS:
        kd_offset += 0.05
    kd_offset = max(-1, min(kd_offset, 1))

    # B - diminuir coeficiente de reflexão especular base
    if key == glfw.KEY_B and action == glfw.PRESS:
        ks_offset -= 0.05
    
    # N - aumentar coeficiente de reflexão especular base
    if key == glfw.KEY_N and action == glfw.PRESS:
        ks_offset += 0.05
    ks_offset = max(-1, min(ks_offset, 1))

def framebuffer_size_callback(window, largura, altura):
    glViewport(0, 0, largura, altura)

# --------------------------------------------------------

def mouse_event(window, xpos, ypos):
    global cameraFront, lastX, lastY, firstMouse, yaw, pitch

    if (firstMouse):
        lastX = xpos
        lastY = ypos
        firstMouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos # reversed since y-coordinates go from bottom to top
    lastX = xpos
    lastY = ypos

    sensitivity = 0.1 # change this value to your liking
    xoffset *= sensitivity
    yoffset *= sensitivity

    yaw += xoffset
    pitch += yoffset

    # make sure that when pitch is out of bounds, screen doesn't get flipped
    if (pitch > 89.0):
        pitch = 89.0
    if (pitch < -89.0):
        pitch = -89.0
    
    front = glm.vec3()
    front.x = glm.cos(glm.radians(yaw)) * glm.cos(glm.radians(pitch))
    front.y = glm.sin(glm.radians(pitch))
    front.z = glm.sin(glm.radians(yaw)) * glm.cos(glm.radians(pitch))
    cameraFront = glm.normalize(front)

# --------------------------------------------------------

def scroll_event(window, xoffset, yoffset):
    global fov

    fov -= yoffset
    if (fov < 1.0):
        fov = 1.0
    if (fov > 45.0):
        fov = 45.0

# MAIN
if __name__ == '__main__':
    ### CONSTANTES IMPORTANTES
    ABSOLUTE_ROOT_PATH, _ = os.path.split(os.path.dirname(os.path.realpath(__file__)))
    OBJECTS_PATH = path_join(ABSOLUTE_ROOT_PATH, 'objetos')
    TEXTURES_PATH = path_join(ABSOLUTE_ROOT_PATH, 'texturas')
    LARGURA_JANELA = 700
    ALTURA_JANELA = 700

    ### INICIALIZANDO JANELA
    glfw.init()
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

    window = glfw.create_window(LARGURA_JANELA, ALTURA_JANELA, "Cabana Assombrada", None, None)

    if (window == None):
        print("Failed to create GLFW window")
        glfwTerminate()
        exit(1)

    glfw.make_context_current(window)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    ### SHADERS
    shaders_path = path_join(ABSOLUTE_ROOT_PATH, 'src', 'shaders')

    DEFAULT_SHADER = Shader(
        path_join(shaders_path, 'default.vs'),
        path_join(shaders_path, 'default.fs')
    )

    LIGHT_SOURCE_SHADER = Shader(
        path_join(shaders_path, 'default.vs'),
        path_join(shaders_path, 'light_source.fs')
    )
    LIGHT_SOURCE_SHADER.use()
    LIGHT_SOURCE_SHADER.setVec4('color', *[0,0,0,0])

    SKYBOX_SHADER = Shader(
        path_join(shaders_path, 'skybox.vs'),
        path_join(shaders_path, 'skybox.fs')
    )
    SKYBOX_SHADER.use()
    glUniform1i(glGetUniformLocation(SKYBOX_SHADER.getProgram(), "skybox"), 0)

    ### CARREGANDO OBJETOS

    ## SKYBOX

    # vértices
    skyboxVertices = [
        [-1.0, -1.0,  1.0],
        [1.0, -1.0,  1.0],
        [1.0, -1.0, -1.0],
        [-1.0, -1.0, -1.0],
        [-1.0,  1.0,  1.0],
        [1.0,  1.0,  1.0],
        [1.0,  1.0, -1.0],
        [-1.0,  1.0, -1.0]
    ]

    skyboxIndices = [
        1, 2, 6,
        6, 5, 1,
        0, 4, 7,
        7, 3, 0,
        4, 5, 6,
        6, 7, 4,
        0, 3, 2,
        2, 1, 0,
        0, 1, 5,
        5, 4, 0,
        3, 7, 6,
        6, 2, 3
    ]

    vertices = []
    for i in skyboxIndices:
        vertices.append(skyboxVertices[i])
    allSkyboxVertices = np.zeros(len(vertices), [("position", np.float32, 3)])
    allSkyboxVertices['position'] = vertices

    skyboxVAO = glGenVertexArrays(1)
    skyboxVBO = glGenBuffers(1)

    glBindVertexArray(skyboxVAO)

    glBindBuffer(GL_ARRAY_BUFFER, skyboxVBO)
    glBufferData(GL_ARRAY_BUFFER, allSkyboxVertices.nbytes, allSkyboxVertices, GL_STATIC_DRAW)

    stride = allSkyboxVertices.strides[0]
    offset = ctypes.c_void_p(0)
    loc_vertices = glGetAttribLocation(SKYBOX_SHADER.getProgram(), "aPos")
    glEnableVertexAttribArray(loc_vertices)
    glVertexAttribPointer(loc_vertices, 3, GL_FLOAT, False, stride, offset)

    # texturas
    skybox_root_path = path_join(ABSOLUTE_ROOT_PATH, 'texturas', 'skybox')
    skybox_textures_list = []
    skybox_textures_list.append(path_join(skybox_root_path, 'right.png'))
    skybox_textures_list.append(path_join(skybox_root_path, 'left.png'))
    skybox_textures_list.append(path_join(skybox_root_path, 'top.png'))
    skybox_textures_list.append(path_join(skybox_root_path, 'bottom.png'))
    skybox_textures_list.append(path_join(skybox_root_path, 'front.png'))
    skybox_textures_list.append(path_join(skybox_root_path, 'back.png'))

    obj_manager = ObjManager()
    skyboxTexture = obj_manager.load_texture(skybox_textures_list, cube_map=True)

    ## FONTES DE LUZ

    light_source_manager = ObjManager()

    # vértices
    light_source_manager.load_obj(path_join(OBJECTS_PATH, 'olhos.obj'))
    light_source_manager.load_obj(path_join(OBJECTS_PATH, 'portal.obj'))
    light_source_manager.load_obj(path_join(OBJECTS_PATH, 'lantern.obj'))
    light_source_manager.load_obj(path_join(OBJECTS_PATH, 'fantasma.obj'))

    # vec3 aPosition
    attributes, num_vertices = light_source_manager.get_attribute_arrays()

    vertices = np.zeros((num_vertices, 3*2), dtype=np.float32)
    vertices[:, 0:3] = np.reshape(attributes['positions'], (-1, 3))
    vertices[:, 3:5] = np.reshape(attributes['texture_coords'], (-1, 2))
    
    vertices = vertices.flatten()

    # carregando na GPU
    light_sourcesVAO = glGenVertexArrays(1)
    light_sourcesVBO = glGenBuffers(1)

    glBindVertexArray(light_sourcesVAO)
    glBindBuffer(GL_ARRAY_BUFFER, light_sourcesVBO)

    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    loc_pos = glGetAttribLocation(LIGHT_SOURCE_SHADER.getProgram(), "aPosition")
    glEnableVertexAttribArray(loc_pos)
    glVertexAttribPointer(loc_pos, 3, GL_FLOAT, False, 3*2 * glm.sizeof(glm.float32), ctypes.c_void_p(0))

    loc_texture = glGetAttribLocation(LIGHT_SOURCE_SHADER.getProgram(), "aTexture_coord")
    glEnableVertexAttribArray(loc_texture)
    glVertexAttribPointer(loc_texture, 2, GL_FLOAT, False, 3*2 * glm.sizeof(glm.float32), ctypes.c_void_p(3 * glm.sizeof(glm.float32)))

    ## DEMAIS OBJETOS
    DEFAULT_SHADER.use()

    # vértices
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'chao.obj'))
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'caixa.obj'))
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'casa.obj'))
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'mesa_escritorio.obj'))
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'mesa.obj'))
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'cama.obj'))
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'machado.obj'))
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'papel.obj'))
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'tronco.obj'))
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'fantasma.obj'))
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'fake.obj'))
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'olhos.obj'))
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'haunter.obj'))
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'muro.obj'))
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'lapide.obj'))
    obj_manager.load_obj(path_join(OBJECTS_PATH, 'portal.obj'))

    # texturas
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'terra.png'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'tijolos.jpg'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'casa.png'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'mesa_escritorio.jpg'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'mesa.png'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'cama.png'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'machado.jpg'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'papel.png'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'tronco.jpg'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'fantasma.png'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'fake_1.png'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'fake_2.png'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'olhos.png'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'haunter.png'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'muro.jpg'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'lapide.jpeg'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'portal.png'))
    obj_manager.load_texture(path_join(TEXTURES_PATH, 'lantern.jpg'))

    # vec3 aPosition
    # vec2 aTexture_coord
    # vec3 aNormal
    attributes, num_vertices = obj_manager.get_attribute_arrays()

    vertices = np.zeros((num_vertices, 3*2*3), dtype=np.float32)
    vertices[:, 0:3] = np.reshape(attributes['positions'], (-1, 3))
    vertices[:, 3:5] = np.reshape(attributes['texture_coords'], (-1, 2))
    vertices[:, 5:8] = np.reshape(attributes['normals'], (-1, 3))
    
    vertices = vertices.flatten()

    # carregando na GPU
    objectsVAO = glGenVertexArrays(1)
    objectsVBO = glGenBuffers(1)

    glBindVertexArray(objectsVAO)
    glBindBuffer(GL_ARRAY_BUFFER, objectsVBO)

    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    loc_pos = glGetAttribLocation(DEFAULT_SHADER.getProgram(), "aPosition")
    glEnableVertexAttribArray(loc_pos)
    glVertexAttribPointer(loc_pos, 3, GL_FLOAT, False, 3*2*3 * glm.sizeof(glm.float32), ctypes.c_void_p(0))

    loc_texture = glGetAttribLocation(DEFAULT_SHADER.getProgram(), "aTexture_coord")
    glEnableVertexAttribArray(loc_texture)
    glVertexAttribPointer(loc_texture, 2, GL_FLOAT, False, 3*2*3 * glm.sizeof(glm.float32), ctypes.c_void_p(3 * glm.sizeof(glm.float32)))

    loc_normal = glGetAttribLocation(DEFAULT_SHADER.getProgram(), "aNormal")
    glEnableVertexAttribArray(loc_normal)
    glVertexAttribPointer(loc_normal, 3, GL_FLOAT, False, 3*2*3 * glm.sizeof(glm.float32), ctypes.c_void_p((3+2) * glm.sizeof(glm.float32)))

    # variáveis para a movimentação da câmera
    CAMERA_HEIGHT = -0.4
    cameraPos   = glm.vec3(0.0, CAMERA_HEIGHT, 0.0)
    cameraFront = glm.vec3(0.0, 0.0, -1.0)
    cameraUp    = glm.vec3(0.0, 1.0, 0.0)
    cameraVel   = glm.vec3(0.0, 0.0, 0.0)
    CAMERA_SPEED_WALKING = 5
    CAMERA_SPEED_RUNNING = 10
    deltaTime   = 0.0
    lastFrame   = 0.0
    X_LIMIT = (-35, 35)
    Y_LIMIT = (-1.5, 10)
    Z_LIMIT = (-40, 10)


    # variáveis auxiliares
    papelPos = glm.vec3(-2.02, -0.723, -31.965)
    papelEscala = 1
    pegandoPapel = False
    papelVisivel = True
    ka_offset=0; kd_offset=0; ks_offset=0;
    lights_on = dict(
        olhos=True,
        portal=True,
        lantern=True,
        fantasma=True
    )
    haunter_t = 0.0
    mostrar_corpo = False

    # função auxiliar
    def loadLightSourceAttributes(position, color, constant, linear, quadratic, index):
        DEFAULT_SHADER.use()

        DEFAULT_SHADER.setVec3(f'pointLights[{index}].position', *position)
        DEFAULT_SHADER.setVec3(f'pointLights[{index}].color', *color)
        DEFAULT_SHADER.setFloat(f'pointLights[{index}].decay.constant', constant)
        DEFAULT_SHADER.setFloat(f'pointLights[{index}].decay.linear', linear)
        DEFAULT_SHADER.setFloat(f'pointLights[{index}].decay.quadratic', quadratic)
        
        LIGHT_SOURCE_SHADER.use()

    # variáveis para os callbacks
    show_lines = False
    flying_state = False

    firstMouse = True
    yaw   = -90.0
    pitch =  0.0
    lastX =  LARGURA_JANELA / 2.0
    lastY =  ALTURA_JANELA / 2.0
    
    fov   =  45.0

    # adicionando callbacks
    glfw.set_key_callback(window, key_event)
    glfw.set_cursor_pos_callback(window, mouse_event)
    glfw.set_scroll_callback(window, scroll_event)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    # captura de mouse
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # exibindo janela
    glfw.show_window(window)

    # 3D
    glEnable(GL_DEPTH_TEST)

    ### LOOP PRINCIPAL DA JANELA

    while not glfw.window_should_close(window):
        # setup
        currentFrame = glfw.get_time()
        deltaTime = currentFrame - lastFrame
        lastFrame = currentFrame

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        glfw.poll_events()
        camera_movement_handler()

        ## SKYBOX
        SKYBOX_SHADER.use()

        glDepthFunc(GL_LEQUAL)

        glBindVertexArray(skyboxVAO)
        glBindBuffer(GL_ARRAY_BUFFER, skyboxVBO)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, skyboxTexture)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        glDepthFunc(GL_LESS)

        ### TRANSFORMAÇÕES

        ## MODEL
        DEFAULT_SHADER.use()
        glBindVertexArray(objectsVAO)
        glBindBuffer(GL_ARRAY_BUFFER, objectsVBO)

        slice_vertices_chao = obj_manager.get_vertices_slice(obj_index=0)
        model_objeto(DEFAULT_SHADER.getProgram(), t_z=-15, t_y=-1.6, s_x=35, s_z=25)
        desenha_objeto(
            *slice_vertices_chao,
            shader=DEFAULT_SHADER,
            texture_id=2,
            ka=0.1+ka_offset,
            kd=0.7+kd_offset,
            ks=0+ks_offset,
            ns=1
        )

        # slice_vertices_caixa2 = obj_manager.get_vertices_slice(obj_index=1)
        # model_objeto(DEFAULT_SHADER.getProgram(), t_x=1, t_z=-10)
        # desenha_objeto(*slice_vertices_caixa2, DEFAULT_SHADER, texture_id=3)

        slice_vertices_casa = obj_manager.get_vertices_slice(obj_index=2)
        model_objeto(DEFAULT_SHADER.getProgram(), t_x=1, t_y=-2, t_z=-30, r_y=-90, s_x=2, s_y=2, s_z=2)
        desenha_objeto(
            *slice_vertices_casa,
            DEFAULT_SHADER,
            texture_id=4,
            ka=0.1+ka_offset,
            kd=0.8+kd_offset,
            ks=0.2+ks_offset,
            ns=1
        )

        slice_vertices_mesa_escritorio = obj_manager.get_vertices_slice(obj_index=3)
        model_objeto(DEFAULT_SHADER.getProgram(), t_x=-1.9, t_y=-1.5, t_z=-32, r_x=90, r_y=180, r_z=-90, s_x=0.01, s_y=0.01, s_z=0.01)
        desenha_objeto(
            *slice_vertices_mesa_escritorio,
            DEFAULT_SHADER,
            texture_id=5,
            ka=0.05+ka_offset,
            kd=0.9+kd_offset,
            ks=0.8+ks_offset,
            ns=100
        )

        slice_vertices_mesa = obj_manager.get_vertices_slice(obj_index=4)
        model_objeto(DEFAULT_SHADER.getProgram(), t_y=-1.55, t_z=-28.58, r_y=45, s_x=0.55, s_y=0.55, s_z=0.55)
        desenha_objeto(
            *slice_vertices_mesa,
            DEFAULT_SHADER,
            texture_id=6,
            ka=0.05+ka_offset,
            kd=0.9+kd_offset,
            ks=0.1+ks_offset,
            ns=2
        )

        slice_vertices_cama = obj_manager.get_vertices_slice(obj_index=5)
        model_objeto(DEFAULT_SHADER.getProgram(), t_x=3.6, t_y=-1.56, t_z=-31.9, r_y=-90, s_x=0.007, s_y=0.007, s_z=0.007)
        desenha_objeto(
            *slice_vertices_cama,
            DEFAULT_SHADER,
            texture_id=7,
            ka=0.05+ka_offset,
            kd=0.7+kd_offset,
            ks=0.3+ks_offset,
            ns=5
        )
        
        slice_vertices_machado = obj_manager.get_vertices_slice(obj_index=6)
        model_objeto(DEFAULT_SHADER.getProgram(), t_y=-0.764, t_z=-28.75)
        desenha_objeto(
            *slice_vertices_machado,
            DEFAULT_SHADER, 
            texture_id=8,
            ka=0.05+ka_offset,
            kd=0.9+kd_offset,
            ks=0.5+ks_offset,
            ns=10
        )
        
        if pegandoPapel:
            if not papelVisivel:
                papelEscala *= (1 - (8 * deltaTime))  # 1/8 de segundo de animação
                if papelEscala < 0.01:
                    papelEscala = 0
                    pegandoPapel = False
            else:
                if papelEscala == 0:
                    papelEscala = 0.0001
                papelEscala /= (1 - (8 * deltaTime))  # 1/8 de segundo de animação
                if papelEscala > 1:
                    papelEscala = 1
                    pegandoPapel = False
        slice_vertices_papel = obj_manager.get_vertices_slice(obj_index=7)
        model_objeto(DEFAULT_SHADER.getProgram(), 
            t_x=papelPos.x, t_y=papelPos.y, t_z=papelPos.z, 
            s_x=papelEscala, s_y=papelEscala, s_z=papelEscala, 
            r_y=85)
        desenha_objeto(
            *slice_vertices_papel,
            DEFAULT_SHADER,
            texture_id=9,
            ka=0.05+ka_offset,
            kd=0.9+kd_offset,
            ks=0+ks_offset,
            ns=1
        )
        
        troncos_reflection_coeffs = dict(
            ka=0.1+ka_offset,
            kd=0.8+kd_offset,
            ks=0+ks_offset,
            ns=1
        )
        slice_vertices_tronco = obj_manager.get_vertices_slice(obj_index=8)
        model_objeto(DEFAULT_SHADER.getProgram(), t_x=-5, t_y=-2.3)
        desenha_objeto(*slice_vertices_tronco, DEFAULT_SHADER, texture_id=10, **troncos_reflection_coeffs)
        
        model_objeto(DEFAULT_SHADER.getProgram(), t_x=-25, t_y=-2.3, t_z=-20)
        desenha_objeto(*slice_vertices_tronco, DEFAULT_SHADER, texture_id=10, **troncos_reflection_coeffs)
        
        model_objeto(DEFAULT_SHADER.getProgram(), t_x=25, t_y=-2.3, t_z=-15)
        desenha_objeto(*slice_vertices_tronco, DEFAULT_SHADER, texture_id=10, **troncos_reflection_coeffs)
        
        model_objeto(DEFAULT_SHADER.getProgram(), t_x=15, t_y=-2.3, t_z=-35)
        desenha_objeto(*slice_vertices_tronco, DEFAULT_SHADER, texture_id=10, **troncos_reflection_coeffs)

        n_fake_arvores = 7
        raio = 50
        fake_cx, fake_cz = 0, -15  # centro do círculo
        slice_vertices_fake = obj_manager.get_vertices_slice(obj_index=10)
        for i in range(n_fake_arvores):
            angulo = 2 * math.pi * i / n_fake_arvores  # divide a circunferência em partes iguais

            fake_tx = fake_cx + raio * math.cos(angulo)  # coordenada X
            fake_tz = fake_cz + raio * math.sin(angulo)  # coordenada Z
            
            dx = cameraPos.x - fake_tx
            dz = cameraPos.z - fake_tz

            # ângulo para olhar para o centro (em radianos)
            rot_y = math.degrees(math.atan2(dx, dz))

            model_objeto(DEFAULT_SHADER.getProgram(), t_x=fake_tx, t_y=-2, t_z=fake_tz, r_y=rot_y, s_x=8, s_y=8, s_z=8)
            desenha_objeto(
                *slice_vertices_fake,
                DEFAULT_SHADER,
                texture_id=12+(i%2),
                ka=0.1+ka_offset,
                kd=0.8+kd_offset,
                ks=0+ks_offset,
                ns=1
            )

        escala = 15.0

        haunter_x = escala * math.cos(haunter_t)
        haunter_z = escala * math.sin(haunter_t * 0.7 + math.cos(haunter_t * 0.5))

        haunter_dx = cameraPos.x - haunter_x
        haunter_dz = cameraPos.z - haunter_z
        haunter_rot_y = math.degrees(math.atan2(haunter_dx, haunter_dz))

        if mostrar_corpo:
            slice_vertices_haunter = obj_manager.get_vertices_slice(obj_index=12)
            model_objeto(DEFAULT_SHADER.getProgram(),t_x=haunter_x, t_z=haunter_z-10, r_y=haunter_rot_y)
            desenha_objeto(
                *slice_vertices_haunter,
                DEFAULT_SHADER,
                texture_id=15,
                ka=0.1+ka_offset,
                kd=0.8+kd_offset,
                ks=0.6+ks_offset,
                ns=10
            )

        tamanho_muro = 4
        slice_vertices_muro = obj_manager.get_vertices_slice(obj_index=13)
        muros_reflection_coeffs = dict(
            ka=0.1+ka_offset,
            kd=0.8+kd_offset,
            ks=0.3+ks_offset,
            ns=5
        )
        for j_index, j in enumerate(Z_LIMIT):
            for i in range(X_LIMIT[0], X_LIMIT[1], tamanho_muro):
                model_objeto(DEFAULT_SHADER.getProgram(),t_x=i, t_y=0.4, t_z=j, r_y=(180 if j_index == 1 else 0))
                desenha_objeto(
                    *slice_vertices_muro,
                    DEFAULT_SHADER,
                    texture_id=16,
                    **muros_reflection_coeffs
                )
        
        for j_index, j in enumerate(X_LIMIT):
            for i in range(Z_LIMIT[0], Z_LIMIT[1]+ tamanho_muro, tamanho_muro):
                model_objeto(DEFAULT_SHADER.getProgram(),t_x=j, t_y=0.4, t_z=i, r_y=(270 if j_index == 1 else 90))
                desenha_objeto(
                    *slice_vertices_muro,
                    DEFAULT_SHADER,
                    texture_id=16,
                    **muros_reflection_coeffs
                )

        slice_vertices_lapide = obj_manager.get_vertices_slice(obj_index=14)
        model_objeto(DEFAULT_SHADER.getProgram(),t_x=5, t_y=-1.6,t_z=-32.4,r_y=90, s_x=0.01, s_y=0.01, s_z=0.01)
        desenha_objeto(
            *slice_vertices_lapide,
            DEFAULT_SHADER,
            texture_id=17,
            ka=0.1+ka_offset,
            kd=0.8+kd_offset,
            ks=0.2+ks_offset,
            ns=3
        )

        # light sources
        LIGHT_SOURCE_SHADER.use()
        glBindVertexArray(light_sourcesVAO)
        glBindBuffer(GL_ARRAY_BUFFER, light_sourcesVBO)

        olhos = {
            'position': [haunter_x, 0, haunter_z-10],
            'color': [1,1,1] if lights_on['olhos'] else 3*[0],
            'constant': 0.8,
            'linear': 0.06,
            'quadratic': 0.04
        }
        olhos_model_args = dict(
            t_x=olhos['position'][0],
            t_y=olhos['position'][1],
            t_z=olhos['position'][2],
            r_y=haunter_rot_y
        )
        slice_vertices_olhos = light_source_manager.get_vertices_slice(obj_index=0)
        model_objeto(LIGHT_SOURCE_SHADER.getProgram(), **olhos_model_args)
        desenha_objeto(
            *slice_vertices_olhos,
            LIGHT_SOURCE_SHADER,
            texture_id=14,
            light_source=True,
            brightness = 1.0 if lights_on['olhos'] else 0.7
        )
        loadLightSourceAttributes(**olhos, index=0)
        
        
        portal = {
            'position': [2, 10, 0],
            'color': [0,1,0] if lights_on['portal'] else 3*[0],
            'constant': 1,
            'linear': 0.08,
            'quadratic': 0
        }
        portal_model_args = dict(
            t_x=portal['position'][0],
            t_y=portal['position'][1],
            t_z=portal['position'][2],
            r_x=90,
            s_x=15, s_y=15, s_z=15
        )
        slice_vertices_portal = light_source_manager.get_vertices_slice(obj_index=1)
        model_objeto(LIGHT_SOURCE_SHADER.getProgram(), **portal_model_args)
        desenha_objeto(
            *slice_vertices_portal,
            LIGHT_SOURCE_SHADER,
            texture_id=18,
            light_source=True,
            brightness = 1.0 if lights_on['portal'] else 0.7
        )
        loadLightSourceAttributes(**portal, index=1)
        
        
        lantern = {
            'position': [-2.02, -0.643, -31.265],
            'color': [247/255, 125/255, 25/255] if lights_on['lantern'] else 3*[0],
            'constant': 1.0,
            'linear': 0.06,
            'quadratic': 0.02
        }
        lantern_model_args = dict(
            t_x=lantern['position'][0],
            t_y=lantern['position'][1]-0.1,
            t_z=lantern['position'][2],
            s_x=0.003, s_y=0.003, s_z=0.003
        )
        slice_vertices_lantern = light_source_manager.get_vertices_slice(obj_index=2)
        model_objeto(LIGHT_SOURCE_SHADER.getProgram(), **lantern_model_args)
        desenha_objeto(
            *slice_vertices_lantern,
            LIGHT_SOURCE_SHADER,
            texture_id=19,
            light_source=True,
            brightness = 1.0 if lights_on['lantern'] else 0.7
        )
        loadLightSourceAttributes(**lantern, index=2)

        fantasma_tz = -28.6
        fantasma_dz = cameraPos.z - fantasma_tz
        fantasma_rot_y = math.degrees(math.atan2(cameraPos.x, fantasma_dz))
        fantasma = {
            'position': [0, -1.29, fantasma_tz],
            'color': [0.9, 0.9, 0.9] if lights_on['fantasma'] else 3*[0],
            'constant': 1.0,
            'linear': 0.06,
            'quadratic': 0.02,
        }
        fantasma_model_args = dict(
            t_x=fantasma['position'][0],
            t_y=fantasma['position'][1],
            t_z=fantasma['position'][2],
            r_y=fantasma_rot_y,
            s_x=0.5, s_y=0.5, s_z=0.5
        )
        slice_vertices_fantasma = light_source_manager.get_vertices_slice(obj_index=3)
        model_objeto(LIGHT_SOURCE_SHADER.getProgram(), **fantasma_model_args)
        desenha_objeto(
            *slice_vertices_fantasma,
            LIGHT_SOURCE_SHADER,
            texture_id=11,
            alpha=0.7,
            light_source=True,
            brightness = 1.0 if lights_on['fantasma'] else 0.8
        )
        loadLightSourceAttributes(**fantasma, index=3)

        ## VIEW
        cameraPos += cameraVel * deltaTime
        cameraVel = glm.vec3(0.0, 0.0, 0.0)

        # verificando limites da cena
        if cameraPos.x < X_LIMIT[0] + 0.5:
            cameraPos.x = X_LIMIT[0] + 0.5
        elif cameraPos.x > X_LIMIT[1] - 0.5:
            cameraPos.x = X_LIMIT[1] - 0.5
        
        if cameraPos.y < Y_LIMIT[0]:
            cameraPos.y = Y_LIMIT[0]
        elif cameraPos.y > Y_LIMIT[1]:
            cameraPos.y = Y_LIMIT[1]
        
        if cameraPos.z < Z_LIMIT[0] + 0.5:
            cameraPos.z = Z_LIMIT[0] + 0.5
        elif cameraPos.z > Z_LIMIT[1] - 0.5:
            cameraPos.z = Z_LIMIT[1] - 0.5

        mat_view = view(cameraPos, cameraFront, cameraUp)

        # default
        DEFAULT_SHADER.use()
        loc_view = glGetUniformLocation(DEFAULT_SHADER.getProgram(), "view")
        glUniformMatrix4fv(loc_view, 1, GL_TRUE, np.array(mat_view))

        DEFAULT_SHADER.setVec3('view_pos', cameraPos[0], cameraPos[1], cameraPos[2])

        # light sources
        LIGHT_SOURCE_SHADER.use()
        loc_projection = glGetUniformLocation(LIGHT_SOURCE_SHADER.getProgram(), "view")
        glUniformMatrix4fv(loc_projection, 1, GL_TRUE, np.array(mat_view))

        # skybox
        SKYBOX_SHADER.use()
        loc_projection = glGetUniformLocation(SKYBOX_SHADER.getProgram(), "view")
        glUniformMatrix4fv(loc_projection, 1, GL_TRUE, np.array(glm.mat4(glm.mat3(mat_view))))


        ## PROJECTION
        mat_projection = projection(fov, LARGURA_JANELA, ALTURA_JANELA)

        # default
        DEFAULT_SHADER.use()
        loc_projection = glGetUniformLocation(DEFAULT_SHADER.getProgram(), "projection")
        glUniformMatrix4fv(loc_projection, 1, GL_TRUE, np.array(mat_projection))

        # light sources
        LIGHT_SOURCE_SHADER.use()
        loc_projection = glGetUniformLocation(LIGHT_SOURCE_SHADER.getProgram(), "projection")
        glUniformMatrix4fv(loc_projection, 1, GL_TRUE, np.array(mat_projection))

        # skybox
        SKYBOX_SHADER.use()
        loc_projection = glGetUniformLocation(SKYBOX_SHADER.getProgram(), "projection")
        glUniformMatrix4fv(loc_projection, 1, GL_TRUE, np.array(mat_projection))

        glfw.swap_buffers(window)

    glfw.terminate()