from enum import Enum
from datetime import datetime
import math

# Enum for order status - defines the stages an order goes through
class OrderStatus(Enum):
    PLACED = "placed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# MenuItem represents a single dish in a restaurant's menu
class MenuItem:
    def __init__(self, name, price, category, is_vegetarian, preparation_time):
        self.name = name                          # Name of the dish
        self.price = price                        # Price of the dish
        self.category = category                  # Category like "Main Course", "Dessert"
        self.is_vegetarian = is_vegetarian        # True if vegetarian
        self.preparation_time = preparation_time  # Time in minutes to prepare
    
    def __str__(self):
        veg_label = "veg" if self.is_vegetarian else "Non_veg"
        return f"{veg_label} {self.name} - ₹{self.price} ({self.preparation_time} mins)"

# Restaurant class with menu and delivery capabilities
class Restaurant:
    def __init__(self, name, location, cuisine_type, delivery_range):
        self.name = name                    # Restaurant name
        self.location = location            # Location as (x, y) coordinates
        self.cuisine_type = cuisine_type    # Type like "Italian", "Indian"
        self.menu = []                      # List of MenuItem objects
        self.ratings = 4.0                  # Average rating (default 4.0)
        self.delivery_range = delivery_range # Maximum delivery distance in km
    
    def add_menu_item(self, menu_item):
        """Add a new dish to the restaurant's menu"""
        self.menu.append(menu_item)
    
    def can_deliver_to(self, customer_location):
        """Check if restaurant can deliver to customer's location"""
        distance = self._calculate_distance(customer_location)
        return distance <= self.delivery_range
    
    def _calculate_distance(self, customer_location):
        """Calculate distance between restaurant and customer (Euclidean distance)"""
        x1, y1 = self.location
        x2, y2 = customer_location
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def display_menu(self):
        """Display all menu items"""
        print(f"\n{'='*50}")
        print(f" {self.name} - {self.cuisine_type}")
        print(f" Rating: {self.ratings}/5.0")
        print(f"{'='*50}")
        for idx, item in enumerate(self.menu, 1):
            print(f"{idx}. {item}")
        print(f"{'='*50}\n")

# Customer class with wallet and order history
class Customer:
    def __init__(self, name, address):
        self.name = name                    # Customer name
        self.address = address              # Address as (x, y) coordinates
        self.order_history = []             # List of past orders
        self.wallet_balance = 1000.0        # Initial wallet balance
        self.loyalty_points = 0             # Loyalty points earned
    
    def add_money_to_wallet(self, amount):
        """Add money to customer's wallet"""
        self.wallet_balance += amount
        print(f" ₹{amount} added to wallet. New balance: ₹{self.wallet_balance}")
    
    def deduct_from_wallet(self, amount):
        """Deduct money from wallet for order payment"""
        if self.wallet_balance >= amount:
            self.wallet_balance -= amount
            return True
        return False
    
    def add_loyalty_points(self, points):
        """Add loyalty points after order completion"""
        self.loyalty_points += points
        print(f" You earned {points} loyalty points! Total: {self.loyalty_points}")
    
    def redeem_loyalty_points(self, points_to_redeem):
        """Redeem loyalty points for discount (100 points = ₹10 discount)"""
        if self.loyalty_points >= points_to_redeem:
            self.loyalty_points -= points_to_redeem
            discount = points_to_redeem / 10  # 100 points = ₹10
            return discount
        return 0
    
    def view_wallet(self):
        """Display wallet and loyalty points"""
        print(f"\n {self.name}'s Wallet")
        print(f" Balance: ₹{self.wallet_balance:.2f}")
        print(f" Loyalty Points: {self.loyalty_points}\n")

# Delivery Partner class
class DeliveryPartner:
    def __init__(self, name, vehicle_type, current_location):
        self.name = name                          # Partner name
        self.vehicle_type = vehicle_type          # "bike", "car", "bicycle"
        self.current_location = current_location  # Location as (x, y)
        self.is_available = True                  # Availability status
        self.earnings = 0.0                       # Total earnings
    
    def calculate_distance_from(self, location):
        """Calculate distance from given location by the formula = (x2-x1)**2 + (y2 - y1)**2"""
        x1, y1 = self.current_location 
        x2, y2 = location
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def assign_order(self):
        """Mark partner as busy when order is assigned"""
        self.is_available = False
    
    def complete_delivery(self, delivery_fee):
        """Mark partner as available and add earnings"""
        self.is_available = True
        self.earnings += delivery_fee
        print(f" {self.name} earned ₹{delivery_fee}. Total earnings: ₹{self.earnings}")

# Delivery Tracking system
class DeliveryTracking:
    def __init__(self, order):
        self.order = order                    # Reference to the order being tracked
        self.status_history = []              # History of status changes
        self.estimated_delivery_time = 30     # Estimated time in minutes
    
    def update_status(self, new_status, message=""):
        """Update order status and log it"""
        self.order.status = new_status
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_history.append(f"[{timestamp}] {new_status.value}: {message}")
        print(f" [{timestamp}] Order Status: {new_status.value.upper()} - {message}")
    
    def display_tracking_info(self):
        """Show complete tracking history"""
        print(f"\n{'='*60}")
        print(f" Order Tracking - Order #{self.order.order_id}")
        print(f"{'='*60}")
        for entry in self.status_history:
            print(entry)
        print(f"⏱  Estimated delivery: {self.estimated_delivery_time} minutes")
        print(f"{'='*60}\n")

