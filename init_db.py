from app import db, Producto, Sucursal, ProductoSucursal, app

with app.app_context():
    db.drop_all()
    db.create_all()

    # Crear sucursales
    sucursal1 = Sucursal(nombre='Sucursal Santiago')
    sucursal2 = Sucursal(nombre='Sucursal Concepcion')
    sucursal3 = Sucursal(nombre='Sucursal Puerto Montt')
    db.session.add_all([sucursal1, sucursal2, sucursal3])

    # Crear productos y guardar las referencias
    martillo = Producto(codigo='P1', nombre='Martillo')
    destornillador = Producto(codigo='P2', nombre='Destornillador')
    taladro = Producto(codigo='P3', nombre='Taladro')
    db.session.add_all([martillo, destornillador, taladro])
    db.session.commit()  # ¡Importante para obtener los IDs!

    # Relaciones ProductoSucursal usando las variables definidas
    stocks = [
        ProductoSucursal(
            producto_id=martillo.id, 
            sucursal_id=sucursal1.id, 
            cantidad=10, 
            precio=20.99
        ),
        ProductoSucursal(
            producto_id=martillo.id, 
            sucursal_id=sucursal2.id, 
            cantidad=5, 
            precio=155.35
        ),
        ProductoSucursal(
            producto_id=destornillador.id, 
            sucursal_id=sucursal1.id, 
            cantidad=20, 
            precio=80.50
        ),
        ProductoSucursal(
            producto_id=taladro.id, 
            sucursal_id=sucursal3.id, 
            cantidad=35, 
            precio=90.89
        )
    ]
    
    db.session.add_all(stocks)
    db.session.commit()