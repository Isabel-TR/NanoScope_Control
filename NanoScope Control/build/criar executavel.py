import PyInstaller.__main__
import os

pasta_atual = os.path.dirname(os.path.abspath(__file__))
os.chdir(pasta_atual)

print("[SISTEMA] Iniciando a fabricação avançada do executável portável...")
print("[SISTEMA] Isso pode levar alguns segundos. Aguarde...")

PyInstaller.__main__.run([
    'interface.py',
    '--noconsole',
    '--onefile',
    '--name=LabScope_Control',
    '--collect-all=customtkinter',
    '--collect-all=matplotlib',
    '--collect-all=pywinstyles'
])

print("\n" + "="*50)
print("[SUCESSO!] Executável gerado com todas as bibliotecas embutidas!")
print(f"Procure a pasta 'dist' em: {os.getcwd()}")
print("="*50)