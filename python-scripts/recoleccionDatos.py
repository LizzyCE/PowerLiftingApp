import os
import yt_dlp

# === CONFIGURACIÓN ===
urls_file = "urls.txt"  # Archivo con URLs si se elige la opción manual
download_archive = "download_archive.txt"

# Palabras clave para clasificación de levantamientos
movimientos = {
    "squat": "Sentadilla",
    "sentadilla": "Sentadilla",
    "bench": "PressBanca",
    "banca": "PressBanca",
    "press": "PressBanca",
    "deadlift": "PesoMuerto",
    "peso muerto": "PesoMuerto"
}

# Crear carpetas para cada tipo de movimiento
for carpeta in set(movimientos.values()):
    os.makedirs(carpeta, exist_ok=True)
os.makedirs("Otros", exist_ok=True)

# Clasificar el video según metadatos
def clasificar_video(info):
    texto = f"{info.get('title', '')} {info.get('description', '')} {' '.join(info.get('tags') or [])}".lower()
    for palabra, carpeta in movimientos.items():
        if palabra in texto:
            return carpeta
    return "Otros"

# Opciones de descarga
def obtener_opciones(output_dir):
    return {
        "outtmpl": os.path.join(output_dir, "%(title).80s.%(ext)s"),
        "format": "bestvideo+bestaudio/best",    # mejor video y mejor audio
        "merge_output_format": "mp4",            # salida final en .mp4
        "quiet": False,
        "download_archive": download_archive,    # evita repetir descargas
        "noplaylist": True,
    }

# Descargar una lista de URLs
def descargar_urls(urls):
    for url in urls:
        try:
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)
                carpeta = clasificar_video(info)
                print(f"\n➡️  Descargando: {info['title']}")
                print(f"   Clasificado como: {carpeta}")

                opciones = obtener_opciones(carpeta)
                with yt_dlp.YoutubeDL(opciones) as ydl2:
                    ydl2.download([url])
        except Exception as e:
            print(f"❌ Error con {url}: {e}")

# Cargar URLs desde archivo
def cargar_urls_de_archivo():
    with open(urls_file, "r") as f:
        return [line.strip() for line in f if line.strip()]

# Buscar en el canal oficial de IPF por palabra clave
def buscar_en_canal_ipf():
    canal_url = "https://www.youtube.com/@powerliftingtv/videos"
    
    palabras_clave = input("🔍 Palabra clave para buscar (ej. deadlift, bench, squat): ").strip()
    max_videos = input("¿Cuántos videos quieres descargar? (Enter para 5): ").strip()
    max_videos = int(max_videos) if max_videos.isdigit() else 5

    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "dump_single_json": True,
    }

    print("\n🔎 Buscando videos en el canal de IPF...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        canal_info = ydl.extract_info(canal_url, download=False)
        resultados = [
            entry["url"] for entry in canal_info["entries"]
            if palabras_clave.lower() in entry["title"].lower()
        ][:max_videos]

    if not resultados:
        print("⚠️  No se encontraron videos con esa palabra clave.")
        return

    print(f"📥 {len(resultados)} videos encontrados. Iniciando descarga...")
    descargar_urls(resultados)

# Menú principal
def menu():
    print("\n=== Descargador de Videos IPF ===")
    print("1. Descargar desde archivo 'urls.txt'")
    print("2. Buscar y descargar videos del canal oficial de IPF")
    opcion = input("Elige una opción (1 o 2): ").strip()

    if opcion == "1":
        urls = cargar_urls_de_archivo()
        descargar_urls(urls)
    elif opcion == "2":
        buscar_en_canal_ipf()
    else:
        print("Opción no válida.")

if __name__ == "__main__":
    menu()
