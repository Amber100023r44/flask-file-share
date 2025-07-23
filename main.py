from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            filename = secure_filename(uploaded_file.filename)
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('index'))

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    file_data = []
    total_size = 0

    for file in files:
        path = os.path.join(app.config['UPLOAD_FOLDER'], file)
        size = os.path.getsize(path)
        total_size += size
        file_data.append({
            "name": file,
            "size": round(size / (1024 * 1024), 2)  # size in MB
        })

    total_size_mb = round(total_size / (1024 * 1024), 2)

    return render_template('index.html', files=file_data, total_size=total_size_mb)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
