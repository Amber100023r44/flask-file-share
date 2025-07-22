from flask import Flask, request, send_from_directory, render_template
import os, time, threading

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
EXPIRY_SECONDS = 2 * 60 * 60

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        return f'{file.filename} uploaded successfully! <a href="/">Upload more</a>'
    return 'Upload failed.'

@app.route('/files')
def list_files():
    clean_expired_files()
    files = os.listdir(UPLOAD_FOLDER)
    return '<br>'.join([f'<a href="/download/{f}">{f}</a>' for f in files])

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

def clean_expired_files():
    now = time.time()
    for fname in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, fname)
        if os.path.isfile(path) and now - os.path.getmtime(path) > EXPIRY_SECONDS:
            os.remove(path)

def cleaner_thread():
    while True:
        time.sleep(600)
        clean_expired_files()

threading.Thread(target=cleaner_thread, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
