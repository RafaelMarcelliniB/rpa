#!/bin/bash
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
