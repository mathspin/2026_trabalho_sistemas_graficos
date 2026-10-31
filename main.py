import sys
import numpy as np
import glfw
from OpenGL.GL import *
from matrizes import (
    matriz_translacao, matriz_rotacao_y, matriz_escala,
    matriz_perspectiva, matriz_ortogonal
)

LARGURA = 1024
ALTURA = 768
TITULO = "CG - Canteiro C3 / FURG"

R0 = 3.0
AMPLITUDE = 1.0
NUM_PONTOS = 120

usar_perspectiva = True
mostrar_rasterizacao = True

# Variáveis globais para controle de rotação e zoom
rotacao_x = 30.0       # Inclinação inicial
rotacao_y = 0.0        # Rotação em volta do centro
distancia_cam = 13.0   # Zoom da câmera (distância inicial no eixo Z)

PASSO_ROTACAO = 5.0
PASSO_ZOOM = 0.5       # Quantidade de zoom a cada clique

def raio_canteiro(theta):
    return R0 + AMPLITUDE * np.cos(3 * theta)

def bresenham_linha_3d(x0, z0, x1, z1, y=0.01):
    escala = 50
    ix0, iz0 = int(x0 * escala), int(z0 * escala)
    ix1, iz1 = int(x1 * escala), int(z1 * escala)

    dx = abs(ix1 - ix0)
    dz = abs(iz1 - iz0)
    sx = 1 if ix0 < ix1 else -1
    sz = 1 if iz0 < iz1 else -1
    err = dx - dz

    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 0.0)
    glPointSize(3.0)
    glBegin(GL_POINTS)
    
    curr_x, curr_z = ix0, iz0
    while True:
        glVertex3f(curr_x / escala, y, curr_z / escala)
        if curr_x == ix1 and curr_z == iz1:
            break
        e2 = 2 * err
        if e2 > -dz:
            err -= dz
            curr_x += sx
        if e2 < dx:
            err += dx
            curr_z += sz
    glEnd()
    glEnable(GL_LIGHTING)

def inicializar_opengl():
    glClearColor(0.5, 0.7, 0.9, 1.0)
    
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    
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

def redimensionar_janela(window, width, height):
    global LARGURA, ALTURA
    if height == 0:
        height = 1
    LARGURA, ALTURA = width, height
    glViewport(0, 0, width, height)

def tratar_teclado(window, key, scancode, action, mods):
    global usar_perspectiva, mostrar_rasterizacao, rotacao_x, rotacao_y, distancia_cam
    
    if action == glfw.PRESS or action == glfw.REPEAT:
        # Troca de Projeções
        if key == glfw.KEY_P:
            usar_perspectiva = True
            print("Projeção: PERSPECTIVA")
        elif key == glfw.KEY_O:
            usar_perspectiva = False
            print("Projeção: ORTOGONAL")
        # Alterna Rasterização Bresenham
        elif key == glfw.KEY_B:
            mostrar_rasterizacao = not mostrar_rasterizacao
            print(f"Bresenham: {'ATIVADO' if mostrar_rasterizacao else 'DESATIVADO'}")
            
        # Rotação pelas Setinhas
        elif key == glfw.KEY_LEFT:
            rotacao_y -= PASSO_ROTACAO
        elif key == glfw.KEY_RIGHT:
            rotacao_y += PASSO_ROTACAO
        elif key == glfw.KEY_UP:
            rotacao_x = min(90.0, rotacao_x + PASSO_ROTACAO)
        elif key == glfw.KEY_DOWN:
            rotacao_x = max(0.0, rotacao_x - PASSO_ROTACAO)
            
        # Zoom com + e -
        elif key in (glfw.KEY_KP_ADD, glfw.KEY_EQUAL):  # '+' (Teclado numérico ou Shift+=)
            distancia_cam = max(3.0, distancia_cam - PASSO_ZOOM) # Aproxima
        elif key in (glfw.KEY_KP_SUBTRACT, glfw.KEY_MINUS): # '-' (Teclado numérico ou hífen)
            distancia_cam = min(30.0, distancia_cam + PASSO_ZOOM) # Afasta

def desenhar_eixos():
    glDisable(GL_LIGHTING)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    # X
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0); glVertex3f(5.0, 0.0, 0.0)
    # Y
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0); glVertex3f(0.0, 5.0, 0.0)
    # Z
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, 0.0); glVertex3f(0.0, 0.0, 5.0)
    glEnd()
    glEnable(GL_LIGHTING)

