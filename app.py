from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
db = SQLAlchemy(app)

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

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/api/buscar_producto', methods=['GET'])
def buscar_producto():
    nombre = request.args.get('nombre')
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
                'precio': ps.precio
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
    producto_codigo = data.get('codigo')
    sucursal_nombre = data.get('sucursal')

    producto = Producto.query.filter_by(codigo=producto_codigo).first()
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404

    sucursal = Sucursal.query.filter_by(nombre=sucursal_nombre).first()
    if not sucursal:
        return jsonify({'error': 'Sucursal no encontrada'}), 404

    ps = ProductoSucursal.query.filter_by(producto_id=producto.id, sucursal_id=sucursal.id).first()
    if not ps:
        return jsonify({'error': 'Producto no disponible en la sucursal'}), 404

    if ps.cantidad <= 0:
        return jsonify({'error': 'Sin stock disponible'}), 400

    ps.cantidad -= 1
    db.session.commit()
    return jsonify({'mensaje': 'Venta realizada', 'cantidad_restante': ps.cantidad})

if __name__ == '__main__':
    app.run(debug=True)
