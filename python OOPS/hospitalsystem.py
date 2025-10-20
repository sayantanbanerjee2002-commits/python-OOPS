from datetime import datetime
from typing import List, Dict, Optional

class Person:
  # represent person class with shared attributes
    def __init__(self, name: str, age: int, contact: str, address: str): # Intialize a person object with shared attributes
        self.name = name
        self.age = age
        self.contact = contact
        self.address = address
    
    def __str__(self):
        """String representation of Person"""
        return f"{self.name}, Age: {self.age}, Contact: {self.contact}"


# DOCTOR CLASS (Inherits from Person)

class Doctor(Person): # Represeent Doctor class which is inherit from person class
  
    all_doctors = [] # Class variable to store available doctors
    
    def __init__(self, name: str, age: int, contact: str, address: str, 
                 specialization: str, consultation_fee: float):
    # intialize  new doctor object with extra attributes Specialization, Consultation_fee
        # Call parent class constructor
        super().__init__(name, age, contact, address)
        
        self.specialization = specialization
        self.consultation_fee = consultation_fee
        self.available_slots = {}  # Dictionary: {date: [time_slots]}
        
        # Add this doctor to class-level list
        Doctor.all_doctors.append(self)
    
    def add_available_slot(self, date: str, time: str): # method to determine available Slots for doctors with extra attributes date,time
      
        if date not in self.available_slots:
            self.available_slots[date] = []
        
        if time not in self.available_slots[date]:
            self.available_slots[date].append(time)
            print(f" Slot added: Dr. {self.name} available on {date} at {time}")
    
    def is_available(self, date: str, time: str):
      # Method to check if doctor is available or not
        return date in self.available_slots and time in self.available_slots[date]
    
    def remove_slot(self, date: str, time: str): # Remove a time slot (when appointment is booked)
        if date in self.available_slots and time in self.available_slots[date]:
            self.available_slots[date].remove(time)
    
    @staticmethod
    def find_available_doctors(specialization: str) -> List['Doctor']:
    # Static method to find Specialization of doctors and return the list of Doctors with matching Specialization
        matching_doctors = []
        for doctor in Doctor.all_doctors:
            if doctor.specialization.lower() == specialization.lower():
                matching_doctors.append(doctor)
        return matching_doctors
    
    def __str__(self): # Method for readable string of matching doctors
        return f"Dr. {self.name} - {self.specialization} (Fee: ${self.consultation_fee})"


class MedicalRecord: # Reperesent Medical record Class which stores each patient's history
   
    def __init__(self): # Intialize empty Medical Records
        self.records = []  # List of dictionaries
    
    def add_entry(self, date: str, diagnosis: str, treatment: str, medications: List[str]):
    # Add a new mediacal entry with attributes date, diagnosis, treatment,medications
        entry = {
            'date': date,
            'diagnosis': diagnosis,
            'treatment': treatment,
            'medications': medications
        }
        self.records.append(entry)
        print(f" Medical record added for {date}")
    
    def get_history(self):
        """Return complete medical history"""
        return self.records
    
    def __str__(self):
        if not self.records:
            return "No medical history available"
        
        history = "Medical History:\n"
        for i, record in enumerate(self.records, 1):
            history += f"\n{i}. Date: {record['date']}\n"
            history += f"   Diagnosis: {record['diagnosis']}\n"
            history += f"   Treatment: {record['treatment']}\n"
            history += f"   Medications: {', '.join(record['medications'])}\n"
        return history


