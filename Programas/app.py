from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import time
from flask_socketio import SocketIO

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)

# Asegurarse de que la carpeta exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'photo' not in request.files:
            return redirect(request.url)
        file = request.files['photo']
        if file.filename == '':
            return redirect(request.url)
        if file:
            # Generar un nombre de archivo único usando timestamp
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            unique_filename = f"{int(time.time()*1000)}{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            # Notificar a todos los clientes que hay una nueva foto
            socketio.emit('new_photo')
            return redirect(url_for('index'))
    
    # Listar todas las fotos subidas y ordenarlas por fecha de modificación (más recientes primero)
    photos_dir = app.config['UPLOAD_FOLDER']
    photos = [f for f in os.listdir(photos_dir) if os.path.isfile(os.path.join(photos_dir, f))]
    photos.sort(key=lambda x: os.path.getmtime(os.path.join(photos_dir, x)), reverse=True)
    photos = [f'/static/uploads/{p}' for p in photos]
    return render_template('index.html', photos=photos)

if __name__ == '__main__':
    # Cambia host='0.0.0.0' para que sea accesible en tu red local
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