def desenhar_relva():
    glColor3f(0.15, 0.60, 0.15)
    thetas = np.linspace(0, 2 * np.pi, NUM_PONTOS)
    
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    for t in reversed(thetas):
        r = raio_canteiro(t)
        x = r * np.cos(t)
        z = r * np.sin(t)
        glVertex3f(x, 0.0, z)
    glEnd()

def desenhar_tijolo(x, z, angulo_rotacao, largura=0.25, altura=0.15, profundidade=0.4):
    glPushMatrix()
    
    m_trans = matriz_translacao(x, altura / 2.0, z)
    m_rot = matriz_rotacao_y(angulo_rotacao)
    
    glMultMatrixf(m_trans.T)
    glMultMatrixf(m_rot.T)
    
    w, h, d = largura / 2.0, altura / 2.0, profundidade / 2.0
    glColor3f(0.85, 0.85, 0.80)
    
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-w,  h, -d); glVertex3f(-w,  h,  d); glVertex3f( w,  h,  d); glVertex3f( w,  h, -d)
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(-w, -h,  d); glVertex3f( w, -h,  d); glVertex3f( w,  h,  d); glVertex3f(-w,  h,  d)
    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(-w, -h, -d); glVertex3f(-w,  h, -d); glVertex3f( w,  h, -d); glVertex3f( w, -h, -d)
    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(-w, -h, -d); glVertex3f(-w, -h,  d); glVertex3f(-w,  h,  d); glVertex3f(-w,  h, -d)
    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f( w, -h, -d); glVertex3f( w,  h, -d); glVertex3f( w,  h,  d); glVertex3f( w, -h,  d)
    glEnd()
    
    glPopMatrix()

def desenhar_borda_tijolos():
    thetas = np.linspace(0, 2 * np.pi, NUM_PONTOS, endpoint=False)
    for t in thetas:
        r = raio_canteiro(t)
        x = r * np.cos(t)
        z = r * np.sin(t)
        
        dt = 0.001
        r_prox = raio_canteiro(t + dt)
        dx = (r_prox * np.cos(t + dt)) - x
        dz = (r_prox * np.sin(t + dt)) - z
        angulo = -np.arctan2(dz, dx)
        
        desenhar_tijolo(x, z, angulo)

def aplicar_projecao():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    aspecto = LARGURA / ALTURA
    if usar_perspectiva:
        m_proj = matriz_perspectiva(45.0, aspecto, 0.1, 100.0)
    else:
        # Na projeção ortogonal, ajustamos o volume de visão proporcionalmente ao zoom
        escala_orto = distancia_cam / 2.0
        m_proj = matriz_ortogonal(-escala_orto * aspecto, escala_orto * aspecto, -escala_orto, escala_orto, 0.1, 100.0)
    
    glMultMatrixf(m_proj.T)

def renderizar():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    aplicar_projecao()
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Recua a câmera usando a distância dinâmica
    m_cam_trans = matriz_translacao(0.0, -1.0, -distancia_cam)
    glMultMatrixf(m_cam_trans.T)
    
    # Aplica as rotações interativas
    glRotatef(rotacao_x, 1.0, 0.0, 0.0)
    glRotatef(rotacao_y, 0.0, 1.0, 0.0)
    
    desenhar_eixos()
    desenhar_relva()
    desenhar_borda_tijolos()
    
    if mostrar_rasterizacao:
        for angulo in np.linspace(0, 2 * np.pi, 6, endpoint=False):
            r = raio_canteiro(angulo)
            x_fim = r * np.cos(angulo)
            z_fim = r * np.sin(angulo)
            bresenham_linha_3d(0.0, 0.0, x_fim, z_fim)

def main():
    if not glfw.init():
        return

    window = glfw.create_window(LARGURA, ALTURA, TITULO, None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, redimensionar_janela)
    glfw.set_key_callback(window, tratar_teclado)
    
    inicializar_opengl()

    print("--- Controles do Teclado ---")
    print("Setas (Esquerda / Direita): Gira a cena horizontalmente")
    print("Setas (Cima / Baixo): Inclina a cena verticalmente")
    print("+ / -: Zoom In / Zoom Out")
    print("P: Projeção Perspectiva | O: Projeção Ortogonal")
    print("B: Alternar Linhas de Bresenham")

    while not glfw.window_should_close(window):
        glfw.poll_events()
        renderizar()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()