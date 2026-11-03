import numpy as np
from OpenGL.GL import *
from matrizes import matriz_translacao, matriz_rotacao_y

R0 = 3.0
AMPLITUDE = 1.0
NUM_PONTOS = 120

modo_sombra = False

def cor(r, g, b):
    if not modo_sombra:
        glColor3f(r, g, b)

from iluminacao import POSICAO_SOL
from matrizes import matriz_sombra_plana

def desenhar_sombras():
    global modo_sombra
    m = matriz_sombra_plana(POSICAO_SOL)

    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE)          # a projeção achata e pode inverter faces
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    glEnable(GL_POLYGON_OFFSET_FILL) # evita z-fighting com a relva (mesmo y=0)
    glPolygonOffset(-2.0, -2.0)

    # Stencil: só desenha onde há relva (valor 1) e zera depois de desenhar,
    # assim cada pixel recebe a sombra UMA vez (sem escurecer em dobro).
    glEnable(GL_STENCIL_TEST)
    glStencilFunc(GL_EQUAL, 1, 0xFF)
    glStencilOp(GL_KEEP, GL_KEEP, GL_ZERO)

    glColor4f(0.0, 0.0, 0.0, 0.45)

    glPushMatrix()
    glMultMatrixf(m.T)
    modo_sombra = True
    desenhar_borda_tijolos()
    desenhar_poste(1.5, 0.0, 0.0)
    desenhar_placa(-1.8, 0.0, 2.8)
    modo_sombra = False
    glPopMatrix()

    glDisable(GL_STENCIL_TEST)
    glDisable(GL_POLYGON_OFFSET_FILL)
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)

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

def desenhar_cilindro(raio, altura, fatias=24):
    """Desenha um cilindro 3D vertical (haste/suporte)."""
    thetas = np.linspace(0, 2 * np.pi, fatias, endpoint=True)
    glBegin(GL_QUADS)
    for i in range(len(thetas) - 1):
        t1 = thetas[i]
        t2 = thetas[i+1]
        
        x1, z1 = raio * np.cos(t1), raio * np.sin(t1)
        x2, z2 = raio * np.cos(t2), raio * np.sin(t2)
        
        glNormal3f(np.cos(t1), 0.0, np.sin(t1))
        glVertex3f(x1, 0.0, z1)
        glVertex3f(x1, altura, z1)
        
        glNormal3f(np.cos(t2), 0.0, np.sin(t2))
        glVertex3f(x2, altura, z2)
        glVertex3f(x2, 0.0, z2)
    glEnd()
    
    # Tampa superior do cilindro
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, altura, 0.0)
    for t in thetas:
        glVertex3f(raio * np.cos(t), altura, raio * np.sin(t))
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
    
    m_trans = matriz_translacao(x, y, z)
    glMultMatrixf(m_trans.T)
    
    # 1. Haste metálica do poste (Cinzento-escuro)
    glColor3f(0.25, 0.25, 0.28)
    desenhar_cilindro(raio_haste, altura)
    
    # 2. Globo de iluminação no topo (Amarelo claro / Luz brilhante)
    glPushMatrix()
    m_trans_globo = matriz_translacao(0.0, altura + raio_globo, 0.0)
    glMultMatrixf(m_trans_globo.T)
    
    cor(1.0, 0.95, 0.6)
    desenhar_esfera(raio_globo)
    glPopMatrix()
    
    glPopMatrix()

def desenhar_placa(x, y, z, altura_suporte=0.8, raio_suporte=0.28, largura_painel=1.0, profundidade_painel=0.6, espessura_painel=0.05):
    """
    Desenha a estrutura composta por um suporte cilíndrico mais largo
    e um painel retangular horizontal (deitado, virado para cima) no topo.
    """
    glPushMatrix()
    
    # Translação manual para a posição da base
    m_trans = matriz_translacao(x, y, z)
    glMultMatrixf(m_trans.T)
    
    # 1. Suporte Cilíndrico Mais Largo
    glColor3f(0.3, 0.3, 0.32)
    desenhar_cilindro(raio_suporte, altura_suporte)
    
    # 2. Painel Retangular Deitado (Face Superior Virada para Cima)
    glPushMatrix()
    m_trans_painel = matriz_translacao(0.0, altura_suporte + (espessura_painel / 2.0), 0.0)
    glMultMatrixf(m_trans_painel.T)

    # Rotação no eixo Y (convertendo o ângulo em graus para radianos)
    m_rot_painel = matriz_rotacao_y(np.radians(150))
    glMultMatrixf(m_rot_painel.T)
    
    w = largura_painel / 2.0
    h = espessura_painel / 2.0
    d = profundidade_painel / 2.0
    
    cor(0.9, 0.9, 0.88)
    
    glBegin(GL_QUADS)
    # Face Superior (Virada para cima em +Y)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-w,  h, -d); glVertex3f(-w,  h,  d); glVertex3f( w,  h,  d); glVertex3f( w,  h, -d)
    
    # Face Inferior (-Y)
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(-w, -h, -d); glVertex3f( w, -h, -d); glVertex3f( w, -h,  d); glVertex3f(-w, -h,  d)
    
    # Face Frontal (+Z)
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(-w, -h,  d); glVertex3f( w, -h,  d); glVertex3f( w,  h,  d); glVertex3f(-w,  h,  d)
    
    # Face Traseira (-Z)
    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(-w, -h, -d); glVertex3f(-w,  h, -d); glVertex3f( w,  h, -d); glVertex3f( w, -h, -d)
    
    # Face Lateral Esquerda (-X)
    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(-w, -h, -d); glVertex3f(-w, -h,  d); glVertex3f(-w,  h,  d); glVertex3f(-w,  h, -d)
    
    # Face Lateral Direita (+X)
    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f( w, -h, -d); glVertex3f( w,  h, -d); glVertex3f( w,  h,  d); glVertex3f( w, -h,  d)
    glEnd()
    
    glPopMatrix()
    
    glPopMatrix()

def desenhar_sombras(luz_mundo):
    global modo_sombra
    m = matriz_sombra_plana(luz_mundo)                # <-- novo

    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE)
    glDisable(GL_DEPTH_TEST)                  # <-- novo (desliga o depth)
    glDisable(GL_BLEND)                       # <-- novo
    # glEnable(GL_STENCIL_TEST)               # <-- comentado
    # glStencilFunc(GL_EQUAL, 1, 0xFF)        # <-- comentado
    # glStencilOp(GL_KEEP, GL_KEEP, GL_ZERO)  # <-- comentado

    glColor4f(1.0, 0.0, 0.0, 1.0)             # <-- vermelho opaco

    glPushMatrix()
    glMultMatrixf(m.T)
    modo_sombra = True
    desenhar_borda_tijolos()
    desenhar_poste(1.5, 0.0, 0.0)
    desenhar_placa(-1.8, 0.0, 2.8)
    modo_sombra = False
    glPopMatrix()

    glEnable(GL_DEPTH_TEST)                   # <-- restaura
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)