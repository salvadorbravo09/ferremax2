@echo off
echo Iniciando entorno de Ferremax...

:: Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python no está instalado o no está en el PATH.
    exit /b 1
)

:: Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

:: Inicializar la base de datos si es necesario
if not exist instance\inventario.db (
    echo Inicializando la base de datos...
    python init_db.py
)

:: Generar archivos gRPC si es necesario
if not exist product_pb2.py (
    echo Generando archivos gRPC...
    python generate_grpc.py
)

:: Iniciar el servidor gRPC en segundo plano
echo Iniciando servidor gRPC...
start cmd /c "python grpc_server.py"

:: Esperar un momento para que el servidor gRPC se inicie
timeout /t 3 /nobreak >nul

:: Iniciar la aplicación Flask
echo Iniciando aplicación web...
python app.py

echo Deteniendo servicios...
taskkill /f /im python.exe >nul 2>&1
echo Aplicación cerrada.
