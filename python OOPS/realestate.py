from datetime import datetime, timedelta
from typing import List, Optional

# =======
# BASE CLASSES
# =======

class Property: # Represent Base class for all properties with shared attributes
  
    def __init__(self, property_id: str, address: str, owner, area_sqft: float, price: float):
        # Unique identifier for each property
        self.property_id = property_id
        # Full address of the property
        self.address = address
        # Owner object reference
        self.owner = owner
        # Total area in square feet
        self.area_sqft = area_sqft
        # Purchase/sale price of the property
        self.price = price
        # List to store tenants (a property can have multiple tenants over time)
        self.tenants: List[Tenant] = []
        # Current tenant (None if vacant)
        self.current_tenant: Optional[Tenant] = None
        # List to track all maintenance requests
        self.maintenance_requests: List[MaintenanceRequest] = []
    
    def calculate_property_value(self) -> float: # Method to calculate property value 
        return self.price
    
    def add_tenant(self, tenant):
        """Add a tenant to this property and set as current tenant"""
        self.tenants.append(tenant)
        self.current_tenant = tenant
    
    def remove_tenant(self):
        """Remove current tenant """
        self.current_tenant = None
    
    def add_maintenance_request(self, request):
        """Add a maintenance request to this property"""
        self.maintenance_requests.append(request)
    
    def __str__(self):
        """String representation for easy printing"""
        return f"{self.__class__.__name__} - {self.property_id} at {self.address}"


# ==========================================
# PROPERTY TYPES (Inheritance from Property)
# ==========================================

class Apartment(Property): 
  # Represent Apartment class with specific attributes  
    def __init__(self, property_id: str, address: str, owner, area_sqft: float, 
                 price: float, floor_number: int, building_name: str, 
                 parking_slots: int, maintenance_fee: float):
        # Call parent class constructor to initialize common properties
        super().__init__(property_id, address, owner, area_sqft, price)
        # Apartment-specific attributes
        self.floor_number = floor_number
        self.building_name = building_name
        self.parking_slots = parking_slots
        self.maintenance_fee = maintenance_fee
    
    def calculate_property_value(self) -> float:
        base_value = self.price
        # Higher floors get 2% bonus per floor
        floor_bonus = self.floor_number * 0.02 * base_value
        # Each parking slot adds $10,000 to value
        parking_value = self.parking_slots * 10000
        return base_value + floor_bonus + parking_value


class Villa(Property):
 # Represent Villa type property with extra attributes
    def __init__(self, property_id: str, address: str, owner, area_sqft: float, 
                 price: float, plot_area: float, number_of_floors: int, 
                 has_garden: bool, has_swimming_pool: bool):
        super().__init__(property_id, address, owner, area_sqft, price)
        # Villa-specific attributes
        self.plot_area = plot_area  # Total land area
        self.number_of_floors = number_of_floors
        self.has_garden = has_garden
        self.has_swimming_pool = has_swimming_pool
    
    def calculate_property_value(self) -> float:
        
        # Villa valuation considers luxury amenities:
        # - Base price
        # - Garden adds 10% value
        # - Swimming pool adds 15% value
        # - Larger plot area increases value
       
        base_value = self.price
        amenity_bonus = 0
        # Garden increases value by 10%
        if self.has_garden:
            amenity_bonus += 0.10 * base_value
        # Swimming pool increases value by 15%
        if self.has_swimming_pool:
            amenity_bonus += 0.15 * base_value
        # Large plot bonus: if plot is bigger than built area
        plot_bonus = (self.plot_area - self.area_sqft) * 50  # $50 per extra sqft
        return base_value + amenity_bonus + plot_bonus


class CommercialSpace(Property): 
    # Represent Commercial Space type property with extra attribute
    def __init__(self, property_id: str, address: str, owner, area_sqft: float, 
                 price: float, business_type_allowed: str, parking_capacity: int, 
                 floor_load_capacity: float):
        super().__init__(property_id, address, owner, area_sqft, price)
        # Commercial-specific attributes
        self.business_type_allowed = business_type_allowed  # retail/office/industrial
        self.parking_capacity = parking_capacity  # Number of parking spaces
        self.floor_load_capacity = floor_load_capacity  # Load capacity in kg/sqm
    
    def calculate_property_value(self) -> float:
       
        # Commercial valuation based on:
        # - Base price
        # - Parking capacity (crucial for commercial)
        # - Business type flexibility
       
        base_value = self.price
        # Each parking space adds $15,000 (more valuable than residential)
        parking_value = self.parking_capacity * 15000
        # Mixed-use or flexible zoning adds 20% premium
        business_bonus = 0.20 * base_value if self.business_type_allowed == "mixed" else 0
        return base_value + parking_value + business_bonus


