from OpenGL.GL import *

def bresenham_linha_3d(x0, z0, x1, z1, y=0.01):
    """
    Algoritmo de Rasterização de Bresenham (15% da Nota) (cite: 1).
    Discretiza uma linha em pontos no plano XZ e renderiza com GL_POINTS.
    """
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