@echo off
title Iniciando o Sirius com Flask + Cloudflare Tunnel
cd /d E:\EU\TCC\SIRIUS 2.0

:: Inicia o Flask
start "" python run.py

:: Espera 3 segundos para o Flask subir
timeout /t 3 >nul

:: Abre o tunnel Cloudflare apontando para o Flask
cloudflared.exe tunnel --url http://localhost:5000

pause
