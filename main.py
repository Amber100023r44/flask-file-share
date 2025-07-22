from flask import Flask, request, send_from_directory
import os, time, threading

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
EXPIRY_SECONDS = 2 * 60 * 60  # 2 hours

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return '''
    <h2>Upload a Video</h2>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file" accept="video/*" required>
        <button type="submit">Upload</button>
    </form>
    <br>
    <a href="/files">🔽 Download Files</a>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        return f'✅ {file.filename} uploaded! <a href="/">Upload more</a>'
    return '❌ Upload failed.'

@app.route('/files')
def list_files():
    clean_expired_files()
    files = os.listdir(UPLOAD_FOLDER)
    return '<h2>Available Files</h2>' + '<br>'.join(
        [f'<a href="/download/{f}">{f}</a>' for f in files]
    )

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

def clean_expired_files():
    now = time.time()
    for fname in os.listdir(UPLOAD_FOLDER):
        fpath = os.path.join(UPLOAD_FOLDER, fname)
        if os.path.isfile(fpath):
            if now - os.path.getmtime(fpath) > EXPIRY_SECONDS:
                try:
                    os.remove(fpath)
                    print(f"Deleted expired file: {fname}")
                except Exception as e:
                    print(f"Error deleting {fname}: {e}")

# Run cleaner in background every 10 minutes
def cleaner_thread():
    while True:
        time.sleep(600)  # every 10 minutes
        clean_expired_files()

threading.Thread(target=cleaner_thread, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