class Land(Property):
  # Represent Land type property with extra attributes
    def __init__(self, property_id: str, address: str, owner, area_sqft: float, 
                 price: float, zoning_type: str, road_access: bool):
        super().__init__(property_id, address, owner, area_sqft, price)
        # Land-specific attributes
        self.zoning_type = zoning_type  # residential/commercial/agricultural
        self.road_access = road_access  # Whether land has direct road access
    
    def calculate_property_value(self) -> float:
       
        # Land valuation based on:
        # - Base price per sqft
        # - Zoning type (commercial > residential > agricultural)
        # - Road access (critical for development)
       
        base_value = self.price
        # Zoning multipliers
        zoning_multiplier = {
            "commercial": 1.5,  # 50% premium
            "residential": 1.2,  # 20% premium
            "agricultural": 1.0  # Base value
        }
        zoning_bonus = base_value * (zoning_multiplier.get(self.zoning_type, 1.0) - 1)
        # Road access adds 30% value
        road_bonus = 0.30 * base_value if self.road_access else 0
        return base_value + zoning_bonus + road_bonus


# ============
# OWNER CLASS
# ============
class Owner:
  # Represent a Property owner who has multiple Properties
    def __init__(self, name: str, contact: str, tax_id: str):
        self.name = name
        self.contact = contact  # Phone or email
        self.properties_owned: List[Property] = []  # List of properties owned
        self.tax_id = tax_id  # Tax identification number
    
    def add_property(self, property: Property):
        """Add a property to owner's portfolio"""
        self.properties_owned.append(property)
    
    def calculate_monthly_rental_income(self) -> float:
        """
        Calculate total monthly rental income from all properties.
        Only count properties with current tenants.
        """
        total_income = 0
        # Loop through all properties owned
        for prop in self.properties_owned:
            # If property has a tenant, add their rent to total
            if prop.current_tenant:
                total_income += prop.current_tenant.rent_amount
        return total_income
    
    def get_total_property_value(self) -> float:
        """Calculate total value of all properties owned"""
        return sum(prop.calculate_property_value() for prop in self.properties_owned)
    
    def __str__(self):
        return f"Owner: {self.name} (Properties: {len(self.properties_owned)})"


# ============
# TENANT CLASS
# ============

class Tenant:
    """
    Represents a tenant renting a property
    """
    def __init__(self, name: str, lease_start_date: datetime, lease_end_date: datetime, 
                 rent_amount: float, deposit: float):
        self.name = name
        self.lease_start_date = lease_start_date
        self.lease_end_date = lease_end_date
        self.rent_amount = rent_amount  # Monthly rent
        self.deposit = deposit  # Security deposit
        # Track rent payment history: {date: amount_paid}
        self.payment_history: dict = {}
        self.total_paid = 0
    
    def make_payment(self, payment_date: datetime, amount: float):
        """Record a rent payment"""
        self.payment_history[payment_date] = amount
        self.total_paid += amount
    
    def calculate_late_fee(self, current_date: datetime, due_day: int = 5, 
                          late_fee_percent: float = 0.05) -> float:
        """
        Calculate late fee if rent is not paid by due date.
        
        Returns:
            Late fee amount
        """
        # Check if we're past the due date for current month
        due_date = datetime(current_date.year, current_date.month, due_day)
        
        if current_date > due_date:
            # Check if payment was made for current month
            current_month_payments = [
                amount for date, amount in self.payment_history.items()
                if date.month == current_date.month and date.year == current_date.year
            ]
            
            # If no payment or partial payment, calculate late fee
            if sum(current_month_payments) < self.rent_amount:
                return self.rent_amount * late_fee_percent
        
        return 0  # No late fee
    
    def is_lease_active(self, current_date: datetime) -> bool:
        """Check if lease is currently active"""
        return self.lease_start_date <= current_date <= self.lease_end_date
    
    def __str__(self):
        return f"Tenant: {self.name} (Rent: ${self.rent_amount}/month)"


# =========================
# MAINTENANCE REQUEST CLASS
# ==========================

