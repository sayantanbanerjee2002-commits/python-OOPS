from datetime import datetime

class Vehicle:
    """Base class representing any vehicle in the rental fleet"""
    
    total_fleet_count = 0 #class variable
    # intialization of new  vehicle with extra attributes when it is created
    def __init__(self, vehicle_id, brand, model, rental_rate_per_day):
        self.vehicle_id = vehicle_id
        self.brand = brand
        self.model = model
        self.rental_rate_per_day = rental_rate_per_day
        self.is_available = True  # Initially all vehicles are available
        self.min_age_requirement = 18  # Default minimum age
        
        Vehicle.total_fleet_count += 1 # increment total fleet count by 1 when new vehicle is created
    
    def calculate_rental_cost(self, days, insurance=False): # Base method to calculate rental cost
        
        base_cost = self.rental_rate_per_day * days
        insurance_cost = 15 * days if insurance else 0 # conditioanal logic is applied (Ternary operator)
        return base_cost + insurance_cost
    
    def mark_as_rented(self): # when the vehicle is rented , marked vehicle is unavailable
        self.is_available = False
    
    def mark_as_available(self): # marked vehicle as available 
        self.is_available = True
    
    def __str__(self): # readable type for string 
        status = "Available" if self.is_available else "Rented"
        return f"{self.brand} {self.model} (ID: {self.vehicle_id}) - ${self.rental_rate_per_day}/day - {status}"


# CHILD CLASSES - Specific vehicle types

class Car(Vehicle): # Represent Car Class with specific features
     
    available_fleet = 0  # Class variable for tracking available cars
    # intialize Car class with Extra variable Fuel_type and Transmission
    def __init__(self, vehicle_id, brand, model, rental_rate_per_day, seats, fuel_type, transmission):
        super().__init__(vehicle_id, brand, model, rental_rate_per_day)
        self.seats = seats
        self.fuel_type = fuel_type
        self.transmission = transmission
        self.min_age_requirement = 21  # reauired age for car
        Car.available_fleet += 1
    
    def calculate_rental_cost(self, days, insurance=False):
        # Calculate Rental cost
        base_cost = super().calculate_rental_cost(days, insurance)
        if self.transmission == "auto":
            base_cost += 10 * days  # $10 extra per day for automatic
        return base_cost
    
    def mark_as_rented(self):
        super().mark_as_rented()
        Car.available_fleet -= 1
    
    def mark_as_available(self):
        super().mark_as_available()
        Car.available_fleet += 1


class Motorcycle(Vehicle): # Represent Motorcycle class with specific fetures
 
    available_fleet = 0 # Class variable ,accesed by all motorcycles
    
    def __init__(self, vehicle_id, brand, model, rental_rate_per_day, engine_cc, has_sidecar):
        super().__init__(vehicle_id, brand, model, rental_rate_per_day)
        self.engine_cc = engine_cc
        self.has_sidecar = has_sidecar
        self.min_age_requirement = 18  # Motorcycles require age 18
        Motorcycle.available_fleet += 1
    
    def calculate_rental_cost(self, days, insurance=False):
    # calculate rental cost : extra cost for Sidecar
        base_cost = super().calculate_rental_cost(days, insurance)
        if self.has_sidecar:
            base_cost += 5 * days  # $5 extra per day for sidecar
        return base_cost
    
    def mark_as_rented(self):
        super().mark_as_rented()
        Motorcycle.available_fleet -= 1
    
    def mark_as_available(self):
        super().mark_as_available()
        Motorcycle.available_fleet += 1


class Van(Vehicle): # Represent Van class with specific Features
    
    available_fleet = 0 # class variable acessed by all created vans
    #Intiaize newly created van with extra attributes cargo_capacity, passanger_seats 
    def __init__(self, vehicle_id, brand, model, rental_rate_per_day, cargo_capacity, passenger_seats):
        super().__init__(vehicle_id, brand, model, rental_rate_per_day)
        self.cargo_capacity = cargo_capacity
        self.passenger_seats = passenger_seats
        self.min_age_requirement = 23  # Vans require age 23+
        Van.available_fleet += 1
    
    def calculate_rental_cost(self, days, insurance=False): # method to calculate Total rental cost
        base_cost = super().calculate_rental_cost(days, insurance)
        if self.passenger_seats > 8: # Large vans required more cost
            base_cost += 20 * days  # $20 extra per day for large vans
        return base_cost
    
    def mark_as_rented(self):
        super().mark_as_rented()
        Van.available_fleet -= 1
    
    def mark_as_available(self):
        super().mark_as_available()
        Van.available_fleet += 1


