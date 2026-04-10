import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from PIL import Image
from rembg import remove

# -------------------------------
# Configuration
# -------------------------------
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# Create folders safely
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = "supersecretkey"


# -------------------------------
# Helper Functions
# -------------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def remove_background(input_path, output_path):
    try:
        input_img = Image.open(input_path).convert("RGBA")
        output_img = remove(input_img)
        output_img.save(output_path)
    except Exception as e:
        print("Error removing background:", e)


# -------------------------------
# Routes
# -------------------------------
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/remback', methods=['POST'])
def remback():
    if 'file' not in request.files:
        return render_template('home.html', error="No file uploaded")

    file = request.files['file']

    if file.filename == '':
        return render_template('home.html', error="No file selected")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)

        # Output file name
        output_filename = filename.rsplit('.', 1)[0] + "_rembg.png"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        # Remove background
        remove_background(input_path, output_path)

        return render_template(
            'home.html',
            org_img_name=filename,
            rembg_img_name=output_filename
        )

    return render_template('home.html', error="Invalid file format")


# -------------------------------
# Run App (Render Compatible)
# -------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