class Patient(Person): # Represents Patient class of hospital inherit from person class
  
    all_patients = [] # class variable shared by all instance
    patient_counter = 1000  # Start patient IDs from 1000
    
    def __init__(self, name: str, age: int, contact: str, address: str, 
                 insurance_coverage: float = 0.0):
     # Intialize patient object with extra attribute patient_id, insurance coverage
        super().__init__(name, age, contact, address)
        
        # Generate unique patient ID
        self.patient_id = f"P{Patient.patient_counter}"
        Patient.patient_counter += 1
        
        self.insurance_coverage = insurance_coverage
        
        # COMPOSITION: Patient HAS-A MedicalRecord
        self.medical_history = MedicalRecord()
        
        # COMPOSITION: Patient HAS-MANY Appointments
        self.appointments = []
        
        # Add to class-level list
        Patient.all_patients.append(self)
    
    def add_appointment(self, appointment: 'Appointment'):
        """Add an appointment to patient's list"""
        self.appointments.append(appointment)
    
    def get_appointments(self) -> List['Appointment']:
        """Return all appointments for this patient"""
        return self.appointments
    
    def __str__(self):
        return f"Patient {self.patient_id}: {self.name} (Insurance: {self.insurance_coverage*100}%)"



class Appointment: # represent appointment class ,inherit from Person Class
    # Class variable to store all appointments
    all_appointments = []
    appointment_counter = 1
    
    def __init__(self, doctor: Doctor, patient: Patient, date: str, time: str):
      # intialize a new appointment 
        self.appointment_id = f"APT{Appointment.appointment_counter}"
        Appointment.appointment_counter += 1
        
        self.doctor = doctor
        self.patient = patient
        self.date = date
        self.time = time
        self.status = "Scheduled"  # Scheduled, Completed, Cancelled
        self.diagnosis = None
        
        # CONFLICT CHECKING: Verify doctor is available
        if not doctor.is_available(date, time):
            raise ValueError(f" Doctor {doctor.name} is not available on {date} at {time}")
        
        # Remove the slot from doctor's availability
        doctor.remove_slot(date, time)
        
        # Add appointment to both doctor and patient
        patient.add_appointment(self)
        
        # Add to class-level list
        Appointment.all_appointments.append(self)
        
        print(f" Appointment {self.appointment_id} created: {patient.name} with Dr. {doctor.name}")
    
    def complete_appointment(self, diagnosis: str, treatment: str, medications: List[str]):
      # Method for complete appointment
        self.status = "Completed"
        self.diagnosis = diagnosis
        
        # Add to patient's medical history
        self.patient.medical_history.add_entry(
            self.date, diagnosis, treatment, medications
        )
        
        print(f" Appointment {self.appointment_id} completed")
    
    def cancel_appointment(self):
        """Cancel the appointment and restore doctor's availability"""
        self.status = "Cancelled"
        self.doctor.add_available_slot(self.date, self.time)
        print(f" Appointment {self.appointment_id} cancelled")
    
    def __str__(self):
        return (f"Appointment {self.appointment_id}: {self.patient.name} with "
                f"Dr. {self.doctor.name} on {self.date} at {self.time} [{self.status}]")

class Bill: # Represent Bill class with medical insurrande calculation
    all_bills = []
    bill_counter = 1
    
    def __init__(self, patient: Patient, appointment: Appointment):
     # create a bill for patient's appointment
        self.bill_id = f"BILL{Bill.bill_counter}"
        Bill.bill_counter += 1
        
        self.patient = patient
        self.appointment = appointment
        self.services_list = []  # List of (service_name, cost) tuples
        self.total_amount = 0.0
        self.payment_status = "Pending"  # Pending, Paid, Partially Paid
        self.insurance_claim = 0.0
        self.patient_pays = 0.0
        
        # Add consultation fee automatically
        self.add_service("Consultation", appointment.doctor.consultation_fee)
        
        Bill.all_bills.append(self)
    
    def add_service(self, service_name: str, cost: float): # add service to the bill
      
        self.services_list.append((service_name, cost))
        self.total_amount += cost
        self._calculate_insurance()
        print(f" Service added: {service_name} - ${cost}")
    
    def _calculate_insurance(self): # method to calculate insurance for patients , total paid bill
        self.insurance_claim = self.total_amount * self.patient.insurance_coverage
        self.patient_pays = self.total_amount - self.insurance_claim
    
    def mark_paid(self):
        """Mark bill as paid"""
        self.payment_status = "Paid"
        print(f" Bill {self.bill_id} marked as paid")
    
    def get_bill_summary(self) -> str: # Generate detailed bill summary
        summary = f"\n{'='*50}\n"
        summary += f"BILL #{self.bill_id}\n"
        summary += f"{'='*50}\n"
        summary += f"Patient: {self.patient.name} ({self.patient.patient_id})\n"
        summary += f"Doctor: Dr. {self.appointment.doctor.name}\n"
        summary += f"Date: {self.appointment.date}\n\n"
        
        summary += "Services:\n"
        for service, cost in self.services_list:
            summary += f"  - {service}: ${cost:.2f}\n"
        
        summary += f"\n{'='*50}\n"
        summary += f"Total Amount: ${self.total_amount:.2f}\n"
        summary += f"Insurance Coverage ({self.patient.insurance_coverage*100}%): -${self.insurance_claim:.2f}\n"
        summary += f"{'='*50}\n"
        summary += f"PATIENT PAYS: ${self.patient_pays:.2f}\n"
        summary += f"{'='*50}\n"
        summary += f"Payment Status: {self.payment_status}\n"
        
        return summary
    
    def __str__(self):
        return f"Bill {self.bill_id}: ${self.total_amount:.2f} ({self.payment_status})"

