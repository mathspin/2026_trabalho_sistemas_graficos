import numpy as np

def matriz_translacao(tx, ty, tz):
    """Retorna matriz de translação 4x4."""
    return np.array([
        [1.0, 0.0, 0.0, tx],
        [0.0, 1.0, 0.0, ty],
        [0.0, 0.0, 1.0, tz],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float32)

def matriz_rotacao_y(angulo_rad):
    """Retorna matriz de rotação no eixo Y (4x4)."""
    c = np.cos(angulo_rad)
    s = np.sin(angulo_rad)
    return np.array([
        [ c,  0.0,  s,  0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s,  0.0,  c,  0.0],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float32)

def matriz_escala(sx, sy, sz):
    """Retorna matriz de escala 4x4."""
    return np.array([
        [sx,  0.0, 0.0, 0.0],
        [0.0, sy,  0.0, 0.0],
        [0.0, 0.0, sz,  0.0],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float32)

def matriz_perspectiva(fovy, aspect, z_near, z_far):
    """Matriz de projeção perspectiva 4x4."""
    f = 1.0 / np.tan(np.radians(fovy) / 2.0)
    return np.array([
        [f / aspect, 0.0, 0.0, 0.0],
        [0.0, f, 0.0, 0.0],
        [0.0, 0.0, (z_far + z_near) / (z_near - z_far), (2.0 * z_far * z_near) / (z_near - z_far)],
        [0.0, 0.0, -1.0, 0.0]
    ], dtype=np.float32)

def matriz_ortogonal(left, right, bottom, top, z_near, z_far):
    """Matriz de projeção ortogonal 4x4."""
    return np.array([
        [2.0 / (right - left), 0.0, 0.0, -(right + left) / (right - left)],
        [0.0, 2.0 / (top - bottom), 0.0, -(top + bottom) / (top - bottom)],
        [0.0, 0.0, -2.0 / (z_far - z_near), -(z_far + z_near) / (z_far - z_near)],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float32)