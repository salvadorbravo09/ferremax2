import multiprocessing
import time
import grpc
from concurrent import futures
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from PIL import Image
import io

import product_pb2
import product_pb2_grpc

# Asegurarse de que el directorio actual está en el path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Configurar la conexión a la base de datos
DB_PATH = os.path.join(current_dir, 'instance', 'inventario.db')
engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

class ProductService(product_pb2_grpc.ProductServiceServicer):
    def ValidateProduct(self, request, context):
        inicio = time.time()
        errors = []
        session = Session()

        # Validar código
        producto_existente = None
        if request.codigo:
            producto_existente = session.execute(
                text("SELECT * FROM producto WHERE codigo = :codigo"),
                {"codigo": request.codigo}
            ).fetchone()

        if producto_existente:
            errors.append("El código de producto ya existe en la base de datos")

        # Validar nombre
        if not request.nombre or len(request.nombre) < 3:
            errors.append("El nombre del producto debe tener al menos 3 caracteres")

        # Validar precio
        if request.precio <= 0:
            errors.append("El precio debe ser mayor que 0")

        # Validar cantidad
        if request.cantidad <= 0:
            errors.append("La cantidad debe ser mayor que 0")

        # Validar sucursal
        sucursales = session.execute(text("SELECT nombre FROM sucursal")).fetchall()
        valid_sucursales = [sucursal[0] for sucursal in sucursales]

        if not valid_sucursales:
            valid_sucursales = ["Sucursal Santiago", "Sucursal Concepcion", "Sucursal Puerto Montt"]

        if request.sucursal not in valid_sucursales:
            errors.append(f"Sucursal no válida. Sucursales válidas: {', '.join(valid_sucursales)}")

        # Validar foto
        if request.foto:
            try:
                image = Image.open(io.BytesIO(request.foto))
                if image.format not in ['JPEG', 'PNG','WEBP']:
                    errors.append("La imagen debe ser en formato JPEG o PNG")
                if image.size[0] > 1920 or image.size[1] > 1080:
                    errors.append("La imagen no debe exceder 1920x1080 píxeles")
            except Exception as e:
                errors.append(f"Error al procesar la imagen: {str(e)}")
        else:
            errors.append("La foto es requerida")

        session.close()

        print(f"⏱️ Tiempo de respuesta gRPC: {time.time() - inicio:.3f} segundos")

        if errors:
            return product_pb2.ProductResponse(
                valid=False,
                message="Validación fallida",
                errors=errors
            )

        return product_pb2.ProductResponse(
            valid=True,
            message="Producto válido",
            errors=[]
        )

def serve():
    num_cores = multiprocessing.cpu_count()
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=num_cores * 4)
    )
    product_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
    server.add_insecure_port('[::]:50051')
    print(f"✅ Servidor gRPC iniciado en el puerto 50051 con {num_cores * 4} workers...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
