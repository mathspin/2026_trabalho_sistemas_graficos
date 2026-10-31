from OpenGL.GL import *

def inicializar_iluminacao():
    """Configura Z-Buffer, Culling, Fonte de Luz Phong e Tonalização Gouraud."""
    glClearColor(0.5, 0.7, 0.9, 1.0)
    
    # Algoritmo de Visibilidade (10%) (cite: 1)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    
    # Iluminação Phong & Tonalização Gouraud (15%) (cite: 1)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    posicao_luz = [5.0, 12.0, 5.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz)
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    
    glShadeModel(GL_SMOOTH)