class Hospital: # Represent Hospital class 
    
    @classmethod
    def total_patients_report(cls) -> str: # Class method to represents total paitent reports
        total = len(Patient.all_patients)
        report = f"\n{'='*50}\n"
        report += f"TOTAL PATIENTS REPORT\n"
        report += f"{'='*50}\n"
        report += f"Total Registered Patients: {total}\n"
        
        if total > 0:
            report += "\nPatient List:\n"
            for patient in Patient.all_patients:
                report += f"  - {patient}\n"
        
        return report
    
    @classmethod
    def revenue_report(cls) -> str: # Class method to generate revenue report
        total_revenue = sum(bill.total_amount for bill in Bill.all_bills)
        total_collected = sum(bill.patient_pays for bill in Bill.all_bills 
                            if bill.payment_status == "Paid")
        total_pending = sum(bill.patient_pays for bill in Bill.all_bills 
                          if bill.payment_status == "Pending")
        
        report = f"\n{'='*50}\n"
        report += f"REVENUE REPORT\n"
        report += f"{'='*50}\n"
        report += f"Total Bills Generated: {len(Bill.all_bills)}\n"
        report += f"Total Revenue (Gross): ${total_revenue:.2f}\n"
        report += f"Amount Collected: ${total_collected:.2f}\n"
        report += f"Amount Pending: ${total_pending:.2f}\n"
        report += f"{'='*50}\n"
        
        return report
    
    @classmethod
    def appointments_report(cls) -> str: # Class method to generate Appointment's report
        total = len(Appointment.all_appointments)
        completed = sum(1 for apt in Appointment.all_appointments if apt.status == "Completed")
        scheduled = sum(1 for apt in Appointment.all_appointments if apt.status == "Scheduled")
        cancelled = sum(1 for apt in Appointment.all_appointments if apt.status == "Cancelled")
        
        report = f"\n{'='*50}\n"
        report += f"APPOINTMENTS REPORT\n"
        report += f"{'='*50}\n"
        report += f"Total Appointments: {total}\n"
        report += f"  - Completed: {completed}\n"
        report += f"  - Scheduled: {scheduled}\n"
        report += f"  - Cancelled: {cancelled}\n"
        report += f"{'='*50}\n"
        
        return report

# DEMONSTRATION CODE

