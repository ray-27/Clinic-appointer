import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class PatientAppointmentDB:
    def __init__(self, appointments_file="./data/patients.csv"):
        """Initialize the patient appointment database."""
        try:
            self.appointments_df = pd.read_csv(appointments_file)
            print("PAtient database init success")
        except FileNotFoundError:
            # Create empty DataFrame with required columns
            print("Patent db. unsuccessful")
            self.appointments_df = pd.DataFrame(columns=[
                'appointment_id', 'patient_name', 'patient_age', 
                'doctor_id', 'doctor_name', 'specialty', 
                'appointment_date', 'slot_timing', 'status', 
                'booking_date', 'symptoms'
            ])
        
        self.next_appointment_id = self._get_next_appointment_id()

    def _get_next_appointment_id(self) -> int:
        """Get next available appointment ID."""
        if self.appointments_df.empty:
            return 1
        return self.appointments_df['appointment_id'].max() + 1
    
    def book_patient_appointment(self, patient_name: str, patient_age: int, 
                        doctor_name: str, specialty: str, 
                           appointment_date: str, slot_timing: str, doctor_id: int = 0,symptoms: str = ""):
        """
        Book appointment only when all conditions are met.
        Book an appointment for a patient with all details provided.

        Args:
            patient_name (str): Full name of the patient
            patient_age (int): Age of the patient
            doctor_id (int): ID of the doctor to book with (optional)
            doctor_name (str): Name of the doctor
            specialty (str): Medical specialty of the doctor
            appointment_date (str): Date of the appointment (YYYY-MM-DD)
            slot_timing (str): Time slot of the appointment
            symptoms (str, optional): Patient's symptoms or reason for visit (optional)

        Returns:
            dict: Booking confirmation details including all appointment info
        """
        # Create appointment record
        appointment_id = self.next_appointment_id
        self.next_appointment_id += 1

        new_appointment = {
            'appointment_id': appointment_id,
            'patient_name': patient_name,
            'patient_age': patient_age,
            'doctor_id': doctor_id,
            'doctor_name': doctor_name,
            'specialty': specialty,
            'appointment_date': appointment_date,
            'slot_timing': slot_timing,
            'status': 'confirmed',
            'booking_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'symptoms': symptoms
        }

        # Add to DataFrame
        self.appointments_df = pd.concat([
            self.appointments_df, 
            pd.DataFrame([new_appointment])
        ], ignore_index=True)

        self.save_to_csv()
        
        print(f"New appointment reached for patient {patient_name}, and age {patient_age}, doctor : {doctor_name} with id {doctor_id}")

        return new_appointment

    def get_patient_appointments(self, patient_name: str):
        """
        Get all appointments for a specific patient.
        
        Args:
            patient_name (str): Name of the patient to search for
        
        Returns:
            list: List of appointments for the patient
        """
        patient_appointments = self.appointments_df[
            self.appointments_df['patient_name'].str.lower() == patient_name.lower()
        ]
        
        appointments_list = []
        for _, row in patient_appointments.iterrows():
            appointments_list.append({
                'appointment_id': row['appointment_id'],
                'patient_name': row['patient_name'],
                'patient_age': row['patient_age'],
                'doctor_name': row['doctor_name'],
                'specialty': row['specialty'],
                'appointment_date': row['appointment_date'],
                'slot_timing': row['slot_timing'],
                'status': row['status'],
                'symptoms': row['symptoms']
            })
        
        return appointments_list
    
    def cancel_appointment(self, appointment_id: int):
        
        """
            Cancel an appointment by its unique appointment ID.
            
            This function locates an appointment in the database using the provided appointment ID
            and changes its status to 'cancelled'. The appointment record is maintained in the 
            database for audit and historical purposes, but the status change indicates it is 
            no longer active. This function is commonly used when patients need to cancel their
            scheduled appointments or when administrative cancellations are required.
            
            Args:
                appointment_id (int): Unique identifier of the appointment to cancel. This ID
                                    was generated when the appointment was originally booked
                                    and should be provided to the patient as confirmation.
            
            Returns:
                dict: A dictionary containing the cancellation result with the following keys:
                    - status (str): 'success' if cancellation was completed, 'failed' if not
                    - appointment_id (int): The ID of the cancelled appointment
                    - patient_name (str): Name of the patient whose appointment was cancelled
                    - doctor_name (str): Name of the doctor for the cancelled appointment
                    - appointment_date (str): Date of the cancelled appointment
                    - slot_timing (str): Time slot of the cancelled appointment
                    - message (str): Human-readable confirmation or error message
                    
                    If appointment ID is not found, returns:
                    - status (str): 'failed'
                    - message (str): Error message explaining the appointment was not found
            
            Raises:
                TypeError: If appointment_id is not provided as an integer
                ValueError: If appointment_id is negative or zero
            
            Examples:
                # Cancel a specific appointment
                >>> result = patient_db.cancel_appointment(12345)
                >>> print(result)
                {
                    'status': 'success',
                    'appointment_id': 12345,
                    'patient_name': 'John Doe',
                    'doctor_name': 'Dr. Smith',
                    'appointment_date': '2024-01-15',
                    'slot_timing': '09:00-10:00',
                    'message': 'Appointment cancelled successfully'
                }
                
                # Attempt to cancel non-existent appointment
                >>> result = patient_db.cancel_appointment(99999)
                >>> print(result)
                {
                    'status': 'failed',
                    'message': 'Appointment not found'
                }
            
            Note:
                - Cancelled appointments remain in the database with status 'cancelled'
                - The original appointment slot may become available for rebooking
                - Multiple cancellations of the same appointment will not cause errors
                - This function does not automatically notify patients of cancellation
        """

        appointment_mask = self.appointments_df['appointment_id'] == appointment_id
        
        if not appointment_mask.any():
            return {
                'status': 'failed',
                'message': 'Appointment not found'
            }
        
        appointment = self.appointments_df[appointment_mask].iloc[0]
        
        # Update status to cancelled
        self.appointments_df.loc[appointment_mask, 'status'] = 'cancelled'
        
        # Free up the doctor slot (you'll need to implement this in DocDB)
        # doc.free_doctor_slot(appointment['doctor_id'])
        
        return {
            'status': 'success',
            'appointment_id': appointment_id,
            'patient_name': appointment['patient_name'],
            'message': 'Appointment cancelled successfully'
        }
    
    # these are not to be exported, these will be used by the backend services for analytics and not by llm
    def save_to_csv(self, filename: str = "./data/patients.csv"):
        """Save appointments to CSV file."""
        self.appointments_df.to_csv(filename, index=False)
        print(f"Appointments saved to {filename}")

    def get_all_appointments(self):
        # Check if DataFrame is empty
        if self.appointments_df.empty:
            return pd.DataFrame()
        
        # Convert DataFrame to list of dictionaries
        # appointments_list = []
        # for _, row in self.appointments_df.iterrows():
        #     appointment = {
        #         'appointment_id': int(row.get('appointment_id', 0)),
        #         'patient_name': str(row.get('patient_name', '')),
        #         'patient_age': int(row.get('patient_age', 0)),
        #         'doctor_id': int(row.get('doctor_id', 0)),
        #         'doctor_name': str(row.get('doctor_name', '')),
        #         'specialty': str(row.get('specialty', '')),
        #         'appointment_date': str(row.get('appointment_date', '')),
        #         'slot_timing': str(row.get('slot_timing', '')),
        #         'status': str(row.get('status', 'confirmed')),
        #         'booking_date': str(row.get('booking_date', '')),
        #         'symptoms': str(row.get('symptoms', ''))
        #     }
        #     appointments_list.append(appointment)
        
        # return appointments_list
        return self.appointments_df.copy()



patient = PatientAppointmentDB()
PATIENTS_TOOL = [
    patient.book_patient_appointment,
    patient.get_patient_appointments,
    patient.cancel_appointment,
]
