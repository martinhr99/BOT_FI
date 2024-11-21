#!/bin/bash

# Paso 1: Crear un entorno virtual en Python
echo "Creando un entorno virtual llamado 'bot_env'..."
mkvirtualenv bot_env --python=/usr/bin/python3.9  # Cambia "3.x" por la versión de Python que estés usando (ej. python3.9)

# Paso 2: Activar el entorno virtual
echo "Activando el entorno virtual..."
workon bot_env

# Paso 3: Instalar las dependencias necesarias
echo "Instalando dependencias..."
pip install python-telegram-bot[job-queue]

# Paso 4: Verificar si las dependencias se instalaron correctamente
echo "Verificando las dependencias instaladas..."
pip list

# Paso 5: Ejecutar el bot (si tienes un script bot.py en la misma carpeta)
echo "Ejecutando el bot..."
python /home/MRTN99/bot.py  
echo "¡Todo listo! El bot debería estar corriendo en tu entorno virtual."
