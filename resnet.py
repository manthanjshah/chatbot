from flask import Flask, request, render_template, redirect, url_for
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os
import sys


sys.stdout.reconfigure(encoding='utf-8')


app = Flask(__name__)

# Load the ResNet model
model = load_model('C:/Users/Manthan Jigar shah/ml learning/chatbot/my_resnet101_model.h5')

# Define the class labels based on your model's training
class_labels = ['Melanocytic nevi',
'Melanoma',
'Benign keratosis-like lesions',
'Basal cell carcinoma',
'Actinic keratoses',
'Vascular lesions',
'Dermatofibroma']  # Replace with your actual class labels

@app.route('/')
def index():
    return render_template('indexresnet.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            img_path = os.path.join('uploads', file.filename)
            file.save(img_path)

            # Load and preprocess the image
            img = image.load_img(img_path, target_size=(224, 224))  # Adjust target size as per your model
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
            img_array /= 255.0  # Normalize the image

            # Make predictions
            predictions = model.predict(img_array)
            predicted_class = class_labels[np.argmax(predictions)]

            return render_template('result.html', prediction=predicted_class)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
