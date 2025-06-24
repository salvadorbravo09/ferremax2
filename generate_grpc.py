import os
import subprocess
import shutil

# Asegurarse de que estamos en el directorio correcto
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

# Comando para generar los archivos Python
protoc_command = [
    'python', '-m', 'grpc_tools.protoc',
    '-I.',
    '--python_out=.',
    '--grpc_python_out=.',
    'proto/product.proto'
]

try:
    # Ejecutar el comando
    subprocess.run(protoc_command, check=True)
    
    # Verificar si los archivos se generaron en el directorio proto
    proto_dir = os.path.join(current_dir, 'proto')
    if os.path.exists(os.path.join(proto_dir, 'product_pb2.py')):
        # Mover los archivos al directorio raíz
        shutil.move(os.path.join(proto_dir, 'product_pb2.py'), current_dir)
        shutil.move(os.path.join(proto_dir, 'product_pb2_grpc.py'), current_dir)
    
    print("Archivos gRPC generados exitosamente:")
    print("- product_pb2.py")
    print("- product_pb2_grpc.py")
except subprocess.CalledProcessError as e:
    print(f"Error al generar los archivos gRPC: {e}")
except Exception as e:
    print(f"Error inesperado: {e}") 