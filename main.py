# pip3 install flask opencv-python
from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import cv2
import os

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cartoon_filter(img):
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply a median blur to reduce image noise
    gray = cv2.medianBlur(gray, 5)

    # Detect edges using adaptive thresholding
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

    # Apply a bilateral filter to create a cartoon effect
    color = cv2.bilateralFilter(img, 9, 300, 300)

    # Combine the edges and color images
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    return cartoon

def processImage(filename, operation):
    print(f"the operation is {operation} and filename is {filename}")
    img = cv2.imread(f"uploads/{filename}")
    match operation:
        case "cgray":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            newFilename = f"static/{filename.split('.')[0]}_gray.png"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "cwebp": 
            newFilename = f"static/{filename.split('.')[0]}.webp"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cjpg": 
            newFilename = f"static/{filename.split('.')[0]}.jpg"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cpng": 
            newFilename = f"static/{filename.split('.')[0]}.png"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cred":
            imgProcessed = img.copy()
            imgProcessed[:, :, 0] = 0  # Blue channel
            imgProcessed[:, :, 1] = 0  # Green channel
            newFilename = f"static/{filename.split('.')[0]}_red.jpg"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "ccartoon":
            imgProcessed = cartoon_filter(img)
            newFilename = f"static/{filename.split('.')[0]}_cartoon.jpg"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST": 
        operation = request.form.get("operation")
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = processImage(filename, operation)
            flash(f"Your image has been processed and is available <a href='/{new}' target='_blank'>here</a>")
            return render_template("index.html")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
