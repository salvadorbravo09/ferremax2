from app import db, Producto, app

with app.app_context():
    db.create_all()

    # Agrega productos de ejemplo
    p1 = Producto(codigo='P1', nombre='Martillos', sucursal='Sucursal 1', cantidad=10, precio=150.0)
    p2 = Producto(codigo='P2', nombre='Destornilladores', sucursal='Sucursal 2', cantidad=25, precio=80.0)
    db.session.add_all([p1, p2])
    db.session.commit() 