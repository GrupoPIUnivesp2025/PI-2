import os
import base64

# SVG simples para o ícone da UNIVESP
svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="45" fill="#0d6efd"/>
  <circle cx="50" cy="50" r="35" fill="white"/>
  <text x="50" y="65" font-family="Arial, sans-serif" font-size="40" font-weight="bold" text-anchor="middle" fill="#0d6efd">U</text>
</svg>'''

# Diretório onde os ícones serão salvos
icon_dir = r'c:\Users\raulk\OneDrive\Documentos\Estudos\Univesp\PI 2\aplicação\app\static\images'

# Criar um arquivo SVG temporário
svg_path = os.path.join(icon_dir, 'icon.svg')
with open(svg_path, 'w') as f:
    f.write(svg_content)

print(f"Created SVG icon at {svg_path}")

# Para usar temporariamente até instalarmos o Pillow, vamos criar um placeholder PNG simples
# Vamos usar a imagem tema.png existente como base
import shutil

tema_path = os.path.join(icon_dir, 'tema.png')
if os.path.exists(tema_path):
    # Copiar tema.png para os ícones necessários
    icons = ['icon-192.png', 'icon-512.png', 'apple-touch-icon.png']
    for icon in icons:
        icon_path = os.path.join(icon_dir, icon)
        shutil.copy2(tema_path, icon_path)
        print(f"Created {icon} from tema.png")
else:
    print("tema.png não encontrado")
