import os
from io import BytesIO

import cv2
import pytesseract
from flask import (Flask, render_template, request, send_file,
                   send_from_directory)
from flask_sqlalchemy import SQLAlchemy
from pytesseract import Output
from werkzeug.utils import secure_filename

app = Flask(__name__)
pythonAnywhereDir = '/home/salientautomation/doc-boundary-generator'
upload_folder = os.path.join('static', 'uploads')
#print(upload_folder)
app.config['UPLOAD'] = upload_folder

supported_files = ['.png', '.jpg', '.jpeg', '.tiff']

#Draw boundary boxes on file
def drawFile(file, name):
    img = cv2.imread(file)
    h, w, c = img.shape
    d = pytesseract.image_to_data(img, output_type=Output.DICT)
    # print(d.keys())
    n_boxes = len(d['text'])
    for i in range(n_boxes):
        if int(d['conf'][i]) > 60:
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    outputFileName = secure_filename('output-'+name)
    outputFile = os.path.join(app.config['UPLOAD'], outputFileName)
    cv2.imwrite(outputFile, img)
    return outputFile


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[1]
        print(extension)
        #heck for file type
        if (extension not in supported_files): return render_template('index.html', message='That file type is not supported')
        #end check
        file.save(os.path.join(app.root_path, app.config['UPLOAD'], filename))
        img = os.path.join(app.root_path, app.config['UPLOAD'], filename)
        outputFile = drawFile(img, filename)
        outputFileName = 'output-'+filename
        return render_template('index.html', img=outputFile, filename=outputFileName)
    return render_template('index.html', message='Image will render below')

# create download function for download files
@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    print(app.root_path)
    full_path = os.path.join(app.root_path, app.config['UPLOAD'])
    print(full_path)
    return send_from_directory(full_path, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)