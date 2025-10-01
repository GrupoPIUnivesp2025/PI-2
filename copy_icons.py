import shutil
import os

source = r'c:\Users\raulk\OneDrive\Documentos\Estudos\Univesp\PI 2\aplicação\app\static\images\tema.png'
target_dir = r'c:\Users\raulk\OneDrive\Documentos\Estudos\Univesp\PI 2\aplicação\app\static\images'

icons = ['icon-192.png', 'icon-512.png', 'apple-touch-icon.png']

for icon in icons:
    target = os.path.join(target_dir, icon)
    try:
        shutil.copy2(source, target)
        print(f'Copied {icon}')
    except Exception as e:
        print(f'Error copying {icon}: {e}')

print('Done!')
