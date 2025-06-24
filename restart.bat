@echo off
echo Reiniciando servicios...

:: Detener procesos existentes
taskkill /f /im python.exe >nul 2>&1

:: Esperar un momento
timeout /t 2 /nobreak >nul

:: Iniciar el servidor gRPC en segundo plano
echo Iniciando servidor gRPC...
start cmd /c "python grpc_server.py"

:: Esperar un momento para que el servidor gRPC se inicie
timeout /t 3 /nobreak >nul

:: Iniciar la aplicación Flask
echo Iniciando aplicación web...
start cmd /c "python app.py"

echo Servicios reiniciados. Accede a http://127.0.0.1:5000/ en tu navegador.
