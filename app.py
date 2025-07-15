from flask import Flask, render_template, request, jsonify
import uuid
import pandas as pd
from datetime import datetime
# # for patient data visualization
# from patients_database import PatientAppointmentDB 
# Import your existing chatbot
from chatbot import AppointBot  # Your existing chatbot class

app = Flask(__name__)

# Initialize the chatbot
bot = AppointBot()


# Simple in-memory storage for conversations (resets on server restart)
conversations = {}

@app.route('/')
def index():
    """Main chat interface."""
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        # Get user message
        user_message = request.json.get('message', '').strip()
        conversation_id = request.json.get('conversation_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get bot response
        bot_response = bot.chat(user_message, conversation_id)
        
        # Store conversation (optional)
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        conversations[conversation_id].append({
            'user': user_message,
            'bot': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'response': bot_response,
            'conversation_id': conversation_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/new_chat', methods=['POST'])
def new_chat():
    """Start a new conversation."""
    conversation_id = str(uuid.uuid4())
    welcome_message = "Hi! Welcome to our Doctor Appointment Booking Service. How can I help you today?"
    
    return jsonify({
        'response': welcome_message,
        'conversation_id': conversation_id,
        'timestamp': datetime.now().isoformat()
    })

# appointments window
@app.route('/appointments')
def view_appointments():
    """View all patient appointments."""
    try:
        # Get all appointments from the database
        df = pd.read_csv("./data/patients.csv")
        # Convert to DataFrame for easier handling
        if not df.empty:
            # df = pd.DataFrame(appointments)
            # Sort by appointment date
            appointments_df = df.sort_values('appointment_date', ascending=False)
            appointments_data = appointments_df.to_dict('records')
        else:
            appointments_data = []
        
        return render_template('appointments.html', 
                             appointments=appointments_data,
                             total_count=len(appointments_data))
    
    except Exception as e:
        return render_template('appointments.html', 
                             appointments=[], 
                             error=str(e),
                             total_count=0)
    
@app.route('/appointments/filter')
def filter_appointments():
    """Filter appointments by status, date, or doctor."""
    try:
        # Get filter parameters
        status = request.args.get('status', 'all')
        date = request.args.get('date', '')
        doctor = request.args.get('doctor', '')
        
        # Get all appointments
        df = pd.read_csv("./data/patients.csv")
        
        if not df.empty:
            # df = pd.DataFrame(appointments)
            
            # Apply filters
            if status != 'all':
                df = df[df['status'] == status]
            
            if date:
                df = df[df['appointment_date'] == date]
            
            if doctor:
                df = df[df['doctor_name'].str.contains(doctor, case=False, na=False)]
            
            # Sort by appointment date
            df = df.sort_values('appointment_date', ascending=False)
            filtered_appointments = df.to_dict('records')
        else:
            filtered_appointments = []
        
        return jsonify({
            'appointments': filtered_appointments,
            'count': len(filtered_appointments)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @app.route('/appointments/<int:appointment_id>')
# def view_appointment_details(appointment_id):
#     """View detailed information for a specific appointment."""
#     try:
#         # Get all appointments and find the specific one
#         appointments = patient_db.get_all_appointments()
#         appointment = None
        
#         for appt in appointments:
#             if appt['appointment_id'] == appointment_id:
#                 appointment = appt
#                 break
        
#         if not appointment:
#             return render_template('appointment_detail.html', 
#                                  appointment=None, 
#                                  error="Appointment not found")
        
#         return render_template('appointment_detail.html', 
#                              appointment=appointment)
    
#     except Exception as e:
#         return render_template('appointment_detail.html', 
#                              appointment=None, 
#                              error=str(e))




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
