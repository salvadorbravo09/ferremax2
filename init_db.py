from app import db, Producto, Sucursal, ProductoSucursal, app

with app.app_context():
    db.create_all()

    # Crear sucursales
    s1 = Sucursal(nombre='Sucursal 1')
    s2 = Sucursal(nombre='Sucursal 3')
    db.session.add_all([s1, s2])
    db.session.commit()

    # Crear producto
    p1 = Producto(codigo='P1', nombre='Martillo')
    p2 = Producto(codigo='P2', nombre='Destornillador')
    db.session.add_all([p1, p2])
    db.session.commit()

    # Relacionar productos con sucursales
    ps1 = ProductoSucursal(producto_id=p1.id, sucursal_id=s1.id, cantidad=10, precio=150.0)
    ps2 = ProductoSucursal(producto_id=p1.id, sucursal_id=s2.id, cantidad=5, precio=155.0)
    ps3 = ProductoSucursal(producto_id=p2.id, sucursal_id=s1.id, cantidad=20, precio=80.0)
    db.session.add_all([ps1, ps2, ps3])
    db.session.commit()