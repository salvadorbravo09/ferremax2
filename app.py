from flask import Flask, request, jsonify, render_template, Response
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import time
import grpc
import product_pb2
import product_pb2_grpc
import os
import threading
from queue import Queue
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Asegurarse de que el directorio de uploads existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Diccionario para mantener un registro de los clientes conectados
connected_clients = set()

class Sucursal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    foto = db.Column(db.String(200))  # Ruta a la imagen

class ProductoSucursal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)

    producto = db.relationship('Producto', backref=db.backref('productos_sucursal', lazy=True))
    sucursal = db.relationship('Sucursal', backref=db.backref('productos_sucursal', lazy=True))

# Configuración del cliente gRPC
channel = grpc.insecure_channel('localhost:50051')
stub = product_pb2_grpc.ProductServiceStub(channel)

def check_stock_levels():
    """Verifica los niveles de stock y envía notificaciones si es necesario"""
    while True:
        with app.app_context():
            # Cambiado a 10 unidades como se solicita en el requisito #7
            productos_bajos = ProductoSucursal.query.filter(ProductoSucursal.cantidad < 10).all()
            for ps in productos_bajos:
                mensaje = {
                    'tipo': 'stock_bajo',
                    'producto': ps.producto.nombre,
                    'sucursal': ps.sucursal.nombre,
                    'cantidad': ps.cantidad
                }
                for client in connected_clients:
                    client.put(f"data: {json.dumps(mensaje)}\n\n")
        time.sleep(30)  # Verificar cada 30 segundos

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events')
def events():
    def event_stream():
        queue = Queue()
        connected_clients.add(queue)
        try:
            while True:
                data = queue.get()
                yield data
        except GeneratorExit:
            connected_clients.remove(queue)

    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/api/producto/<codigo>', methods=['GET'])
def obtener_producto(codigo):
    producto = Producto.query.filter_by(codigo=codigo).first()
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404

    sucursales = []
    for ps in producto.productos_sucursal:
        sucursales.append({
            'sucursal': ps.sucursal.nombre,
            'cantidad': ps.cantidad,
            'precio': ps.precio
        })
    return jsonify({
        'codigo': producto.codigo,
        'nombre': producto.nombre,
        'sucursales': sucursales
    })

API_KEY = 'apikey'  
CURRENCY_API_URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}/pair/CLP/USD'

@app.route('/api/buscar_producto', methods=['GET'])
def buscar_producto():
    nombre = request.args.get('nombre')
    print(f"Buscando producto con nombre: {nombre}")  # debug

    if not nombre:
        return jsonify({'error': 'Debe proporcionar un nombre de producto'}), 400

    productos = Producto.query.filter(Producto.nombre.ilike(f"%{nombre}%")).all()
    if not productos:
        return jsonify({'error': 'Producto no encontrado'}), 404

    # Obtener tasa de conversión a dólar
    try:
        response = requests.get(CURRENCY_API_URL)
        if response.status_code == 200:
            data = response.json()
            tasa_conversion = data.get('conversion_rate', 950)
        else:
            tasa_conversion = 950  # Valor por defecto
    except Exception:
        tasa_conversion = 950  # Valor por defecto en caso de error

    resultado = []
    for producto in productos:
        sucursales = []
        for ps in producto.productos_sucursal:
            sucursales.append({
                'sucursal': ps.sucursal.nombre,
                'cantidad': ps.cantidad,
                'precio': ps.precio,
                'precio_clp': round(ps.precio * tasa_conversion)
            })
        resultado.append({
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'sucursales': sucursales
        })

    return jsonify(resultado)

@app.route('/api/vender', methods=['POST'])
def vender_producto():
    data = request.get_json()
    cantidad = data.get('cantidad', 1)
    
    producto = Producto.query.filter_by(codigo=data['codigo']).first()
    sucursal = Sucursal.query.filter_by(nombre=data['sucursal']).first()
    
    ps = ProductoSucursal.query.filter_by(
        producto_id=producto.id,
        sucursal_id=sucursal.id
    ).first()
    
    if ps.cantidad < cantidad:
        return jsonify({'error': f'Solo hay {ps.cantidad} unidades disponibles'}), 400
    
    ps.cantidad -= cantidad
    db.session.commit()

    # Notificar a todos los clientes conectados sobre el cambio en el stock
    mensaje = {
        'tipo': 'stock_actualizado',
        'producto': producto.nombre,
        'sucursal': sucursal.nombre,
        'cantidad': ps.cantidad
    }
    for client in connected_clients:
        client.put(f"data: {json.dumps(mensaje)}\n\n")
    
    return jsonify({
        'mensaje': 'Venta realizada',
        'cantidad_restante': ps.cantidad
    })

