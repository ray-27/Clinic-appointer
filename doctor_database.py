import pandas as pd
import numpy as np
from langchain.tools import tool
from datetime import datetime, timedelta

def add_date(df):
    today = datetime.now().date()
    np.random.seed(42)  # Optional: for reproducible results
    random_days = np.random.choice([0, 1, 2], size=len(df))
    df['date'] = [(today + timedelta(days=int(day))).strftime('%Y-%m-%d') for day in random_days]

class DocDB:
    def __init__(self,data_file="./data/doctor.csv"):
        self.df = pd.read_csv(data_file)
        add_date(self.df) #adds the date available

        # self.history = []

    def get_doctors_by_specialty(self, specialty: str):
        """
        Retrieve all doctors who specialize in a specific medical field.

        This function searches the doctors database (CSV) to find all healthcare 
        providers who practice in the specified medical specialty. It's commonly
        used in the appointment booking workflow after symptoms have been analyzed
        and mapped to an appropriate medical department.

        Args:
            specialty (str): The medical specialty to search for.
        
        Returns:
            list: A list of dictionaries containing doctor information. Each dictionary includes the following keys:
                - doctor_id (str): Unique identifier for the doctor
                - doctor_name (str): Full name of the doctor
                - date (str): Date available for appointment
                - slot_timing (str): Days when doctor is available
        """
        filtered = self.df[
            (self.df['speciality'].str.lower() == specialty.lower()) & 
            (self.df['is_booked'] == False)
        ]
    
        # Convert filtered results to list of dictionaries
        doctors_list = []
        for _, row in filtered.iterrows():
            doctors_list.append({
                'doctor_id': row.get('doctor_id', ''),
                'doctor_name': row.get('doctor_name', ''),
                'date': row.get('date', ''),
                'slot_timing': row.get('slot_timing', '')
            })

        return doctors_list

    def book_doctor_appointment(self, doctor_id: int):
        """
        Books the slot with the doctor having the doctor id.

        This funciton will book the appointment by changing the is_booked column to True, this will require the doctor it with which the user
        wants to book the appontment with

        Args:
            doctor_id (int): The id to do the booking to
        
        Returns:
            list: A list of dictionaries containing doctor information. Each dictionary includes the following keys:
                - doctor_id (str): Unique identifier for the doctor
                - doctor_name (str): Full name of the doctor
                - date (str): Date available for appointment
                - slot_timing (str): Days when doctor is available
        """        

        mask_available = (
            (self.df['doctor_id'] == doctor_id) &
            (self.df['is_booked'] == False)
        )

        if not mask_available.any():
            # Either ID not found or slot already booked
            return []
        
        # 2️⃣ mark the slot as booked
        self.df.loc[mask_available, 'is_booked'] = True

        booked_row = self.df[self.df['doctor_id'] == doctor_id]
        booked_info = {
            'doctor_id'  : str(booked_row.get('doctor_id', '')),
            'doctor_name': booked_row.get('doctor_name', ''),
            'date'       : booked_row.get('date', ''),
            'slot_timing': booked_row.get('slot_timing', '')
        }

        return booked_info

    def check_doctor_availability(self, doctor_id: int = None, specialty: str = None, date: str = None, slot_timing: str = None):
        """
        Check availability of doctors based on various filter criteria.
        
        This function searches the doctors database to find available appointment slots
        based on the provided filter criteria. It can be used to check availability
        for a specific doctor, specialty, date, or time slot combination. The function
        is commonly used before booking appointments to present available options to users.
        
        Args:
            doctor_id (int, optional): Specific doctor's unique identifier to check availability for.
                                    If provided, will check only this doctor's availability.
            specialty (str, optional): Medical specialty to filter by (e.g., "Cardiology", 
                                    "Dermatology", "General Medicine"). Case-insensitive matching.
            date (str, optional): Specific date to check availability for in YYYY-MM-DD format
                                (e.g., "2024-01-15"). If not provided, checks all available dates.
            slot_timing (str, optional): Specific time slot to check 
        
        Returns:
            list: A list of dictionaries containing available doctor slots. Each dictionary 
                includes the following keys:
                - doctor_id (str): Unique identifier for the doctor
                - doctor_name (str): Full name of the doctor
                - specialty (str): Medical specialty of the doctor
                - date (str): Available date for appointment
                - slot_timing (str): Available time slot
                - is_booked (bool): Booking status (always False for available slots)
                
                Returns empty list if no available slots match the criteria.
        
        Raises:
            ValueError: If date is provided in incorrect format (not YYYY-MM-DD)
            TypeError: If doctor_id is not an integer when provided
        
        Examples:
            # Check all available slots
             all_available = doc_db.check_doctor_availability()
             len(all_available)
            15
            
            # Check specific doctor availability
             doctor_123_slots = doc_db.check_doctor_availability(doctor_id=123)
             print(doctor_123_slots)
            [{'doctor_id': '123', 'doctor_name': 'Dr. Smith', 'specialty': 'Cardiology', 
            'date': '2024-01-15', 'slot_timing': '09:00-10:00', 'is_booked': False}]
            
            # Check by specialty
             cardiology_slots = doc_db.check_doctor_availability(specialty="Cardiology")
             len(cardiology_slots)
            5
            
            # Check specific date availability
             today_slots = doc_db.check_doctor_availability(date="2024-01-15")
             len(today_slots)
            8
            
            # Check combination of filters
             specific_slots = doc_db.check_doctor_availability(
                 specialty="Dermatology", 
                 date="2024-01-16", 
                 slot_timing="morning"
             )
             len(specific_slots)
            2
        
        Note:
            - All filters are optional and can be combined for more specific searches
            - The function only returns slots where is_booked = False
            - Specialty matching is case-insensitive
            - Date format must be YYYY-MM-DD if provided
            - If no filters are provided, returns all available slots in the system
            - Results are not sorted by default - consider adding sorting if needed
        """
        
        # Input validation
        if doctor_id is not None and not isinstance(doctor_id, int):
            raise TypeError("doctor_id must be an integer")
        
        if date is not None:
            try:
                # Validate date format
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                raise ValueError("date must be in YYYY-MM-DD format")
        
        # Start with base condition: only available slots
        conditions = [self.df['is_booked'] == False]
        
        # Add optional filters
        if doctor_id is not None:
            conditions.append(self.df['doctor_id'] == doctor_id)
        
        if specialty is not None:
            conditions.append(self.df['specialty'].str.lower() == specialty.lower())
        
        if date is not None:
            conditions.append(self.df['date'] == date)
        
        if slot_timing is not None:
            conditions.append(self.df['slot_timing'] == slot_timing)
        
        # Combine all conditions using & operator
        combined_mask = conditions[0]
        for condition in conditions[1:]:
            combined_mask = combined_mask & condition
        
        # Filter the dataframe
        available_slots = self.df[combined_mask]
        
        # Convert to list of dictionaries
        availability_list = []
        for _, row in available_slots.iterrows():
            availability_list.append({
                'doctor_id': str(row.get('doctor_id', '')),
                'doctor_name': row.get('doctor_name', ''),
                'specialty': row.get('specialty', ''),
                'date': row.get('date', ''),
                'slot_timing': row.get('slot_timing', ''),
                'is_booked': row.get('is_booked', False)
            })
        
        return availability_list



doc = DocDB()
TOOLS = [
    doc.get_doctors_by_specialty,
    doc.book_doctor_appointment,
    doc.check_doctor_availability
]


if __name__ == "__main__":
    doc = DocDB()
    # car = doc.get_doctors_by_specialty("Gastroenterology")
    book = doc.book_doctor_appointment(1)
    print(book)
