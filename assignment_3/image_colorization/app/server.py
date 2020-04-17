import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from colorization import colorize
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/<dir>/<filename>')
def uploaded_file(dir, filename):
    return send_from_directory(dir, filename)


@app.route('/colorization_result')
def colorize_image():
    image_path_url = "http://127.0.0.1:5000/"
    name_grayscale = request.args.get('filename')
    path_grayscale = os.path.join(app.config['UPLOAD_FOLDER'], name_grayscale)
    colorized_url = image_path_url + colorize(path_grayscale, name_grayscale, "results")
    return render_template('colorized.html', grayscaled=image_path_url + path_grayscale, colorized=colorized_url)


@app.route('/', methods=['POST', 'GET'])
@app.route('/upload', methods=['POST', 'GET'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            grayscaled = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(grayscaled)
            return redirect(url_for('colorize_image', filename=filename))

    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)
