# Ferremax - Sistema de Gestión de Inventario y Ventas

Sistema de gestión de inventario y ventas para Ferremax, que permite buscar productos, gestionar stock por sucursal y realizar ventas de manera eficiente.

## Características

- 🔍 Búsqueda de productos por nombre
- 📍 Gestión de múltiples sucursales
- 📊 Control de inventario en tiempo real
- 💰 Cálculo automático de precios y conversión de divisas
- 🛒 Sistema de ventas integrado
- 📱 Interfaz responsiva y moderna
- 🔄 Actualización automática de stock
- 🚨 Alertas en tiempo real para stock bajo (menos de 10 unidades)
- 🔒 Validación de productos con gRPC

## Requisitos

- Python 3.13.3 o superior
- pip
- Navegador web moderno con soporte para SSE (Server Sent Events)

## Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/salvadorbravo09/ferremax2.git
cd ferremax2
```

2. Crear y activar un entorno virtual (opcional):

```bash
# Windows
python -m venv venv
venv\Scripts\activate
```

3. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

4. Inicializar la base de datos:

```bash
python init_db.py
```

5. Generar los archivos gRPC (si es necesario):

```bash
python generate_grpc.py
```

6. Iniciar el servidor gRPC:

```bash
# En una nueva terminal
python grpc_server.py
```

7. Iniciar la aplicación web:

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## Método Alternativo (Windows)

También puedes iniciar toda la aplicación utilizando el script de inicio:

```bash
start.bat
```

Este script configurará todo automáticamente.

## Funcionalidades Implementadas

1. ✅ API REST para obtener productos por sucursal
2. ✅ Select con valores de sucursal dinámicos
3. ✅ API para la conversión de dólar
4. ✅ Validación de stock en el frontend
5. ✅ Validación de valores mayores que cero
6. ✅ Alertas de stock bajo (menos de 10 unidades)
7. ✅ Pantalla de creación de productos
8. ✅ Integración con gRPC para validación de productos
   - ✅ Archivos ProtoBuf
   - ✅ Archivos stub generados
   - ✅ Servidor gRPC conectado a la BD existente
