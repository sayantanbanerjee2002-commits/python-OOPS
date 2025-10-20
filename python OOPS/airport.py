from datetime import datetime, timedelta
from typing import List, Optional

class Aircraft:
    """Represents an airplane with its specifications"""
    
    def __init__(self, aircraft_id: str, model: str, manufacturer: str, 
                 seat_capacity: dict, fuel_capacity: float):
        #  Initialize an aircraft
        self.model = model
        self.manufacturer = manufacturer
        self.seat_capacity = seat_capacity  # How many seats in each class
        self.fuel_capacity = fuel_capacity
        self._current_status = "Available"  # Can be: Available, In-Flight, Maintenance
    
    # Property decorator makes this read-only from outside
    @property
    def current_status(self):
        """Get the current status of aircraft"""
        return self._current_status
    
    def set_status(self, status: str):
        """Change aircraft status (only through this method)"""
        valid_statuses = ["Available", "In-Flight", "Maintenance"]
        if status in valid_statuses:
            self._current_status = status
        else:
            print(f"Invalid status! Must be one of {valid_statuses}")
    
    def __str__(self):
        return f"{self.manufacturer} {self.model} ({self.aircraft_id})"

class Airport:
    """Represents an airport with its details"""
    
    def __init__(self, airport_code: str, name: str, city: str, 
                 country: str, runways: int, terminals: int):
        """Initialize an airport (like CCU for Kolkata)"""
        self.airport_code = airport_code  # Unique Airport code for different airport
        self.name = name
        self.city = city
        self.country = country
        self.runways = runways
        self.terminals = terminals
    
    def __str__(self): # redability for Airport class 
        return f"{self.name} ({self.airport_code}), {self.city}"

class Passenger:
    """Represents a person traveling"""
    
    def __init__(self, passenger_id: str, name: str, passport_number: str, 
                 baggage_weight: float):
        """Initialize a passenger"""
        self.passenger_id = passenger_id
        self.name = name
        self.passport_number = passport_number
        self.baggage_weight = baggage_weight  # In kg
        self.seat_number = None  # Assigned later during check-in
        self.checked_in = False
    
    def calculate_baggage_fee(self) -> float:
        """
        Calculate extra baggage charges
        Free allowance: 15 kg
        Extra charge: $10 per kg over 15 kg
        """
        free_allowance = 15
        if self.baggage_weight <= free_allowance:
            return 0.0
        else:
            extra_weight = self.baggage_weight - free_allowance
            return extra_weight * 10
    
    def __str__(self):
        return f"{self.name} (Passport: {self.passport_number})"
    
class Booking:
    """Represents a ticket booking"""
    
    # Class variable to generate unique booking IDs
    booking_counter = 1000
    
    def __init__(self, passenger: Passenger, flight: 'Flight', 
                 class_type: str, meal_preference: str = "Vegetarian"):
        """Create a new booking"""
        self.booking_id = f"BK{Booking.booking_counter}"
        Booking.booking_counter += 1
        
        self.passenger = passenger
        self.flight = flight
        self.class_type = class_type.lower()  # economy, business, first
        self.meal_preference = meal_preference
        self.booking_status = "Confirmed"  # Can be: Confirmed, Cancelled, Waitlisted
    
    def cancel_booking(self):
        """Cancel this booking"""
        self.booking_status = "Cancelled"
        print(f"Booking {self.booking_id} has been cancelled.")
    
    def __str__(self):
        return (f"Booking {self.booking_id}: {self.passenger.name} on "
                f"{self.flight.flight_number} ({self.class_type} class)")

