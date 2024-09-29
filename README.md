Appointment Booking and Chatbot Application

This project is a Flask-based web application that allows patients to book, view, and delete appointments, as well as interact with a chatbot. Doctors can also manage appointment availability. The chatbot is implemented using the RAG (Retrieval-Augmented Generation) model and integrated with Ollama's Phi3 for language model queries.

Features

1. Patient Interface:
   - View available appointments
   - Book an appointment
   - Delete booked appointments
   - Chat with a chatbot using Ollama's Phi3

2. Doctor Interface:
   - Add new appointments
   - Manage (view and delete) available appointments

3. Chatbot:
   - Retrieve responses from a custom language model using the `query_rag` function.
   - Manage chat history, including deleting the entire history.

4. Image Classification with ResNet:
  -Users can upload an image for classification.
  -The image is classified using a pre-trained ResNet model, and the result is displayed in a separate window.

Requirements

Python Packages

- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- Ollama (for Phi3 model)
- TensorFlow (for any additional ML features, if needed)

You can install the required packages using the following command:


--> pip install Flask Flask-SQLAlchemy SQLAlchemy

Ollama Phi3 Model

To use the chatbot functionality, ensure that the **Ollama Phi3 model** is installed on your PC. Visit [Ollama](https://ollama.com) for more information.

Installation Instructions

1. Clone this repository:

  --> git clone https://github.com/yourusername/appointment-chatbot-app.git


2. Navigate to the project directory:

 -->  cd appointment-chatbot-app


3. Install the Python dependencies:

 --> pip install -r requirements.txt


4. Ensure Ollama Phi3 is installed and configured correctly on your system.

Database Setup

Create the SQLite database by running the Flask application for the first time:

--> python app.py


The application will automatically create an `appointment.db` file for storing appointments and chat history.

Usage

Run the Flask application:


--> python app.py


The application will be available at `http://127.0.0.1:5000/`.

- Go to `/` for the **Patient Interface**.
- Go to `/doctor` for the **Doctor Interface**.
- Go to `/chat` to interact with the **Chatbot**.

### Routes Summary

- `/` - View and book available appointments.
- `/delete/<int:appointment_id>` - Delete a booked appointment (POST request).
- `/doctor` - Add and manage appointments (GET and POST requests).
- `/doctor/delete/<int:appointment_id>` - Delete an appointment as a doctor (POST request).
- `/chat` - Interact with the chatbot (GET and POST requests).
- `/delete_chat_history` - Delete the entire chat history (POST request).

### Folder Structure

- `app.py` - Main application file.
- `bot.py` - Contains the function `query_rag` for the chatbot.
- `templates/` - HTML templates for the Flask application (e.g., `index.html`, `doctor.html`, `chat.html`).
- `appointment.db` - SQLite database file.
-`resnet_model.h5` - Pre-trained ResNet model for image classification.
### License

This project is licensed under the MIT License. Feel free to use it for personal or commercial purposes.

### Acknowledgments

- [Flask](https://flask.palletsprojects.com/) for providing a simple and powerful web framework.
- [Ollama](https://ollama.com) for the Phi3 model used in the chatbot.

Feel free to contribute by creating pull requests or raising issues for any improvements or bug fixes!
