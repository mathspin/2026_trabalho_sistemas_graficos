import sys
import numpy as np
import glfw
from OpenGL.GL import *

from matrizes import matriz_translacao, matriz_perspectiva, matriz_ortogonal
from iluminacao import inicializar_iluminacao
from rasterizacao import bresenham_linha_3d
from geometria import (
    desenhar_eixos, desenhar_relva, desenhar_borda_tijolos, 
    desenhar_poste, desenhar_placa, raio_canteiro
)

LARGURA = 1024
ALTURA = 768
TITULO = "CG - Canteiro C3 / FURG"

usar_perspectiva = True
mostrar_rasterizacao = True

# Rotação e Zoom
rotacao_x = 30.0
rotacao_y = 0.0
distancia_cam = 13.0

# Translação da Câmera (WASD)
trans_x = 0.0
trans_y = 0.0

PASSO_ROTACAO = 5.0
PASSO_ZOOM = 0.5
PASSO_TRANS = 0.2  # Velocidade da translação WASD

def redimensionar_janela(window, width, height):
    global LARGURA, ALTURA
    if height == 0:
        height = 1
    LARGURA, ALTURA = width, height
    glViewport(0, 0, width, height)

def tratar_teclado(window, key, scancode, action, mods):
    global usar_perspectiva, mostrar_rasterizacao, rotacao_x, rotacao_y, distancia_cam, trans_x, trans_y
    
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
        elif key in (glfw.KEY_KP_ADD, glfw.KEY_EQUAL):
            distancia_cam = max(3.0, distancia_cam - PASSO_ZOOM)
        elif key in (glfw.KEY_KP_SUBTRACT, glfw.KEY_MINUS):
            distancia_cam = min(30.0, distancia_cam + PASSO_ZOOM)

        # Translação com W, A, S, D
        elif key == glfw.KEY_W:
            trans_y -= PASSO_TRANS  # Move visão para cima
        elif key == glfw.KEY_S:
            trans_y += PASSO_TRANS  # Move visão para baixo
        elif key == glfw.KEY_A:
            trans_x += PASSO_TRANS  # Move visão para a esquerda
        elif key == glfw.KEY_D:
            trans_x -= PASSO_TRANS  # Move visão para a direita

def aplicar_projecao():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    aspecto = LARGURA / ALTURA
    if usar_perspectiva:
        m_proj = matriz_perspectiva(45.0, aspecto, 0.1, 100.0)
    else:
        escala_orto = distancia_cam / 2.0
        m_proj = matriz_ortogonal(-escala_orto * aspecto, escala_orto * aspecto, -escala_orto, escala_orto, 0.1, 100.0)
    
    glMultMatrixf(m_proj.T)

def renderizar():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    aplicar_projecao()
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Aplica a translação combinada (WASD + Zoom no eixo Z) usando a matriz manual
    m_cam_trans = matriz_translacao(trans_x, -1.0 + trans_y, -distancia_cam)
    glMultMatrixf(m_cam_trans.T)
    
    # Aplica as rotações interativas das setinhas
    glRotatef(rotacao_x, 1.0, 0.0, 0.0)
    glRotatef(rotacao_y, 0.0, 1.0, 0.0)
    
    desenhar_eixos()
    desenhar_relva()
    desenhar_borda_tijolos()
    
    # Objetos 3D adicionais
    desenhar_poste(1.5, 0.0, 0.0)
    desenhar_placa(-1.8, 0.0, 2.8)
    
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
    
    inicializar_iluminacao()

    print("--- Controles do Teclado ---")
    print("Setas (Esquerda / Direita): Gira a cena horizontalmente")
    print("Setas (Cima / Baixo): Inclina a cena verticalmente")
    print("W / A / S / D: Translada o ponto de vista (Cima / Esquerda / Baixo / Direita)")
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