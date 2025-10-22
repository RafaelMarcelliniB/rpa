"""
Script de Configuración Automática del RPA Validador
Ejecutar: python setup.py
"""

import os
import sys
import subprocess
import platform

def print_header(text):
    """Imprime encabezado"""
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80 + "\n")

def print_step(step_num, text):
    """Imprime paso de instalación"""
    print(f"\n[Paso {step_num}] {text}")
    print("-"*80)

def check_python_version():
    """Verifica versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detectado")

def create_directory_structure():
    """Crea estructura de directorios"""
    directories = ['input', 'output', 'logs', 'tests']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Carpeta '{directory}/' creada")
        else:
            print(f"  Carpeta '{directory}/' ya existe")

def create_venv():
    """Crea entorno virtual"""
    if os.path.exists('venv'):
        print("  Entorno virtual ya existe")
        return True
    
    try:
        print("  Creando entorno virtual...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✓ Entorno virtual creado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al crear entorno virtual: {e}")
        return False

def get_pip_path():
    """Obtiene ruta del pip en el entorno virtual"""
    system = platform.system()
    if system == "Windows":
        return os.path.join('venv', 'Scripts', 'pip.exe')
    else:
        return os.path.join('venv', 'bin', 'pip')

def install_dependencies():
    """Instala dependencias"""
    pip_path = get_pip_path()
    
    if not os.path.exists(pip_path):
        print("❌ Error: No se encontró pip en el entorno virtual")
        return False
    
    try:
        print("  Actualizando pip...")
        subprocess.run([pip_path, 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        
        print("  Instalando PyPDF2...")
        subprocess.run([pip_path, 'install', 'PyPDF2==3.0.1'], 
                      check=True, capture_output=True)
        
        print("  Instalando python-dateutil...")
        subprocess.run([pip_path, 'install', 'python-dateutil==2.8.2'], 
                      check=True, capture_output=True)
        
        print("✓ Dependencias instaladas")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {e}")
        return False

def create_requirements_file():
    """Crea archivo requirements.txt"""
    content = """# Dependencias para el RPA Validador de Entregable 1
PyPDF2==3.0.1
python-dateutil==2.8.2
"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Archivo requirements.txt creado")

def create_gitignore():
    """Crea archivo .gitignore"""
    content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Archivos de entrada/salida
input/*.pdf
output/*.json
output/*.txt
logs/*.log

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Sistema operativo
.DS_Store
Thumbs.db
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Archivo .gitignore creado")

def create_batch_script_windows():
    """Crea script batch para Windows"""
    content = """@echo off
echo ====================================
echo RPA VALIDADOR - ENTREGABLE 1
echo ====================================
echo.

REM Verificar si existe el PDF
if not exist "input\\entregable1.pdf" (
    echo ERROR: No se encontro input\\entregable1.pdf
    echo.
    echo Coloque su PDF en la carpeta input/ con el nombre entregable1.pdf
    pause
    exit /b 1
)

REM Activar entorno virtual
call venv\\Scripts\\activate

REM Validar PDF
python rpa_validador.py input\\entregable1.pdf

echo.
echo ====================================
echo Reportes generados en carpeta output/
echo ====================================
echo.

pause
"""
    
    with open('validar.bat', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Script validar.bat creado")

def create_bash_script_unix():
    """Crea script bash para Linux/macOS"""
    content = """#!/bin/bash
echo "===================================="
echo "RPA VALIDADOR - ENTREGABLE 1"
echo "===================================="
echo

# Verificar si existe el PDF
if [ ! -f "input/entregable1.pdf" ]; then
    echo "ERROR: No se encontró input/entregable1.pdf"
    echo
    echo "Coloque su PDF en la carpeta input/ con el nombre entregable1.pdf"
    read -p "Presiona Enter para continuar..."
    exit 1
fi

# Activar entorno virtual
source venv/bin/activate

# Validar PDF
python rpa_validador.py input/entregable1.pdf

echo
echo "===================================="
echo "Reportes generados en carpeta output/"
echo "===================================="
echo

read -p "Presiona Enter para continuar..."
"""
    
    with open('validar.sh', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Dar permisos de ejecución en Unix
    if platform.system() != "Windows":
        os.chmod('validar.sh', 0o755)
    
    print("✓ Script validar.sh creado")

def create_readme_example():
    """Crea archivo de ejemplo en input"""
    content = """# Carpeta INPUT

Coloca aquí los PDFs del Entregable 1 que deseas validar.

Ejemplo:
- PRIMER_ENTREGABLE_PACRO_YUNCAN.pdf
- entregable1_version2.pdf

Nota: Los PDFs deben tener texto seleccionable (no ser imágenes escaneadas).
"""
    
    with open('input/README.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Archivo de ejemplo en input/ creado")

def show_next_steps():
    """Muestra los siguientes pasos"""
    system = platform.system()
    
    print_header("INSTALACIÓN COMPLETADA")
    
    print("📋 SIGUIENTES PASOS:\n")
    
    print("1. Coloca tu PDF en la carpeta input/")
    print("   Ejemplo: input/entregable1.pdf\n")
    
    print("2. Ejecuta la validación:\n")
    
    if system == "Windows":
        print("   Opción A (Script automático):")
        print("   > validar.bat\n")
        print("   Opción B (Manual):")
        print("   > venv\\Scripts\\activate")
        print("   > python rpa_validador.py input\\entregable1.pdf\n")
    else:
        print("   Opción A (Script automático):")
        print("   $ ./validar.sh\n")
        print("   Opción B (Manual):")
        print("   $ source venv/bin/activate")
        print("   $ python rpa_validador.py input/entregable1.pdf\n")
    
    print("3. Revisa los reportes en la carpeta output/\n")
    
    print("📁 ESTRUCTURA DEL PROYECTO:")
    print("""
    rpa-validador-entregable1/
    ├── rpa_validador.py       # Script principal
    ├── requirements.txt       # Dependencias
    ├── validar.bat/sh         # Script de ejecución rápida
    ├── input/                 # ← Coloca tus PDFs aquí
    ├── output/                # ← Reportes generados aquí
    └── logs/                  # Logs de ejecución
    """)
    
    print("\n💡 AYUDA:")
    print("   - README.md: Documentación completa")
    print("   - Issues: Reportar problemas\n")

def main():
    """Función principal"""
    print_header("INSTALADOR RPA VALIDADOR - ENTREGABLE 1")
    
    print("Sistema operativo:", platform.system())
    print("Python:", sys.version)
    
    # Paso 1: Verificar Python
    print_step(1, "Verificando versión de Python")
    check_python_version()
    
    # Paso 2: Crear estructura de directorios
    print_step(2, "Creando estructura de directorios")
    create_directory_structure()
    
    # Paso 3: Crear archivos de configuración
    print_step(3, "Creando archivos de configuración")
    create_requirements_file()
    create_gitignore()
    create_readme_example()
    
    # Paso 4: Crear entorno virtual
    print_step(4, "Creando entorno virtual")
    if not create_venv():
        print("\n❌ Error en la instalación")
        sys.exit(1)
    
    # Paso 5: Instalar dependencias
    print_step(5, "Instalando dependencias")
    if not install_dependencies():
        print("\n❌ Error en la instalación")
        sys.exit(1)
    
    # Paso 6: Crear scripts de ejecución
    print_step(6, "Creando scripts de ejecución")
    if platform.system() == "Windows":
        create_batch_script_windows()
    else:
        create_bash_script_unix()
    
    # Mostrar siguientes pasos
    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)