from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
db = SQLAlchemy(app)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    sucursal = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/producto/<codigo>', methods=['GET'])
def obtener_producto(codigo):
    producto = Producto.query.filter_by(codigo=codigo).first()
    if producto:
        return jsonify({
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'sucursal': producto.sucursal,
            'cantidad': producto.cantidad,
            'precio': producto.precio
        })
    else:
        return jsonify({'error': 'Producto no encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)