# Main Order class that ties everything together
class Order:
    order_counter = 1000  # Static counter for order IDs
    
    def __init__(self, restaurant, customer, items):
        self.order_id = Order.order_counter
        Order.order_counter += 1
        self.restaurant = restaurant          # Restaurant object
        self.customer = customer              # Customer object
        self.items = items                    # List of MenuItem objects
        self.total_amount = 0                 # Final amount to pay
        self.status = OrderStatus.PLACED      # Initial status
        self.delivery_partner = None          # Assigned delivery partner
        self.tracking = DeliveryTracking(self) # Tracking system
        self.distance = self._calculate_delivery_distance()
        self.base_amount = self._calculate_base_amount()
    
    def _calculate_base_amount(self):
        """Calculate sum of all item prices"""
        return sum(item.price for item in self.items)
    
    def _calculate_delivery_distance(self):
        """Calculate distance between restaurant and customer"""
        x1, y1 = self.restaurant.location
        x2, y2 = self.customer.address
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def calculate_dynamic_pricing(self, is_peak_hour=False, surge_multiplier=1.0):
        """
        Dynamic pricing calculation:
        - Base amount (sum of item prices)
        - Distance charges (₹10 per km)
        - Peak hour surcharge (20% extra if peak hour)
        - Surge pricing (multiplier based on demand)
        - Taxes (5% GST)
        """
        base_amount = self.base_amount
        distance_charge = self.distance * 10  # ₹10 per km
        
        # Peak hour surcharge (6-9 PM)
        peak_surcharge = base_amount * 0.2 if is_peak_hour else 0
        
        # Surge pricing
        surge_amount = (base_amount + distance_charge) * (surge_multiplier - 1)
        
        # Taxes
        subtotal = base_amount + distance_charge + peak_surcharge + surge_amount
        tax = subtotal * 0.05  # 5% GST
        
        self.total_amount = subtotal + tax
        
        # Display pricing breakdown
        print(f"\n Pricing Breakdown:")
        print(f"   Items Total: ₹{base_amount:.2f}")
        print(f"   Delivery ({self.distance:.1f} km): ₹{distance_charge:.2f}")
        if is_peak_hour:
            print(f"   Peak Hour Surcharge: ₹{peak_surcharge:.2f}")
        if surge_multiplier > 1.0:
            print(f"   Surge Pricing ({surge_multiplier}x): ₹{surge_amount:.2f}")
        print(f"   GST (5%): ₹{tax:.2f}")
        print(f"   {'─'*30}")
        print(f"   TOTAL: ₹{self.total_amount:.2f}\n")
        
        return self.total_amount
    
    def apply_loyalty_discount(self, points_to_redeem):
        """Apply loyalty points discount to total amount"""
        discount = self.customer.redeem_loyalty_points(points_to_redeem)
        if discount > 0:
            self.total_amount -= discount
            print(f" Discount applied: -₹{discount:.2f}")
            print(f"   New Total: ₹{self.total_amount:.2f}\n")
    
    def find_nearest_delivery_partner(self, available_partners):
        """
        Partner assignment algorithm:
        - Find all available partners
        - Calculate distance from restaurant to each partner
        - Assign the nearest one
        """
        if not available_partners:
            print(" No delivery partners available!")
            return None
        
        # Filter only available partners
        available = [p for p in available_partners if p.is_available]
        
        if not available:
            print(" No delivery partners available right now!")
            return None
        
        # Find nearest partner
        nearest_partner = min(available, 
                             key=lambda p: p.calculate_distance_from(self.restaurant.location))
        
        self.delivery_partner = nearest_partner
        nearest_partner.assign_order()
        
        distance = nearest_partner.calculate_distance_from(self.restaurant.location)
        print(f" Delivery partner assigned: {nearest_partner.name} ({nearest_partner.vehicle_type})")
        print(f"   Distance from restaurant: {distance:.1f} km\n")
        
        return nearest_partner
    
    def place_order(self, available_partners, is_peak_hour=False, surge_multiplier=1.0):
        """
        Complete order placement process:
        1. Check if restaurant can deliver
        2. Calculate total amount
        3. Check customer wallet balance
        4. Find delivery partner
        5. Deduct payment
        6. Initialize tracking
        """
        print(f"\n{''*25}")
        print(f"  PLACING ORDER #{self.order_id}")
        print(f"{''*25}\n")
        
        # Step 1: Check delivery availability
        if not self.restaurant.can_deliver_to(self.customer.address):
            print(f" Sorry! {self.restaurant.name} doesn't deliver to your location.")
            return False
        
        print(f" {self.restaurant.name} can deliver to your location!\n")
        
        # Step 2: Calculate total amount
        self.calculate_dynamic_pricing(is_peak_hour, surge_multiplier)
        
        # Step 3: Check wallet balance
        if self.customer.wallet_balance < self.total_amount:
            print(f" Insufficient balance! Need ₹{self.total_amount:.2f}, have ₹{self.customer.wallet_balance:.2f}")
            return False
        
        # Step 4: Find delivery partner
        if not self.find_nearest_delivery_partner(available_partners):
            return False
        
        # Step 5: Deduct payment
        self.customer.deduct_from_wallet(self.total_amount)
        print(f" Payment successful! New balance: ₹{self.customer.wallet_balance:.2f}\n")
        
        # Step 6: Initialize tracking
        self.tracking.update_status(OrderStatus.PLACED, f"Order placed at {self.restaurant.name}")
        
        # Add to customer's order history
        self.customer.order_history.append(self)
        
        print(f" Order placed successfully! Order ID: #{self.order_id}\n")
        return True
    
    def update_order_status(self, new_status, message=""):
        """Update order status through tracking system"""
        self.tracking.update_status(new_status, message)
    
    def complete_order(self):
        """
        Complete the order:
        - Update status to delivered
        - Pay delivery partner
        - Award loyalty points to customer
        """
        self.update_order_status(OrderStatus.DELIVERED, "Order delivered successfully!")
        
        # Pay delivery partner (30% of delivery charge)
        delivery_fee = self.distance * 10 * 0.3
        self.delivery_partner.complete_delivery(delivery_fee)
        
        # Award loyalty points (1 point per ₹10 spent)
        loyalty_points = int(self.total_amount / 10)
        self.customer.add_loyalty_points(loyalty_points)
        
        print(f"\n  Order completed! Thank you for ordering from {self.restaurant.name}!\n")
    
    def display_order_summary(self):
        """Display complete order details"""
        print(f"\n{'='*60}")
        print(f" ORDER SUMMARY - #{self.order_id}")
        print(f"{'='*60}")
        print(f" Restaurant: {self.restaurant.name}")
        print(f" Customer: {self.customer.name}")
        print(f" Status: {self.status.value.upper()}")
        print(f"\n Items:")
        for item in self.items:
            print(f"   • {item.name} - ₹{item.price}")
        print(f"\n  Total Amount: ₹{self.total_amount:.2f}")
        if self.delivery_partner:
            print(f" Delivery Partner: {self.delivery_partner.name}")
        print(f"{'='*60}\n")