class Truck(Vehicle): # Represent Truck class with specific features
    
    available_fleet = 0 # class variable shared by all newly created Tasks
    # Intialize newly Created Truck with extra attributes load_capacity, special_license
    def __init__(self, vehicle_id, brand, model, rental_rate_per_day, load_capacity, requires_special_license):
        super().__init__(vehicle_id, brand, model, rental_rate_per_day)
        self.load_capacity = load_capacity
        self.requires_special_license = requires_special_license
        self.min_age_requirement = 25  # Trucks require age 25+
        Truck.available_fleet += 1
    
    def calculate_rental_cost(self, days, insurance=False): # method to calculate toatl rent
        base_cost = super().calculate_rental_cost(days, insurance)
        if self.load_capacity > 5000: # Heavy trucks requrfred more cost
            base_cost += 30 * days  # $30 extra per day for heavy trucks
        return base_cost
    
    def mark_as_rented(self):
        super().mark_as_rented()
        Truck.available_fleet -= 1
    
    def mark_as_available(self):
        super().mark_as_available()
        Truck.available_fleet += 1


# RENTAL AGREEMENT CLASS (Composition)

class RentalAgreement:
    """Rental agreement linking customer with vehicle using composition"""
    
    def __init__(self, customer_name, customer_age, vehicle, rental_days, insurance=False):
        self.customer_name = customer_name
        self.customer_age = customer_age
        self.vehicle = vehicle  # Composition: RentalAgreement "has-a" Vehicle
        self.rental_days = rental_days
        self.insurance = insurance
        self.rental_start = None
        self.rental_end = None
        self.total_cost = 0
        
        # Validate age requirement
        if customer_age < vehicle.min_age_requirement:
            raise ValueError(
                f"Customer must be at least {vehicle.min_age_requirement} years old to rent a {vehicle.__class__.__name__}"
            )
        
        # Check if vehicle is available
        if not vehicle.is_available:
            raise ValueError(f"Vehicle {vehicle.vehicle_id} is not available for rent")
    
    # Context Manager Methods
    def __enter__(self):
        
        print(f"\n{'='*50}")
        print("RENTAL CHECKOUT")
        print(f"{'='*50}")
        
        self.vehicle.mark_as_rented()
        self.rental_start = datetime.now()
        self.total_cost = self.vehicle.calculate_rental_cost(self.rental_days, self.insurance)
        
        print(f"Customer: {self.customer_name} (Age: {self.customer_age})")
        print(f"Vehicle: {self.vehicle}")
        print(f"Rental Period: {self.rental_days} days")
        print(f"Insurance: {'Yes' if self.insurance else 'No'}")
        print(f"Total Cost: ${self.total_cost:.2f}")
        print(f"Rental Start: {self.rental_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        
        print(f"\n{'='*50}")
        print("RENTAL RETURN")
        print(f"{'='*50}")
        
        self.vehicle.mark_as_available()
        self.rental_end = datetime.now()
        
        print(f"Customer: {self.customer_name}")
        print(f"Vehicle: {self.vehicle}")
        print(f"Rental End: {self.rental_end.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Charged: ${self.total_cost:.2f}")
        print("Vehicle returned successfully!")
        print(f"{'='*50}\n")
        
        return False  # Don't suppress exceptions


# DEMONSTRATION & TESTING

def main():
    print("="*60)
    print("CAR RENTAL SYSTEM - DEMONSTRATION")
    print("="*60)
    
    # Create fleet of vehicles
    print("\n1. Creating Fleet of Vehicles...")
    print("-" * 60)
    
    car1 = Car("C001", "Toyota", "Camry", 50, 4, "Petrol", "auto")
    car2 = Car("C002", "BMW", "Civic", 55, 5, "Petrol", "manual")
    
    bike1 = Motorcycle("M001", "KTM", "Street 750", 30, 750, False)
    bike2 = Motorcycle("M002", "Royal Enfield", "Classic 350", 25, 350, True)
    
    van1 = Van("V001", "Mercedes", "Sprinter", 80, 3000, 12)
    van2 = Van("V002", "Ford", "Transit", 70, 2500, 8)
    
    truck1 = Truck("T001", "Ford", "F-150", 90, 3000, False)
    truck2 = Truck("T002", "Volvo", "FH16", 120, 6000, True)
    
    all_vehicles = [car1, car2, bike1, bike2, van1, van2, truck1, truck2]
    
    for vehicle in all_vehicles:
        print(f"  {vehicle}")
    
    # Display fleet statistics
    print(f"\n2. Fleet Statistics:")
    print("-" * 60)
    print(f"  Total Vehicles: {Vehicle.total_fleet_count}")
    print(f"  Available Cars: {Car.available_fleet}")
    print(f"  Available Motorcycles: {Motorcycle.available_fleet}")
    print(f"  Available Vans: {Van.available_fleet}")
    print(f"  Available Trucks: {Truck.available_fleet}")
    
    # Test cost calculations
    print(f"\n3. Cost Calculations (5 days, with/without insurance):")
    print("-" * 60)
    print(f"  {car1.brand} {car1.model} (Auto): ${car1.calculate_rental_cost(5):.2f} / ${car1.calculate_rental_cost(5, True):.2f} (with insurance)")
    print(f"  {bike2.brand} {bike2.model} (Sidecar): ${bike2.calculate_rental_cost(5):.2f} / ${bike2.calculate_rental_cost(5, True):.2f} (with insurance)")
    print(f"  {van1.brand} {van1.model} (Large): ${van1.calculate_rental_cost(5):.2f} / ${van1.calculate_rental_cost(5, True):.2f} (with insurance)")
    print(f"  {truck2.brand} {truck2.model} (Heavy): ${truck2.calculate_rental_cost(5):.2f} / ${truck2.calculate_rental_cost(5, True):.2f} (with insurance)")
    
    # Test rental agreement with context manager
    print(f"\n4. Testing Rental Agreement with Context Manager:")
    print("-" * 60)
    
    # Successful rental
    try:
        with RentalAgreement("John Smith", 25, car1, 3, insurance=True) as rental:
            print(f"  >>> Rental in progress for {rental.customer_name}...")
            # Simulate some operations during rental
            print(f"  >>> Customer is enjoying the {rental.vehicle.brand} {rental.vehicle.model}")
        # After 'with' block, vehicle is automatically returned
    except ValueError as e:
        print(f"  Rental Failed: {e}")
    
    # Display updated fleet statistics
    print(f"\n5. Updated Fleet Statistics After Return:")
    print("-" * 60)
    print(f"  Available Cars: {Car.available_fleet}")
    print(f"  {car1.brand} {car1.model} Status: {'Available' if car1.is_available else 'Rented'}")
    
    # Test age validation
    print(f"\n6. Testing Age Validation:")
    print("-" * 60)
    
    try:
        with RentalAgreement("Young Driver", 19, truck1, 2) as rental:
            pass
    except ValueError as e:
        print(f"  ✗ Rental Denied: {e}")
    
    # Test vehicle unavailability
    print(f"\n7. Testing Vehicle Availability Check:")
    print("-" * 60)
    
    try:
        with RentalAgreement("Alice Johnson", 30, van1, 5, insurance=True) as rental1:
            print(f"  >>> {rental1.customer_name} has rented {rental1.vehicle.brand} {rental1.vehicle.model}")
            
            # Try to rent the same vehicle while it's rented
            try:
                with RentalAgreement("Bob Williams", 28, van1, 3) as rental2:
                    pass
            except ValueError as e:
                print(f"  ✗ Second Rental Failed: {e}")
    except ValueError as e:
        print(f"  ✗ Rental Failed: {e}")
    
    # Final fleet status
    print(f"\n8. Final Fleet Status:")
    print("-" * 60)
    for vehicle in all_vehicles:
        print(f"  {vehicle}")
    
    print(f"\n{'='*60}")
    print("DEMONSTRATION COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()