def main():
    """
    Main function demonstrating the hospital system.
    """
    print("\n" + "="*60)
    print("HOSPITAL MANAGEMENT SYSTEM DEMO")
    print("="*60 + "\n")
    
    # Create Doctors
    print(">>> Creating Doctors...")
    dr_ghosh = Doctor("Dabu Ghosh", 45, "555-1001", "125 Medical St", 
                     "Cardiology", 500.0)
    dr_banerjee = Doctor("Sayantan Banerjee", 40, "555-1002", "456 Health Ave", 
                     "Pediatrics", 550.0)
    dr_halder = Doctor("Prasun Halder", 42, "555-1003", "789 Care Blvd", 
                     "Cardiology", 450.0)
    
    # Add available slots for doctors
    print("\n>>> Adding Doctor Availability...")
    dr_ghosh.add_available_slot("2025-10-25", "09:00")
    dr_ghosh.add_available_slot("2025-10-25", "10:00")
    dr_ghosh.add_available_slot("2025-10-25", "14:00")
    dr_banerjee.add_available_slot("2025-10-25", "09:00")
    dr_banerjee.add_available_slot("2025-12-26", "11:00")
    
    # Create Patients
    print("\n>>> Registering Patients...")
    patient1 = Patient("Dipesh", 35, "555-2001", "321 Patient Rd", 
                      insurance_coverage=0.8)  # 80% coverage
    patient2 = Patient("Bob", 28, "555-2002", "654 Client St", 
                      insurance_coverage=0.5)  # 50% coverage
    patient3 = Patient("Baban", 42, "555-2003", "987 Visit Lane", 
                      insurance_coverage=0.0)  # No insurance
    
    # Find doctors by specialization (Static Method)
    print("\n>>> Finding Cardiologists...")
    cardiologists = Doctor.find_available_doctors("Cardiology")
    print(f"Found {len(cardiologists)} cardiologist(s):")
    for doc in cardiologists:
        print(f"  - {doc}")
    
    # Create Appointments
    print("\n>>> Scheduling Appointments...")
    try:
        apt1 = Appointment(dr_ghosh, patient1, "2025-10-25", "09:00")
        apt2 = Appointment(dr_banerjee, patient2, "2025-10-25", "09:00")
        apt3 = Appointment(dr_ghosh, patient3, "2025-10-25", "10:00")
    except ValueError as e:
        print(e)
    
    # Try to create conflicting appointment (should fail)
    print("\n>>> Testing Conflict Detection...")
    try:
        apt_conflict = Appointment(dr_ghosh, patient2, "2025-10-25", "09:00")
    except ValueError as e:
        print(e)
    
    # Complete appointments with diagnosis
    print("\n>>> Completing Appointments...")
    apt1.complete_appointment(
        diagnosis="Hypertension",
        treatment="Prescribed blood pressure medication",
        medications=["Lisinopril 10mg", "Aspirin 81mg"]
    )
    
    apt2.complete_appointment(
        diagnosis="Common Cold",
        treatment="Rest and fluids recommended",
        medications=["Paracetamol 500mg"]
    )
    
    # Create Bills
    print("\n>>> Generating Bills...")
    bill1 = Bill(patient1, apt1)
    bill1.add_service("ECG Test", 100.0)
    bill1.add_service("Blood Pressure Monitoring", 50.0)
    
    bill2 = Bill(patient2, apt2)
    bill2.add_service("Throat Examination", 30.0)
    
    bill3 = Bill(patient3, apt3)
    bill3.add_service("Stress Test", 300.0)
    
    # Mark bills as paid
    bill1.mark_paid()
    bill2.mark_paid()
    
    # Display Bill Summaries
    print("\n>>> Bill Details...")
    print(bill1.get_bill_summary())
    print(bill2.get_bill_summary())
    print(bill3.get_bill_summary())
    
    # Display Medical History
    print("\n>>> Patient Medical History...")
    print(f"\n{patient1.name}'s Medical History:")
    print(patient1.medical_history)
    
    # Generate Reports (Class Methods)
    print("\n>>> Hospital Reports...")
    print(Hospital.total_patients_report())
    print(Hospital.appointments_report())
    print(Hospital.revenue_report())
    
    print("\n" + "="*60)
    print("DEMO COMPLETED")
    print("="*60 + "\n")


# Run the demonstration
if __name__ == "__main__":
    main()
