from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os
from bot import query_rag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appointment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'  # Required for session management
db = SQLAlchemy(app)


# Models
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    is_available = db.Column(db.Boolean, default=True)  # Tracks if appointment is available
    patient_name = db.Column(db.String(100), nullable=True)  # Stores the name of the patient if booked


class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)


# Create the database if it doesn't exist
if not os.path.exists('appointment.db'):
    with app.app_context():
        db.create_all()


# Route for the patient to book, view, and delete appointments
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        patient_name = request.form.get('patient_name')
        appointment_id = request.form.get('appointment_id')

        if patient_name and appointment_id:
            appointment = Appointment.query.get(appointment_id)
            if appointment and appointment.is_available:
                appointment.is_available = False
                appointment.patient_name = patient_name
                db.session.commit()
                session['patient_name'] = patient_name  # Store patient name in session
                flash('Appointment booked successfully!', 'success')
            else:
                flash('Appointment not available.', 'danger')

    # Fetch available appointments for booking
    available_appointments = Appointment.query.filter_by(is_available=True).all()

    # Fetch booked appointments for the current patient
    booked_appointments = []
    if 'patient_name' in session:
        booked_appointments = Appointment.query.filter_by(is_available=False,
                                                          patient_name=session['patient_name']).all()

    return render_template('index.html', available_appointments=available_appointments,
                           booked_appointments=booked_appointments)


# Route for patients to delete a booked appointment
@app.route('/delete/<int:appointment_id>', methods=['POST'])
def delete_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if appointment and appointment.patient_name == session.get('patient_name'):
        appointment.is_available = True  # Make appointment available again
        appointment.patient_name = None  # Remove patient booking
        db.session.commit()
        flash('Appointment deleted successfully!', 'success')
    else:
        flash('You cannot delete this appointment.', 'danger')
    return redirect(url_for('index'))


# Route for doctors to add and manage available appointments
@app.route('/doctor', methods=['GET', 'POST'])
def doctor_interface():
    if request.method == 'POST':
        date = request.form.get('date')
        time = request.form.get('time')
        if date and time:
            new_appointment = Appointment(date=date, time=time, is_available=True)
            db.session.add(new_appointment)
            db.session.commit()
            flash('Appointment added successfully!', 'success')
        else:
            flash('Date and time are required.', 'danger')

    # Display all appointments for management
    appointments = Appointment.query.all()
    return render_template('doctor.html', appointments=appointments)


# Route for doctors to delete appointments
@app.route('/doctor/delete/<int:appointment_id>', methods=['POST'])
def delete_appointment_doctor(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        db.session.delete(appointment)
        db.session.commit()
        flash('Appointment deleted successfully!', 'success')
    else:
        flash('Appointment not found.', 'danger')
    return redirect(url_for('doctor_interface'))
# Route to clear all chat history

# Route to delete the complete chat history
@app.route('/delete_chat_history', methods=['POST'])
def delete_chat_history():
    try:
        # Delete all chat history records from the database
        db.session.query(ChatHistory).delete()
        db.session.commit()
        flash('Chat history deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting chat history: {str(e)}', 'danger')
    return redirect(url_for('chat'))


# Chatbot integration
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_message = request.form.get('message')
        if user_message:
            # Get bot response using query_rag
            response, updated_chat_history = query_rag(user_message, "")

            # Store chat history in the database
            new_chat = ChatHistory(user_message=user_message, bot_response=response)
            db.session.add(new_chat)
            db.session.commit()

    # Fetch all chat history from the database
    chat_history = ChatHistory.query.all()

    return render_template('chat.html', chat_history=chat_history)


if __name__ == '__main__':
    app.run(debug=True)