class Flight:
    """Represents a flight from one airport to another"""
    
    def __init__(self, flight_number: str, airline: str, origin: Airport, 
                 destination: Airport, departure_time: datetime, 
                 arrival_time: datetime, aircraft: Aircraft):
        """Initialize a flight"""
        self.flight_number = flight_number
        self.airline = airline
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.aircraft = aircraft  # Composition: Flight HAS-A Aircraft
        
        # Track passengers on this flight
        self.passengers: List[Passenger] = []
        self.bookings: List[Booking] = []
        
        # Seat availability by class
        self.available_seats = aircraft.seat_capacity.copy()
        
        # Waiting list for each class
        self.waiting_list = {
            'economy': [],
            'business': [],
            'first': []
        }
        
        # Flight status
        self._status = "Scheduled"  # Scheduled, Boarding, Departed, Delayed, Cancelled
        self.delay_time = timedelta(0)  # No delay initially
    
    @property
    def status(self):
        """Read-only status property"""
        return self._status
    
    def add_booking(self, booking: Booking) -> bool:
        """
        Try to add a booking to this flight
        Returns True if successful, False if flight is full
        """
        class_type = booking.class_type
        
        # Check if seats are available in requested class
        if self.available_seats[class_type] > 0:
            self.bookings.append(booking)
            self.passengers.append(booking.passenger)
            self.available_seats[class_type] -= 1
            print(f"  Booking confirmed for {booking.passenger.name} in {class_type} class")
            return True
        else:
            # Add to waiting list
            self.waiting_list[class_type].append(booking)
            booking.booking_status = "Waitlisted"
            print(f"  No seats available in {class_type}. Added to waiting list.")
            return False
    
    def check_in_passenger(self, passenger: Passenger, seat_number: str):
        """Check in a passenger and generate boarding pass"""
        if passenger not in self.passengers:
            print(f"Error: {passenger.name} is not booked on this flight!")
            return None
        
        # Assign seat
        passenger.seat_number = seat_number
        passenger.checked_in = True
        
        # Generate boarding pass
        boarding_pass = self._generate_boarding_pass(passenger)
        return boarding_pass
    
    def _generate_boarding_pass(self, passenger: Passenger) -> str:
        """Generate a boarding pass (private method)"""
        baggage_fee = passenger.calculate_baggage_fee()
        
        boarding_pass = f"""
       
        Flight: {self.flight_number} | {self.airline}
        
        Passenger: {passenger.name}
        Passport: {passenger.passport_number}
        
        From: {self.origin.city} ({self.origin.airport_code})
        To: {self.destination.city} ({self.destination.airport_code})
        
        Departure: {self.departure_time.strftime('%d-%b-%Y %H:%M')}
        Seat: {passenger.seat_number}
        
        Baggage: {passenger.baggage_weight} kg
        Baggage Fee: ${baggage_fee:.2f}
        
        Status: {self._status}
      
        """
        return boarding_pass
    
    def delay_flight(self, delay_minutes: int, reason: str):
        """Delay the flight and notify passengers"""
        self.delay_time = timedelta(minutes=delay_minutes)
        self.departure_time += self.delay_time
        self.arrival_time += self.delay_time
        self._status = "Delayed"
        
        # Notify all passengers
        print(f"\n FLIGHT DELAY NOTIFICATION ⚠")
        print(f"Flight {self.flight_number} is delayed by {delay_minutes} minutes")
        print(f"Reason: {reason}")
        print(f"New departure time: {self.departure_time.strftime('%d-%b-%Y %H:%M')}")
        print(f"\nNotifying {len(self.passengers)} passengers...")
        
        for passenger in self.passengers:
            print(f"  → SMS sent to {passenger.name}")
    
    def get_flight_info(self) -> str:
        """Get complete flight information"""
        total_passengers = len(self.passengers)
        total_capacity = sum(self.aircraft.seat_capacity.values())
        
        info = f"""
        Flight Information:
        -------------------
        Flight Number: {self.flight_number}
        Airline: {self.airline}
        Aircraft: {self.aircraft}
        
        Route: {self.origin.city} → {self.destination.city}
        Departure: {self.departure_time.strftime('%d-%b-%Y %H:%M')}
        Arrival: {self.arrival_time.strftime('%d-%b-%Y %H:%M')}
        Status: {self._status}
        
        Passengers: {total_passengers}/{total_capacity}
        Available Seats:
          - Economy: {self.available_seats['economy']}
          - Business: {self.available_seats['business']}
          - First Class: {self.available_seats['first']}
        """
        return info
    
    def __str__(self):
        return f"{self.flight_number}: {self.origin.airport_code} → {self.destination.airport_code}"