class MaintenanceRequest:
    """
    Tracks maintenance issues for properties
    """
    # Class variable to auto-generate request IDs
    _request_counter = 1
    
    def __init__(self, property: Property, issue_description: str, 
                 priority: str, assigned_to: str = "Unassigned"):
        self.request_id = f"MR{MaintenanceRequest._request_counter:04d}"
        MaintenanceRequest._request_counter += 1
        
        self.property = property
        self.issue_description = issue_description
        self.status = "Open"  # Open, In Progress, Closed
        self.priority = priority  # Low, Medium, High, Critical
        self.assigned_to = assigned_to  # Maintenance staff name
        self.created_date = datetime.now()
        self.closed_date: Optional[datetime] = None
    
    def update_status(self, new_status: str):
        """Update the status of maintenance request"""
        self.status = new_status
        if new_status == "Closed":
            self.closed_date = datetime.now()
    
    def assign_to(self, staff_name: str):
        """Assign maintenance request to a staff member"""
        self.assigned_to = staff_name
        if self.status == "Open":
            self.status = "In Progress"
    
    def __str__(self):
        return f"{self.request_id} - {self.priority} - {self.status}: {self.issue_description}"


# ===========================
# PROPERTY MANAGEMENT SYSTEM
# ===========================

class PropertyManagementSystem:
    """
    Main system to manage all properties, owners, and operations
    """
    def __init__(self):
        self.properties: List[Property] = []
        self.owners: List[Owner] = []
        self.maintenance_requests: List[MaintenanceRequest] = []
    
    def add_property(self, property: Property):
        """Add a property to the system"""
        self.properties.append(property)
    
    def add_owner(self, owner: Owner):
        """Add an owner to the system"""
        self.owners.append(owner)
    
    def search_properties(self, min_price: float = 0, max_price: float = float('inf'), 
                         location: str = "", property_type: str = "") -> List[Property]:
        """
        Search properties with filters
        
        Returns:
            List of matching properties
        """
        results = []
        
        for prop in self.properties:
            # Check price range
            if not (min_price <= prop.price <= max_price):
                continue
            
            # Check location (case-insensitive partial match)
            if location and location.lower() not in prop.address.lower():
                continue
            
            # Check property type
            if property_type and prop.__class__.__name__ != property_type:
                continue
            
            results.append(prop)
        
        return results
    
    @classmethod
    def calculate_market_analysis(cls, properties: List[Property]) -> dict:
        """
        Analyze market prices by calculating averages
        
        Returns:
            Dictionary with analysis results
        """
        if not properties:
            return {"error": "No properties to analyze"}
        
        # Group properties by type
        by_type = {}
        by_location = {}
        
        for prop in properties:
            # Group by property type
            prop_type = prop.__class__.__name__
            if prop_type not in by_type:
                by_type[prop_type] = []
            by_type[prop_type].append(prop.price)
            
            # Group by location (use first word of address as area)
            area = prop.address.split(',')[0].strip()
            if area not in by_location:
                by_location[area] = []
            by_location[area].append(prop.price)
        
        # Calculate averages
        analysis = {
            "total_properties": len(properties),
            "average_by_type": {
                prop_type: sum(prices) / len(prices) 
                for prop_type, prices in by_type.items()
            },
            "average_by_area": {
                area: sum(prices) / len(prices) 
                for area, prices in by_location.items()
            },
            "overall_average": sum(p.price for p in properties) / len(properties)
        }
        
        return analysis
    
    def get_vacant_properties(self) -> List[Property]:
        """Get list of properties without current tenants"""
        return [prop for prop in self.properties if prop.current_tenant is None]
    
    def get_properties_needing_maintenance(self) -> List[Property]:
        """Get properties with open maintenance requests"""
        properties_with_issues = set()
        for prop in self.properties:
            for request in prop.maintenance_requests:
                if request.status != "Closed":
                    properties_with_issues.add(prop)
        return list(properties_with_issues)


# ==============
#  DEMONSTRATION
# ==============

