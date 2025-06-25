from app import db, Producto, Sucursal, ProductoSucursal, app

with app.app_context():
    # 🔁 Borra y recrea todas las tablas de forma eficiente
    db.drop_all()
    db.create_all()

    # 🚀 Crea sucursales
    sucursales = {
        "Santiago": Sucursal(nombre="Sucursal Santiago"),
        "Concepcion": Sucursal(nombre="Sucursal Concepcion"),
        "Puerto Montt": Sucursal(nombre="Sucursal Puerto Montt")
    }

    # 🚀 Crea productos
    productos = {
        "Martillo": Producto(codigo="P1", nombre="Martillo"),
        "Destornillador": Producto(codigo="P2", nombre="Destornillador"),
        "Taladro": Producto(codigo="P3", nombre="Taladro")
    }

    # ✅ Guarda sucursales y productos en la DB
    db.session.add_all(list(sucursales.values()) + list(productos.values()))
    db.session.commit()  # Necesario para obtener IDs

    # 📦 Crea relaciones producto-sucursal (stock y precio)
    relaciones = [
        ("Martillo", "Santiago", 10, 20.99),
        ("Martillo", "Concepcion", 5, 155.35),
        ("Destornillador", "Santiago", 20, 80.50),
        ("Taladro", "Puerto Montt", 35, 90.89)
    ]

    producto_sucursal_objs = [
        ProductoSucursal(
            producto_id=productos[prod].id,
            sucursal_id=sucursales[suc].id,
            cantidad=cant,
            precio=precio
        )
        for prod, suc, cant, precio in relaciones
    ]

    db.session.add_all(producto_sucursal_objs)
    db.session.commit()

    print("✅ Base de datos inicializada con datos de prueba.")