# ==================== DEMO USAGE ====================

def main():
    print("\n" + "*"*30)
    print(" "*20 + "FOOD DELIVERY SYSTEM DEMO")
    print("*"*30 + "\n")
    
    # Create a restaurant
    restaurant = Restaurant("Pizza volcano", (0, 0), "Italian", delivery_range=10)
    
    # Add menu items
    restaurant.add_menu_item(MenuItem("Margherita Pizza", 250, "Main Course", True, 15))
    restaurant.add_menu_item(MenuItem("Pepperoni Pizza", 350, "Main Course", False, 18))
    restaurant.add_menu_item(MenuItem("Garlic Bread", 100, "Appetizer", True, 10))
    restaurant.add_menu_item(MenuItem("Chocolate Lava Cake", 150, "Dessert", True, 12))
    
    # Display menu
    restaurant.display_menu()
    
    # Create a customer
    customer = Customer("Ahan", (3, 4))  # 5 km away from restaurant
    customer.view_wallet()
    
    # Create delivery partners
    partners = [
        DeliveryPartner("Rakesh", "bike", (1, 1)),
        DeliveryPartner("Priya", "car", (5, 5)),
        DeliveryPartner("Amit", "bicycle", (0.5, 0.5))
    ]
    
    print(" Available Delivery Partners:")
    for p in partners:
        print(f"   • {p.name} ({p.vehicle_type}) - {'Available ' if p.is_available else 'Busy '}")
    print()
    
    # Customer selects items
    selected_items = [
        restaurant.menu[0],  # Margherita Pizza
        restaurant.menu[2],  # Garlic Bread
        restaurant.menu[3]   # Chocolate Lava Cake
    ]
    
    # Create and place order
    order = Order(restaurant, customer, selected_items)
    
    # Place order with peak hour and surge pricing
    success = order.place_order(partners, is_peak_hour=True, surge_multiplier=1.2)
    
    if success:
        # Simulate order progression
        order.display_order_summary()
        
        order.update_order_status(OrderStatus.PREPARING, "Chef is preparing your order")
        order.update_order_status(OrderStatus.OUT_FOR_DELIVERY, 
                                 f"{order.delivery_partner.name} picked up your order")
        
        # Show tracking info
        order.tracking.display_tracking_info()
        
        # Complete the order
        order.complete_order()
        
        # View updated wallet
        customer.view_wallet()
    
    print("\n" + "*"*30)
    print(" "*25 + "DEMO COMPLETED")
    print("*"*30 + "\n")


if __name__ == "__main__":
    main()