def demo_system():
    """Demonstration of the property management system"""
    
    print("=" * 70)
    print("PROPERTY MANAGEMENT SYSTEM DEMO")
    print("=" * 70)
    
    # Create the management system
    pms = PropertyManagementSystem()
    
    # Create owners
    owner1 = Owner("Sayantan Banerjee", "Sayantan@email.com", "TAX123458")
    owner2 = Owner("Diya Banerjee", "Diya@email.com", "TAX123454")
    pms.add_owner(owner1)
    pms.add_owner(owner2)
    
    print("\n1. CREATING PROPERTIES")
    print("-" * 70)
    
    # Create different types of properties
    apt1 = Apartment("APT001", "Downtown, City Center", owner1, 1200, 350000, 
                     floor_number=4, building_name="Skyline Towers", 
                     parking_slots=1, maintenance_fee=2000)
    owner1.add_property(apt1)
    pms.add_property(apt1)
    print(f" Created: {apt1}")
    
    villa1 = Villa("VIL001", "Sunset Dreamer, Beach Area", owner1, 3500, 950000,
                   plot_area=5000, number_of_floors=2, has_garden=True, 
                   has_swimming_pool=True)
    owner1.add_property(villa1)
    pms.add_property(villa1)
    print(f" Created: {villa1}")
    
    commercial1 = CommercialSpace("COM001", "Business District, Ecco Park", owner2, 
                                  2000, 550000, business_type_allowed="office",
                                  parking_capacity=15, floor_load_capacity=700)
    owner2.add_property(commercial1)
    pms.add_property(commercial1)
    print(f" Created: {commercial1}")
    
    land1 = Land("LND001", "Farm Road, Salbani", owner2, 15000, 270000,
                 zoning_type="commercial", road_access=True)
    owner2.add_property(land1)
    pms.add_property(land1)
    print(f" Created: {land1}")
    
    # Property valuations
    print("\n2. PROPERTY VALUATIONS")
    print("-" * 70)
    print(f"Apartment value: ${apt1.calculate_property_value():,.2f}")
    print(f"Villa value: ${villa1.calculate_property_value():,.2f}")
    print(f"Commercial value: ${commercial1.calculate_property_value():,.2f}")
    print(f"Land value: ${land1.calculate_property_value():,.2f}")
    
    # Create tenants
    print("\n3. ADDING TENANTS")
    print("-" * 70)
    tenant1 = Tenant("Mike Wilson", 
                    datetime(2024, 1, 1), 
                    datetime(2025, 12, 31),
                    rent_amount=2800, 
                    deposit=5000)
    apt1.add_tenant(tenant1)
    print(f" {tenant1} assigned to {apt1.property_id}")
    
    tenant2 = Tenant("Souvik",
                    datetime(2024, 6, 1),
                    datetime(2026, 5, 31),
                    rent_amount=5000,
                    deposit=10000)
    villa1.add_tenant(tenant2)
    print(f" {tenant2} assigned to {villa1.property_id}")
    
    # Rent payments and late fees
    print("\n4. RENT PAYMENT TRACKING")
    print("-" * 70)
    tenant1.make_payment(datetime(2024, 10, 3), 2500)
    print(f" Tenant Mike paid $2500 on Oct 3, 2024")
    
    # Calculate late fee for tenant who didn't pay
    late_fee = tenant2.calculate_late_fee(datetime(2024, 10, 20))
    print(f" Tenant Souvik has late fee: ${late_fee}")
    
    # Owner's rental income
    print("\n5. OWNER RENTAL INCOME")
    print("-" * 70)
    income = owner1.calculate_monthly_rental_income()
    print(f"{owner1.name}'s monthly rental income: ${income:,.2f}")
    print(f"Total property value: ${owner1.get_total_property_value():,.2f}")
    
    # Maintenance requests
    print("\n6. MAINTENANCE MANAGEMENT")
    print("-" * 70)
    request1 = MaintenanceRequest(apt1, "Leaking faucet in kitchen", 
                                  priority="Medium")
    apt1.add_maintenance_request(request1)
    pms.maintenance_requests.append(request1)
    print(f" Created: {request1}")
    
    request2 = MaintenanceRequest(villa1, "Pool pump not working", 
                                  priority="High")
    villa1.add_maintenance_request(request2)
    pms.maintenance_requests.append(request2)
    request2.assign_to("Bob the Handyman")
    print(f" Created: {request2}")
    
    request1.update_status("Closed")
    print(f" Updated: {request1.request_id} status to Closed")
    
    # Property search
    print("\n7. PROPERTY SEARCH")
    print("-" * 70)
    results = pms.search_properties(min_price=300000, max_price=600000, 
                                   location="District")
    print(f"Properties priced $300K-$600K in 'District': {len(results)} found")
    for prop in results:
        print(f"  • {prop}")
    
    # Market analysis
    print("\n8. MARKET ANALYSIS")
    print("-" * 70)
    analysis = PropertyManagementSystem.calculate_market_analysis(pms.properties)
    print(f"Total properties analyzed: {analysis['total_properties']}")
    print("\nAverage price by type:")
    for prop_type, avg_price in analysis['average_by_type'].items():
        print(f"  • {prop_type}: ${avg_price:,.2f}")
    print(f"\nOverall market average: ${analysis['overall_average']:,.2f}")
    
    # Vacant properties
    print("\n9. VACANT PROPERTIES")
    print("-" * 70)
    vacant = pms.get_vacant_properties()
    print(f"Available for rent: {len(vacant)} properties")
    for prop in vacant:
        print(f"  • {prop}")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETED")
    print("=" * 70)


# Run the demonstration
if __name__ == "__main__":
    demo_system()