from PIL import Image
from OpenGL.GL import *

ID_TEXTURA_GRAMA = None

def carregar_textura(caminho_imagem):
    """Carrega uma imagem, ajusta para potência de 2 e registra como textura OpenGL 2D."""
    global ID_TEXTURA_GRAMA
    try:
        img = Image.open(caminho_imagem)
        # Redimensiona automaticamente para 512x512 (potência de 2)
        img = img.resize((512, 512), Image.Resampling.LANCZOS)
        img = img.transpose(Image.FLIP_TOP_BOTTOM) # Inverte Y para o padrão OpenGL
        dados_img = img.convert("RGB").tobytes()

        id_textura = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, id_textura)

        # Repetição da textura (Mosaico)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        # Filtros de textura e Mipmaps
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Envia para a GPU
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 512, 512, 0, GL_RGB, GL_UNSIGNED_BYTE, dados_img)
        glGenerateMipmap(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, 0)
        ID_TEXTURA_GRAMA = id_textura
        print(f"Textura '{caminho_imagem}' carregada com sucesso! ID: {id_textura}")
        return id_textura
    except Exception as e:
        print(f"Erro ao carregar textura: {e}")
        return 0