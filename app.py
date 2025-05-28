from flask import Flask, request, jsonify, render_template, Response
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
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

class ProductoSucursal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)

    producto = db.relationship('Producto', backref=db.backref('productos_sucursal', lazy=True))
    sucursal = db.relationship('Sucursal', backref=db.backref('productos_sucursal', lazy=True))

def check_stock_levels():
    """Verifica los niveles de stock y envía notificaciones si es necesario"""
    while True:
        with app.app_context():
            productos_bajos = ProductoSucursal.query.filter(ProductoSucursal.cantidad <= 5).all()
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

    resultado = []
    for producto in productos:
        sucursales = []
        for ps in producto.productos_sucursal:
            sucursales.append({
                'sucursal': ps.sucursal.nombre,
                'cantidad': ps.cantidad,
                'precio': ps.precio,
                'precio_clp': round(ps.precio * 950)
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
    
