
import subprocess
import shutil
from pathlib import Path

# 📍 Definir rutas
BASE_DIR = Path(__file__).resolve().parent
PROTO_DIR = BASE_DIR / 'proto'
OUTPUT_FILES = ['product_pb2.py', 'product_pb2_grpc.py']

# 💬 Función para ejecutar el comando de generación
def generate_grpc_files():
    print("🔧 Generando archivos gRPC...")

    protoc_cmd = [
        'python', '-m', 'grpc_tools.protoc',
        f'-I{PROTO_DIR}',
        f'--python_out={PROTO_DIR}',
        f'--grpc_python_out={PROTO_DIR}',
        str(PROTO_DIR / 'product.proto')
    ]

    try:
        subprocess.run(protoc_cmd, check=True)

        # 📦 Mover archivos generados al directorio raíz
        for filename in OUTPUT_FILES:
            src = PROTO_DIR / filename
            dst = BASE_DIR / filename
            if src.exists():
                shutil.move(str(src), str(dst))
                print(f"✅ {filename} generado y movido correctamente.")
            else:
                print(f"⚠️ {filename} no fue generado.")
                
    except subprocess.CalledProcessError:
        print("❌ Error: Falló la generación de archivos gRPC (protoc).")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == '__main__':
    generate_grpc_files()
