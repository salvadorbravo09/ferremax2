# Ferremax - Sistema de Gestión de Inventario y Ventas

Sistema de gestión de inventario y ventas para Ferremax, que permite buscar productos, gestionar stock por sucursal y realizar ventas de manera eficiente.

## Características

- 🔍 Búsqueda de productos por nombre
- 📍 Gestión de múltiples sucursales
- 📊 Control de inventario en tiempo real
- 💰 Cálculo automático de precios y totales
- 🛒 Sistema de ventas integrado
- 📱 Interfaz responsiva y moderna
- 🔄 Actualización automática de stock

## Requisitos

- Python 3.13.3 o superior
- pip
- Navegador web

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

5. Iniciar la aplicación:

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`
