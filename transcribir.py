import whisper
import sys
import os
import requests
from workreport.settings import BASE_DIR
from workreport.local_settings import MAIN_URL
#PATH = "/var/www/django/workreport/"

# Verificar que se proporcionó un archivo como argumento
if len(sys.argv) != 3:
    print("Uso: python3 transcribir.py <ruta_al_archivo_audio> <id_objeto>")
    sys.exit(1)

# Obtener la ruta del archivo de audio desde los argumentos
#audio_file = "{}{}".format(PATH, sys.argv[1])
audio_file = "{}{}".format(BASE_DIR, sys.argv[1])
obj_id = sys.argv[2]

# Verificar si el archivo existe
if not os.path.isfile(audio_file):
    print(f"Error: El archivo '{audio_file}' no existe.")
    sys.exit(1)

# Generar el nombre del archivo de salida (cambia extensión a .txt)
output_file = os.path.splitext(audio_file)[0] + ".txt"
print(output_file)

# Define una ruta personalizada
#CACHE_DIR = "{}whisper_cache".format(PATH)
CACHE_DIR = "{}whisper_cache".format(BASE_DIR)
#CACHE_DIR.mkdir(parents=True, exist_ok=True)  # Crea el directorio si no existe

# Configura Whisper
os.environ["WHISPER_CACHE_DIR"] = str(CACHE_DIR)

# Cargar el modelo preentrenado de Whisper
#print("Cargando el modelo de Whisper...")
model = whisper.load_model("base")  # Puedes usar "tiny", "base", "small", "medium", o "large"

# Transcribir el audio
#print("Transcribiendo el audio...")
result = model.transcribe(audio_file, language="es")

#print("Sending...")
#res = requests.post("https://workreport.shidix.es/gestion/set-note-concept", headers={"Accept": "application/txt"}, data={"token": "1234", "text": result["text"], "report": obj_id})
res = requests.post("{}/gestion/set-note-concept".format(MAIN_URL), headers={"Accept": "application/txt"}, data={"token": "1234", "text": result["text"], "report": obj_id})
>>>>>>> 6d9868916d6e007aafbdbf1d96a3796ba8c04be8
# Guardar la transcripción en el archivo de salida
#print(res)
#with open(output_file, "w", encoding="utf-8") as file:
#    file.write(result["text"])

#print(f"Transcripción completa. Archivo guardado como: {output_file}")
