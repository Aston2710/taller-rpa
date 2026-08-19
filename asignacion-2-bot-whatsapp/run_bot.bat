@echo off
cd /d "%~dp0"

echo Verificando dependencias...
pdm install

echo Iniciando bot de WhatsApp...
pdm run bot

pause