@app.route('/api/agregar_producto', methods=['POST'])
def agregar_producto():
    try:
        # Obtener datos del formulario
        codigo = request.form.get('codigo')
        nombre = request.form.get('nombre')
        precio = float(request.form.get('precio'))
        cantidad = int(request.form.get('cantidad'))
        sucursal = request.form.get('sucursal')
        
        # Manejar la imagen
        if 'foto' not in request.files:
            return jsonify({'error': 'No se proporcionó una imagen'}), 400
        
        foto = request.files['foto']
        if foto.filename == '':
            return jsonify({'error': 'No se seleccionó una imagen'}), 400
        
        # Leer la imagen para validación
        foto_bytes = foto.read()
        
        # Validar con gRPC
        request_grpc = product_pb2.ProductRequest(
            codigo=codigo,
            nombre=nombre,
            precio=precio,
            cantidad=cantidad,
            sucursal=sucursal,
            foto=foto_bytes
        )
        
        response = stub.ValidateProduct(request_grpc)
        
        if not response.valid:
            return jsonify({'error': response.message, 'errors': response.errors}), 400
        
        # Guardar la imagen
        filename = secure_filename(f"{codigo}_{foto.filename}")
        foto_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        foto.seek(0)  # Resetear el puntero del archivo
        foto.save(foto_path)
        
        # Crear nuevo producto
        nuevo_producto = Producto(
            codigo=codigo,
            nombre=nombre,
            foto=filename
        )
        db.session.add(nuevo_producto)
        db.session.flush()
        
        # Obtener la sucursal
        sucursal_obj = Sucursal.query.filter_by(nombre=sucursal).first()
        if not sucursal_obj:
            return jsonify({'error': 'Sucursal no encontrada'}), 400
        
        # Crear relación ProductoSucursal
        nuevo_stock = ProductoSucursal(
            producto_id=nuevo_producto.id,
            sucursal_id=sucursal_obj.id,
            cantidad=cantidad,
            precio=precio
        )
        db.session.add(nuevo_stock)
        
        # Guardar cambios
        db.session.commit()
        
        # Notificar a los clientes conectados
        mensaje = {
            'tipo': 'producto_agregado',
            'producto': nuevo_producto.nombre,
            'sucursal': sucursal_obj.nombre,
            'cantidad': cantidad
        }
        for client in connected_clients:
            client.put(f"data: {json.dumps(mensaje)}\n\n")
        
        return jsonify({
            'mensaje': 'Producto agregado exitosamente',
            'producto': {
                'codigo': nuevo_producto.codigo,
                'nombre': nuevo_producto.nombre,
                'sucursal': sucursal_obj.nombre,
                'cantidad': cantidad,
                'precio': precio,
                'foto': filename
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/sucursales', methods=['GET'])
def obtener_sucursales():
    """Endpoint para obtener todas las sucursales disponibles (requisito #2)"""
    sucursales = Sucursal.query.all()
    resultado = []
    for sucursal in sucursales:
        resultado.append({
            'id': sucursal.id,
            'nombre': sucursal.nombre
        })
    return jsonify(resultado)

@app.route('/api/productos/sucursal/<nombre_sucursal>', methods=['GET'])
def productos_por_sucursal(nombre_sucursal):
    """Endpoint para obtener productos por sucursal (requisito #1)"""
    sucursal = Sucursal.query.filter_by(nombre=nombre_sucursal).first()
    if not sucursal:
        return jsonify({'error': 'Sucursal no encontrada'}), 404
    
    productos_sucursal = ProductoSucursal.query.filter_by(sucursal_id=sucursal.id).all()
    resultado = []
    
    for ps in productos_sucursal:
        producto = Producto.query.get(ps.producto_id)
        resultado.append({
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'precio': ps.precio,
            'cantidad': ps.cantidad,
            'foto': producto.foto
        })
    
    return jsonify(resultado)

@app.route('/api/conversion/dolar', methods=['GET'])
def obtener_conversion_dolar():
    """API para la conversión de dólar (requisito #3)"""
    try:
        # Obtener tasa de cambio de la API externa
        response = requests.get(CURRENCY_API_URL)
        if response.status_code != 200:
            # Valor por defecto en caso de error
            return jsonify({'tasa': 950, 'mensaje': 'Usando tasa por defecto debido a error en API externa'})
        
        data = response.json()
        tasa = data.get('conversion_rate', 950)  # valor por defecto si no se encuentra
        
        return jsonify({
            'tasa': tasa,
            'fecha': data.get('time_last_update_utc', 'desconocida')
        })
    except Exception as e:
        # En caso de error, usar un valor por defecto
        return jsonify({'tasa': 950, 'error': str(e), 'mensaje': 'Usando tasa por defecto'})

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

if __name__ == '__main__':
    # Iniciar el thread de verificación de stock en segundo plano
    import threading
    from queue import Queue
    stock_checker = threading.Thread(target=check_stock_levels, daemon=True)
    stock_checker.start()
    app.run(debug=True)

