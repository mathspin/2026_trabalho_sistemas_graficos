import numpy as np
from OpenGL.GL import *
from matrizes import matriz_translacao, matriz_rotacao_y

R0 = 3.0
AMPLITUDE = 1.0
NUM_PONTOS = 120

def raio_canteiro(theta):
    return R0 + AMPLITUDE * np.cos(3 * theta)

def desenhar_eixos():
    glDisable(GL_LIGHTING)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    # X - Vermelho
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0); glVertex3f(5.0, 0.0, 0.0)
    # Y - Verde
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0); glVertex3f(0.0, 5.0, 0.0)
    # Z - Azul
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

def desenhar_cilindro(raio, altura, fatias=16):
    """Desenha um cilindro 3D vertical (haste do poste)."""
    thetas = np.linspace(0, 2 * np.pi, fatias, endpoint=True)
    glBegin(GL_QUADS)
    for i in range(len(thetas) - 1):
        t1 = thetas[i]
        t2 = thetas[i+1]
        
        x1, z1 = raio * np.cos(t1), raio * np.sin(t1)
        x2, z2 = raio * np.cos(t2), raio * np.sin(t2)
        
        # Normais para sombreamento suave das faces laterais (Gouraud)
        glNormal3f(np.cos(t1), 0.0, np.sin(t1))
        glVertex3f(x1, 0.0, z1)
        glVertex3f(x1, altura, z1)
        
        glNormal3f(np.cos(t2), 0.0, np.sin(t2))
        glVertex3f(x2, altura, z2)
        glVertex3f(x2, 0.0, z2)
    glEnd()

def desenhar_esfera(raio, aneis=12, fatias=12):
    """Desenha uma esfera 3D (globo de luz do poste)."""
    for i in range(aneis):
        lat0 = np.pi * (-0.5 + float(i) / aneis)
        z0  = np.sin(lat0)
        zr0 = np.cos(lat0)

        lat1 = np.pi * (-0.5 + float(i+1) / aneis)
        z1  = np.sin(lat1)
        zr1 = np.cos(lat1)

        glBegin(GL_QUAD_STRIP)
        for j in range(fatias + 1):
            lng = 2 * np.pi * float(j) / fatias
            x = np.cos(lng)
            y = np.sin(lng)

            glNormal3f(x * zr0, y * zr0, z0)
            glVertex3f(raio * x * zr0, raio * y * zr0, raio * z0)
            
            glNormal3f(x * zr1, y * zr1, z1)
            glVertex3f(raio * x * zr1, raio * y * zr1, raio * z1)
        glEnd()

def desenhar_poste(x, y, z, altura=2.2, raio_haste=0.06, raio_globo=0.22):
    """Desenha um poste de luz posicionado em (x, y, z) utilizando glMultMatrixf."""
    glPushMatrix()
    
    # Translação manual do poste
    m_trans = matriz_translacao(x, y, z)
    glMultMatrixf(m_trans.T)
    
    # 1. Haste metálica do poste (Cinzento-escuro)
    glColor3f(0.25, 0.25, 0.28)
    desenhar_cilindro(raio_haste, altura)
    
    # 2. Globo de iluminação no topo (Amarelo claro / Luz brilhante)
    glPushMatrix()
    m_trans_globo = matriz_translacao(0.0, altura + raio_globo, 0.0)
    glMultMatrixf(m_trans_globo.T)
    
    glColor3f(1.0, 0.95, 0.6)
    desenhar_esfera(raio_globo)
    glPopMatrix()
    
    glPopMatrix()