class FlightScheduler: # Helper Class
    """Manages all flights and checks for conflicts"""
    
    def __init__(self):
        self.flights: List[Flight] = []
    
    def add_flight(self, flight: Flight) -> bool:
        """Add a flight after checking for aircraft conflicts"""
        if self._check_aircraft_conflict(flight):
            print(f" Cannot schedule {flight.flight_number}: Aircraft conflict detected!")
            return False
        else:
            self.flights.append(flight)
            print(f" Flight {flight.flight_number} scheduled successfully")
            return True
    
    def _check_aircraft_conflict(self, new_flight: Flight) -> bool:
        """
        Check if the aircraft is already scheduled for another flight
        at the same time (conflict checker)
        """
        for existing_flight in self.flights:
            # Check if same aircraft
            if existing_flight.aircraft.aircraft_id == new_flight.aircraft.aircraft_id:
                # Check if time overlaps
                if self._times_overlap(existing_flight, new_flight):
                    return True  # Conflict found!
        return False  # No conflict
    
    def _times_overlap(self, flight1: Flight, flight2: Flight) -> bool:
        """Check if two flights' times overlap"""
        # Flight 1: [departure1 -------- arrival1]
        # Flight 2:           [departure2 -------- arrival2]
        # These overlap!
        
        return not (flight1.arrival_time <= flight2.departure_time or 
                    flight2.arrival_time <= flight1.departure_time)
    
    def get_all_flights(self):
        """Display all scheduled flights"""
        print("\n" + "="*50)
        print("ALL SCHEDULED FLIGHTS")
        print("="*50)
        for flight in self.flights:
            print(flight.get_flight_info())

def main():
    """Demo of the airport system"""
    
    print(" AIRPORT FLIGHT SCHEDULING SYSTEM 🛬\n")
    
    # Create airports
    kolkata = Airport("CCU", "Netaji Subhas Chandra Bose International Airport", 
                      "Kolkata", "India", 2, 2)
    delhi = Airport("DEL", "Indira Gandhi International Airport", 
                    "Delhi", "India", 3, 3)
    mumbai = Airport("BOM", "Chhatrapati Shivaji Maharaj International Airport",
                     "Mumbai", "India", 2, 2)
    
    # Create aircraft
    boeing = Aircraft("AI101", "Boeing 787", "Boeing", 
                      {'economy': 200, 'business': 30, 'first': 10}, 
                      126000)
    airbus = Aircraft("AI102", "Airbus A320", "Airbus",
                      {'economy': 150, 'business': 20, 'first': 8},
                      27000)
    
    # Create flight scheduler
    scheduler = FlightScheduler()
    
    # Create flights
    flight1 = Flight("AI405", "Air India", kolkata, delhi,
                     datetime(2025, 10, 21, 6, 0),  # 6:00 AM tomorrow
                     datetime(2025, 10, 21, 8, 30),  # 8:30 AM tomorrow
                     boeing)
    
    flight2 = Flight("AI406", "Air India", delhi, mumbai,
                     datetime(2025, 10, 21, 10, 0),  # 10:00 AM
                     datetime(2025, 10, 21, 12, 0),  # 12:00 PM
                     boeing)
    
    # Try to add flights (should detect if same aircraft is used)
    scheduler.add_flight(flight1)
    scheduler.add_flight(flight2)
    
    # Create passengers
    passenger1 = Passenger("P001", "Rahul ", "M1234567", 18.5)  # 18.5 kg bag
    passenger2 = Passenger("P002", "Priya", "M7654321", 12.0)  # 12 kg bag
    passenger3 = Passenger("P003", "Amita", "M9876543", 22.0)  # 22 kg bag
    
    # Create bookings
    booking1 = Booking(passenger1, flight1, "economy", "Vegetarian")
    booking2 = Booking(passenger2, flight1, "business", "Non-Vegetarian")
    booking3 = Booking(passenger3, flight1, "first", "Jain")
    
    # Add bookings to flight
    print("\n--- MAKING BOOKINGS ---")
    flight1.add_booking(booking1)
    flight1.add_booking(booking2)
    flight1.add_booking(booking3)
    
    # Check-in passengers
    print("\n--- CHECK-IN PROCESS ---")
    bp1 = flight1.check_in_passenger(passenger1, "12A")
    print(bp1)
    
    bp2 = flight1.check_in_passenger(passenger2, "3B")
    print(bp2)
    
    # Delay the flight
    print("\n--- FLIGHT DELAY ---")
    flight1.delay_flight(45, "Bad weather conditions")
    
    # Show flight information
    print("\n--- FLIGHT STATUS ---")
    print(flight1.get_flight_info())
    
    # Show all flights
    scheduler.get_all_flights()
    
    # Test waiting list (book more than capacity)
    print("\n--- TESTING WAITING LIST ---")
    # Set available seats to 0 for demo
    flight1.available_seats['economy'] = 0
    passenger4 = Passenger("P004", "Neha Gupta", "M1111111", 15.0)
    booking4 = Booking(passenger4, flight1, "economy", "Vegetarian")
    flight1.add_booking(booking4)  # Should go to waiting list


if __name__ == "__main__":
    main()