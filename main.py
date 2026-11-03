import sys
import numpy as np
import glfw
from OpenGL.GL import *

from matrizes import matriz_translacao, matriz_perspectiva, matriz_ortogonal,matriz_rotacao_x, matriz_rotacao_y
from iluminacao import inicializar_iluminacao, posicionar_sol, POSICAO_SOL
from rasterizacao import bresenham_linha_3d
from geometria import (
    desenhar_eixos, desenhar_relva, desenhar_borda_tijolos,
    desenhar_poste, desenhar_placa, desenhar_sombras, raio_canteiro
)

LARGURA = 1024
ALTURA = 768
TITULO = "CG - Canteiro C3 / FURG"

usar_perspectiva = True
mostrar_rasterizacao = True
mostrar_sombra = True

# Rotação e Zoom
rotacao_x = 30.0
rotacao_y = 0.0
distancia_cam = 13.0

# Translação da Câmera (WASD)
trans_x = 0.0
trans_y = 0.0

PASSO_ROTACAO = 5.0
PASSO_ZOOM = 0.5
PASSO_TRANS = 0.2

def redimensionar_janela(window, width, height):
    global LARGURA, ALTURA
    if height == 0:
        height = 1
    LARGURA, ALTURA = width, height
    glViewport(0, 0, width, height)

def tratar_teclado(window, key, scancode, action, mods):
    global usar_perspectiva, mostrar_rasterizacao, mostrar_sombra
    global rotacao_x, rotacao_y, distancia_cam, trans_x, trans_y

    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_P:
            usar_perspectiva = True
            print("Projeção: PERSPECTIVA")
        elif key == glfw.KEY_O:
            usar_perspectiva = False
            print("Projeção: ORTOGONAL")
        elif key == glfw.KEY_B:
            mostrar_rasterizacao = not mostrar_rasterizacao
            print(f"Bresenham: {'ATIVADO' if mostrar_rasterizacao else 'DESATIVADO'}")
        elif key == glfw.KEY_H:
            mostrar_sombra = not mostrar_sombra
            print(f"Sombra: {'ATIVADA' if mostrar_sombra else 'DESATIVADA'}")
        elif key == glfw.KEY_LEFT:
            rotacao_y -= PASSO_ROTACAO
        elif key == glfw.KEY_RIGHT:
            rotacao_y += PASSO_ROTACAO
        elif key == glfw.KEY_UP:
            rotacao_x = min(90.0, rotacao_x + PASSO_ROTACAO)
        elif key == glfw.KEY_DOWN:
            rotacao_x = max(0.0, rotacao_x - PASSO_ROTACAO)
        elif key in (glfw.KEY_KP_ADD, glfw.KEY_EQUAL):
            distancia_cam = max(3.0, distancia_cam - PASSO_ZOOM)
        elif key in (glfw.KEY_KP_SUBTRACT, glfw.KEY_MINUS):
            distancia_cam = min(30.0, distancia_cam + PASSO_ZOOM)
        elif key == glfw.KEY_W:
            trans_y -= PASSO_TRANS
        elif key == glfw.KEY_S:
            trans_y += PASSO_TRANS
        elif key == glfw.KEY_A:
            trans_x += PASSO_TRANS
        elif key == glfw.KEY_D:
            trans_x -= PASSO_TRANS

def aplicar_projecao():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    aspecto = LARGURA / ALTURA
    if usar_perspectiva:
        m_proj = matriz_perspectiva(45.0, aspecto, 0.1, 100.0)
    else:
        escala_orto = distancia_cam / 2.0
        m_proj = matriz_ortogonal(-escala_orto * aspecto, escala_orto * aspecto,
                                  -escala_orto, escala_orto, 0.1, 100.0)

    glMultMatrixf(m_proj.T)
def direcao_sol_no_mundo():
    """Sol fixo na tela: desfaz as rotações da cena para obter a direção no espaço do mundo."""
    d_olho = np.array([POSICAO_SOL[0], POSICAO_SOL[1], POSICAO_SOL[2], 0.0], dtype=np.float32)
    inv = matriz_rotacao_y(np.radians(-rotacao_y)) @ matriz_rotacao_x(np.radians(-rotacao_x))
    return inv @ d_olho

def renderizar():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

    aplicar_projecao()

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    posicionar_sol()          # luz fixa no espaço da tela

    m_cam_trans = matriz_translacao(trans_x, -1.0 + trans_y, -distancia_cam)
    glMultMatrixf(m_cam_trans.T)
    glRotatef(rotacao_x, 1.0, 0.0, 0.0)
    glRotatef(rotacao_y, 0.0, 1.0, 0.0)

    desenhar_eixos()

    glEnable(GL_STENCIL_TEST)
    glStencilFunc(GL_ALWAYS, 1, 0xFF)
    glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
    desenhar_relva()
    glDisable(GL_STENCIL_TEST)

    if mostrar_sombra:
        luz = direcao_sol_no_mundo()
        if luz[1] > 0.05:
            desenhar_sombras(luz)

    desenhar_borda_tijolos()
    desenhar_poste(1.5, 0.0, 0.0)
    desenhar_placa(-1.8, 0.0, 2.8)

    if mostrar_rasterizacao:
        for angulo in np.linspace(0, 2 * np.pi, 6, endpoint=False):
            r = raio_canteiro(angulo)
            bresenham_linha_3d(0.0, 0.0, r * np.cos(angulo), r * np.sin(angulo))

def main():
    if not glfw.init():
        return

    glfw.window_hint(glfw.STENCIL_BITS, 8)
    window = glfw.create_window(LARGURA, ALTURA, TITULO, None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    print("Stencil bits:", glGetIntegerv(GL_STENCIL_BITS))
    glfw.set_window_size_callback(window, redimensionar_janela)
    glfw.set_key_callback(window, tratar_teclado)

    inicializar_iluminacao()

    print("--- Controles do Teclado ---")
    print("Setas (Esquerda / Direita): Gira a cena horizontalmente")
    print("Setas (Cima / Baixo): Inclina a cena verticalmente")
    print("W / A / S / D: Translada o ponto de vista")
    print("+ / -: Zoom In / Zoom Out")
    print("P: Projeção Perspectiva | O: Projeção Ortogonal")
    print("B: Alternar Linhas de Bresenham")
    print("H: Alternar Sombra do Sol")

    while not glfw.window_should_close(window):
        glfw.poll_events()
        renderizar()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()