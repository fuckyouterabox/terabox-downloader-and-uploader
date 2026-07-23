import os
import sys
from terabox import TeraBox 

def main():
    if len(sys.argv) < 3:
        print("Uso: python upload_to_terabox.py <directorio_local> <ruta_terabox>")
        sys.exit(1)

    local_dir = sys.argv[1]
    remote_folder = sys.argv[2]
    
    cookie = os.environ.get("TERABOX_COOKIE")
    if not cookie:
        print("Error: No se encontró la variable TERABOX_COOKIE.")
        sys.exit(1)

    try:
        tb_client = TeraBox(cookie=cookie)
        
        for filename in os.listdir(local_dir):
            file_path = os.path.join(local_dir, filename)
            
            if os.path.isfile(file_path):
                print(f"Iniciando subida de: {filename}")
                print(f"Destino en TeraBox: {remote_folder}")
                
                tb_client.upload(file_path, remote_folder)
                
                print(f"¡Subida exitosa de {filename}!")
                
    except Exception as e:
        print(f"Ocurrió un error al intentar subir a TeraBox: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
