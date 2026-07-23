import os
import sys

# IMPORTANTE: Esta es la importación de la librería de TeraBox.
# Dependiendo de la librería exacta que uses (ej. terabox-api, terabox-wrapper),
# la forma de importarla y llamarla puede variar ligeramente. 
# Este código asume la estructura estándar de la mayoría de wrappers en Python.
try:
    from terabox import TeraBox
except ImportError:
    print("Error: No se encontró la librería 'terabox'. Asegúrate de que se instaló en el workflow.")
    sys.exit(1)

def main():
    # 1. Validar que se pasaron los argumentos correctos desde GitHub Actions
    if len(sys.argv) < 3:
        print("Uso: python upload_to_terabox.py <directorio_local> <ruta_terabox>")
        sys.exit(1)

    local_dir = sys.argv[1]
    remote_folder = sys.argv[2]
    
    # 2. Obtener la cookie de los secretos de GitHub Actions
    cookie = os.environ.get("TERABOX_COOKIE")
    if not cookie:
        print("Error Crítico: No se encontró la variable TERABOX_COOKIE en el entorno.")
        sys.exit(1)

    # 3. Inicializar el cliente de TeraBox
    print("Autenticando en TeraBox...")
    try:
        tb_client = TeraBox(cookie=cookie)
    except Exception as e:
        print(f"Error al autenticar con TeraBox: {e}")
        sys.exit(1)

    # 4. Validar que la carpeta de descargas exista
    if not os.path.exists(local_dir):
        print(f"Error: El directorio local '{local_dir}' no existe. No hay nada que subir.")
        sys.exit(1)

    # 5. Obtener lista de archivos descargados
    archivos = [f for f in os.listdir(local_dir) if os.path.isfile(os.path.join(local_dir, f))]
    
    if not archivos:
        print("No se encontraron archivos en el directorio de descarga.")
        sys.exit(0)

    print(f"Se encontraron {len(archivos)} archivo(s) para subir a: {remote_folder}")
    print("-" * 40)

    # 6. Iterar y subir cada archivo
    archivos_exitosos = 0
    archivos_fallidos = 0

    for filename in archivos:
        file_path = os.path.join(local_dir, filename)
        print(f"-> Iniciando subida: {filename}")
        
        try:
            # La mayoría de librerías usan un método .upload(archivo_local, ruta_remota)
            tb_client.upload(file_path, remote_folder)
            print(f"[EXITO] {filename} subido correctamente.")
            archivos_exitosos += 1
        except Exception as e:
            print(f"[ERROR] Falló la subida de {filename}. Detalles: {str(e)}")
            archivos_fallidos += 1

    # 7. Resumen final
    print("-" * 40)
    print("RESUMEN DE SUBIDA:")
    print(f"Exitosos: {archivos_exitosos}")
    print(f"Fallidos: {archivos_fallidos}")
    print("-" * 40)

    # Si algún archivo falló, hacemos que el workflow de GitHub Actions marque un error (cruz roja)
    if archivos_fallidos > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
