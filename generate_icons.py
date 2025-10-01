from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    # Criar uma nova imagem com fundo azul (cor da UNIVESP)
    background_color = "#0d6efd"  # Azul Bootstrap primary
    image = Image.new('RGB', (size, size), background_color)
    draw = ImageDraw.Draw(image)
    
    # Adicionar um círculo branco
    margin = size // 4
    draw.ellipse([margin, margin, size - margin, size - margin], fill='white')
    
    # Adicionar texto "U" em azul
    try:
        font_size = size // 2
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    text = "U"
    text_color = background_color
    
    # Centralizar o texto
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, font=font, fill=text_color)
    
    # Salvar a imagem
    image.save(filename)

# Diretório onde os ícones serão salvos
icon_dir = r'c:\Users\raulk\OneDrive\Documentos\Estudos\Univesp\PI 2\aplicação\app\static\images'

# Criar os ícones em diferentes tamanhos
icons = {
    'icon-192.png': 192,
    'icon-512.png': 512,
    'apple-touch-icon.png': 180,
    'favicon.ico': 32
}

for filename, size in icons.items():
    filepath = os.path.join(icon_dir, filename)
    create_icon(size, filepath)
    print(f"Created {filename}")
