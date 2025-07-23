from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

# --- Configuration ---
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # For flash messages

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', 'docx', 'xlsx'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB limit

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# --- Helpers ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- Routes ---
@app.route('/')
def index():
    file_list = os.listdir(app.config['UPLOAD_FOLDER'])
    total_size = sum(
        os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f))
        for f in file_list
    )
    total_size_mb = round(total_size / (1024 * 1024), 2)
    return render_template('index.html', files=file_list, total_size=total_size_mb)


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part in the request.')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('No file selected.')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Prevent overwriting files
        counter = 1
        original_filename = filename
        while os.path.exists(filepath):
            name, ext = os.path.splitext(original_filename)
            filename = f"{name}_{counter}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            counter += 1

        file.save(filepath)
        flash(f'Uploaded successfully: {filename}')
        return redirect(url_for('index'))
    else:
        flash('File type not allowed.')
        return redirect(url_for('index'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# --- Main ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
