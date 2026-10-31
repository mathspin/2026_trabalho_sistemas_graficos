import numpy as np
from OpenGL.GL import *
from matrizes import matriz_translacao, matriz_rotacao_y

R0 = 3.0
AMPLITUDE = 1.0
NUM_PONTOS = 120

def raio_canteiro(theta):
    """Equação da curva paramétrica trilobada r(theta) = R0 + A * cos(3*theta)."""
    return R0 + AMPLITUDE * np.cos(3 * theta)

def desenhar_eixos():
    """Desenha os eixos cartesianos X (Vermelho), Y (Verde) e Z (Azul)."""
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
    """Desenha a malha preenchida de grama com GL_TRIANGLE_FAN."""
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
    """Desenha um bloco de tijolo transformado via glMultMatrixf."""
    glPushMatrix()
    
    m_trans = matriz_translacao(x, altura / 2.0, z)
    m_rot = matriz_rotacao_y(angulo_rotacao)
    
    glMultMatrixf(m_trans.T)
    glMultMatrixf(m_rot.T)
    
    w, h, d = largura / 2.0, altura / 2.0, profundidade / 2.0
    glColor3f(0.85, 0.85, 0.80)
    
    glBegin(GL_QUADS)
    # Topo
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-w,  h, -d); glVertex3f(-w,  h,  d); glVertex3f( w,  h,  d); glVertex3f( w,  h, -d)
    # Frente
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(-w, -h,  d); glVertex3f( w, -h,  d); glVertex3f( w,  h,  d); glVertex3f(-w,  h,  d)
    # Trás
    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(-w, -h, -d); glVertex3f(-w,  h, -d); glVertex3f( w,  h, -d); glVertex3f( w, -h, -d)
    # Esquerda
    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(-w, -h, -d); glVertex3f(-w, -h,  d); glVertex3f(-w,  h,  d); glVertex3f(-w,  h, -d)
    # Direita
    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f( w, -h, -d); glVertex3f( w,  h, -d); glVertex3f( w,  h,  d); glVertex3f( w, -h,  d)
    glEnd()
    
    glPopMatrix()

def desenhar_borda_tijolos():
    """Gera a borda de tijolos acompanhando a curvatura do canteiro."""
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