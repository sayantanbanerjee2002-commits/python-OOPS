"""
HOTEL RESERVATION PLATFORM
Complete implementation with dynamic pricing, reviews, and booking management
"""

from datetime import datetime, timedelta
from enum import Enum
import random
import string


# ======================== ENUMERATIONS ========================

class RoomType(Enum):
    """Room categories"""
    SINGLE = "Single"
    DOUBLE = "Double"
    SUITE = "Suite"


class BookingStatus(Enum):
    """Booking lifecycle states"""
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class PaymentStatus(Enum):
    """Payment transaction states"""
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"
    REFUNDED = "Refunded"


class PaymentMethod(Enum):
    """Supported payment methods"""
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    PAYPAL = "PayPal"
    BANK_TRANSFER = "Bank Transfer"


class LoyaltyTier(Enum):
    """Customer loyalty tiers with discount rates"""
    BRONZE = ("Bronze", 0.05)    # 5% discount
    SILVER = ("Silver", 0.10)    # 10% discount
    GOLD = ("Gold", 0.15)        # 15% discount
    PLATINUM = ("Platinum", 0.20) # 20% discount
    
    def __init__(self, tier_name, discount_rate):
        self.tier_name = tier_name
        self.discount_rate = discount_rate


class Season(Enum):
    """Seasonal pricing multipliers"""
    LOW_SEASON = ("Low Season", 0.85)      # 15% discount
    REGULAR = ("Regular Season", 1.0)      # No change
    HIGH_SEASON = ("High Season", 1.15)    # 15% increase
    PEAK_SEASON = ("Peak Season", 1.30)    # 30% increase
    
    def __init__(self, season_name, price_multiplier):
        self.season_name = season_name
        self.price_multiplier = price_multiplier


# ======================== RATING SYSTEM ========================

class Rating:
    """Customer review with rating score, comment, and hotel response"""
    
    def __init__(self, booking, score, comment):
        """
        Create a new rating
        
        Args:
            booking: Associated booking object
            score: Rating score (1-5)
            comment: Review text
        """
        if not isinstance(score, (int, float)) or not (1 <= score <= 5):
            raise ValueError("Rating score must be between 1 and 5")
        
        self.booking = booking
        self.score = score
        self.comment = comment
        self.created_at = datetime.now()
        self.hotel_response = None
        self.response_date = None
    
    def add_hotel_response(self, response_text):
        """Hotel management responds to customer review"""
        self.hotel_response = response_text
        self.response_date = datetime.now()
        print(f"✅ Response added to review by {self.booking.customer.name}")
    
    def __str__(self):
        stars = "⭐" * int(self.score)
        response_info = ""
        if self.hotel_response:
            response_info = f"\n      Hotel Response: {self.hotel_response}"
        return (f"{stars} ({self.score}/5) - {self.comment}\n"
                f"      By: {self.booking.customer.name} on {self.created_at.strftime('%Y-%m-%d')}"
                f"{response_info}")


# ======================== ROOM CLASS ========================

class Room:
    """Hotel room with availability tracking and booking management"""
    
    def __init__(self, room_number, room_type, price_per_night):
        """
        Initialize a hotel room
        
        Args:
            room_number: Unique room identifier within hotel
            room_type: RoomType enum (SINGLE/DOUBLE/SUITE)
            price_per_night: Base nightly rate
        """
        self.room_number = room_number
        self.room_type = room_type
        self.price_per_night = price_per_night
        self.is_available = True
        self.bookings = []  # All bookings for this room
    
    def check_availability(self, check_in_date, check_out_date):
        """
        Verify room availability for specified date range
        
        Args:
            check_in_date: Proposed check-in date
            check_out_date: Proposed check-out date
            
        Returns:
            bool: True if available, False if conflict exists
        """
        for booking in self.bookings:
            # Skip cancelled bookings
            if booking.status == BookingStatus.CANCELLED:
                continue
            
            # Check for date overlap
            # Overlap exists if: new_start < existing_end AND new_end > existing_start
            if (check_in_date < booking.check_out_date and 
                check_out_date > booking.check_in_date):
                return False
        
        return True
    
    def get_bookings_in_range(self, start_date, end_date):
        """Get all active bookings within date range"""
        active_bookings = []
        for booking in self.bookings:
            if booking.status != BookingStatus.CANCELLED:
                if (booking.check_in_date < end_date and 
                    booking.check_out_date > start_date):
                    active_bookings.append(booking)
        return active_bookings
    
    def __str__(self):
        status = "✓ Available" if self.is_available else "✗ Occupied"
        return (f"Room {self.room_number} - {self.room_type.value} "
                f"(${self.price_per_night}/night) [{status}]")
    
    def __repr__(self):
        return f"Room({self.room_number}, {self.room_type.value}, ${self.price_per_night})"


# ======================== HOTEL CLASS ========================

class Hotel:
    """Hotel with rooms, amenities, location, and rating system"""
    
    all_hotels = []  # Class variable: registry of all hotels
    
    def __init__(self, name, location, star_rating, amenities_list):
        """
        Create a new hotel
        
        Args:
            name: Hotel name
            location: Geographic location (city, country)
            star_rating: Star rating (1-5)
            amenities_list: List of amenities (e.g., ["Pool", "Gym", "WiFi"])
        """
        if not (1 <= star_rating <= 5):
            raise ValueError("Star rating must be between 1 and 5")
        
        self.name = name
        self.location = location
        self.star_rating = star_rating
        self.amenities_list = amenities_list
        self.rooms_list = []  # Composition: Hotel owns rooms
        self.ratings = []
        
        # Register hotel in global registry
        Hotel.all_hotels.append(self)
    
    def add_room(self, room):
        """Add room to hotel (composition relationship)"""
        if room not in self.rooms_list:
            self.rooms_list.append(room)
            print(f"✅ Added {room} to {self.name}")
    
    def remove_room(self, room_number):
        """Remove room from hotel"""
        for room in self.rooms_list:
            if room.room_number == room_number:
                self.rooms_list.remove(room)
                print(f"✅ Removed Room {room_number} from {self.name}")
                return
        print(f"❌ Room {room_number} not found")
    
    def find_available_rooms(self, check_in_date, check_out_date, room_type=None):
        """
        Find available rooms for date range with optional type filter
        
        Args:
            check_in_date: Desired check-in date
            check_out_date: Desired check-out date
            room_type: Optional RoomType filter
            
        Returns:
            list: Available Room objects
        """
        available_rooms = []
        
        for room in self.rooms_list:
            # Filter by room type if specified
            if room_type and room.room_type != room_type:
                continue
            
            # Check date availability
            if room.check_availability(check_in_date, check_out_date):
                available_rooms.append(room)
        
        return available_rooms
    
    def add_rating(self, rating):
        """Add customer rating to hotel"""
        self.ratings.append(rating)
    
    def get_average_rating(self):
        """Calculate average rating score"""
        if not self.ratings:
            return 0.0
        return round(sum(r.score for r in self.ratings) / len(self.ratings), 2)
    
    def get_rating_distribution(self):
        """Get count of each rating score (1-5)"""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in self.ratings:
            distribution[int(rating.score)] += 1
        return distribution
    
    @classmethod
    def find_hotels(cls, location=None, min_price=None, max_price=None, min_rating=None):
        """
        Search hotels by location, price range, and minimum rating
        
        Args:
            location: Location keyword (case-insensitive)
            min_price: Minimum room price
            max_price: Maximum room price
            min_rating: Minimum average rating
            
        Returns:
            list: Matching Hotel objects
        """
        results = []
        
        for hotel in cls.all_hotels:
            # Filter by location
            if location and location.lower() not in hotel.location.lower():
                continue
            
            # Filter by minimum rating
            if min_rating and hotel.get_average_rating() < min_rating:
                continue
            
            # Filter by price range
            if hotel.rooms_list:
                min_room_price = min(room.price_per_night for room in hotel.rooms_list)
                
                if min_price and min_room_price < min_price:
                    continue
                if max_price and min_room_price > max_price:
                    continue
            
            results.append(hotel)
        
        return results
    
    def display_info(self):
        """Display comprehensive hotel information"""
        stars = "⭐" * self.star_rating
        avg_rating = self.get_average_rating()
        
        print(f"\n{'='*60}")
        print(f"🏨 {self.name} {stars}")
        print(f"{'='*60}")
        print(f"📍 Location: {self.location}")
        print(f"⭐ Average Rating: {avg_rating}/5 ({len(self.ratings)} reviews)")
        print(f"🛏️  Total Rooms: {len(self.rooms_list)}")
        print(f"✨ Amenities: {', '.join(self.amenities_list)}")
        
        if self.rooms_list:
            print(f"\n{'Rooms:':-^60}")
            for room in self.rooms_list:
                print(f"  {room}")
    
    def __str__(self):
        stars = "⭐" * self.star_rating
        avg = self.get_average_rating()
        return f"{self.name} {stars} - {self.location} (Rating: {avg}/5)"
    
    def __repr__(self):
        return f"Hotel({self.name}, {self.location})"


# ======================== CUSTOMER CLASS ========================

class Customer:
    """Customer with booking history and loyalty program"""
    
    def __init__(self, name, email, phone, loyalty_tier=LoyaltyTier.BRONZE):
        """
        Create a new customer
        
        Args:
            name: Full name
            email: Email address
            phone: Phone number
            loyalty_tier: Initial loyalty tier (default: BRONZE)
        """
        self.name = name
        self.email = email
        self.phone = phone
        self.booking_history = []  # Association: independent existence
        self.loyalty_tier = loyalty_tier
        self.created_at = datetime.now()
    
    def add_booking(self, booking):
        """Add booking to customer history"""
        self.booking_history.append(booking)
    
    def get_completed_bookings_count(self):
        """Count completed stays (for loyalty tier upgrades)"""
        return sum(1 for b in self.booking_history 
                  if b.status == BookingStatus.COMPLETED)
    
    def get_total_spending(self):
        """Calculate total amount spent on completed bookings"""
        return sum(b.total_cost for b in self.booking_history 
                  if b.status == BookingStatus.COMPLETED)
    
    def upgrade_loyalty_tier(self):
        """Automatically upgrade loyalty tier based on completed bookings"""
        completed = self.get_completed_bookings_count()
        
        if completed >= 20:
            self.loyalty_tier = LoyaltyTier.PLATINUM
        elif completed >= 10:
            self.loyalty_tier = LoyaltyTier.GOLD
        elif completed >= 5:
            self.loyalty_tier = LoyaltyTier.SILVER
        else:
            self.loyalty_tier = LoyaltyTier.BRONZE
    
    def display_profile(self):
        """Display customer profile with statistics"""
        print(f"\n{'='*60}")
        print(f"👤 Customer Profile: {self.name}")
        print(f"{'='*60}")
        print(f"📧 Email: {self.email}")
        print(f"📱 Phone: {self.phone}")
        print(f"🏆 Loyalty Tier: {self.loyalty_tier.tier_name} ({self.loyalty_tier.discount_rate*100}% discount)")
        print(f"📊 Total Bookings: {len(self.booking_history)}")
        print(f"✅ Completed Stays: {self.get_completed_bookings_count()}")
        print(f"💰 Total Spending: ${self.get_total_spending():.2f}")
    
    def __str__(self):
        return f"{self.name} ({self.loyalty_tier.tier_name}) - {len(self.booking_history)} bookings"
    
    def __repr__(self):
        return f"Customer({self.name}, {self.email})"


# ======================== BOOKING CLASS ========================

class Booking:
    """Booking with dynamic pricing, availability checking, and lifecycle management"""
    
    confirmation_counter = 1000  # Class variable for unique confirmation numbers
    
    # Cancellation policy thresholds (days before check-in)
    FULL_REFUND_DAYS = 14
    PARTIAL_REFUND_DAYS = 7
    PARTIAL_REFUND_PERCENTAGE = 0.50
    
    # Weekend surcharge rate
    WEEKEND_SURCHARGE_RATE = 0.20  # 20% extra for Friday/Saturday
    
    def __init__(self, customer, room, check_in_date, check_out_date, 
                 season=Season.REGULAR):
        """
        Create a new booking with dynamic pricing
        
        Args:
            customer: Customer object
            room: Room object
            check_in_date: Check-in datetime
            check_out_date: Check-out datetime
            season: Season enum for seasonal pricing
        """
        # Validate dates
        if check_in_date >= check_out_date:
            raise ValueError("Check-out date must be after check-in date")
        
        if check_in_date < datetime.now():
            raise ValueError("Check-in date cannot be in the past")
        
        # Check room availability
        if not room.check_availability(check_in_date, check_out_date):
            raise ValueError(f"Room {room.room_number} is not available for selected dates")
        
        # Initialize booking attributes
        self.customer = customer
        self.room = room
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.season = season
        self.status = BookingStatus.PENDING
        self.confirmation_number = self._generate_confirmation_number()
        self.payment = None
        self.rating = None
        self.created_at = datetime.now()
        
        # Calculate pricing
        self.base_cost = self._calculate_base_cost()
        self.seasonal_adjustment = self._calculate_seasonal_adjustment()
        self.weekend_surcharge = self._calculate_weekend_surcharge()
        self.loyalty_discount = self._calculate_loyalty_discount()
        self.total_cost = self._calculate_total_cost()
        
        # Establish relationships
        room.bookings.append(self)
        customer.add_booking(self)
        
        print(f"✅ Booking created: {self.confirmation_number}")
    
    def _generate_confirmation_number(self):
        """Generate unique confirmation number (format: BK####XXX)"""
        Booking.confirmation_counter += 1
        random_suffix = ''.join(random.choices(string.ascii_uppercase, k=3))
        return f"BK{Booking.confirmation_counter:04d}{random_suffix}"
    
    def get_number_of_nights(self):
        """Calculate number of nights in booking"""
        return (self.check_out_date - self.check_in_date).days
    
    def _calculate_base_cost(self):
        """Calculate base cost (nights × room price)"""
        nights = self.get_number_of_nights()
        return self.room.price_per_night * nights
    
    def _calculate_seasonal_adjustment(self):
        """Calculate seasonal price adjustment"""
        base = self._calculate_base_cost()
        adjusted = base * self.season.price_multiplier
        return adjusted - base  # Return the adjustment amount
    
    def _calculate_weekend_surcharge(self):
        """Calculate surcharge for weekend nights (Friday & Saturday)"""
        weekend_nights = 0
        current_date = self.check_in_date
        nights = self.get_number_of_nights()
        
        for _ in range(nights):
            # weekday(): Monday=0, Friday=4, Saturday=5, Sunday=6
            if current_date.weekday() in [4, 5]:  # Friday or Saturday
                weekend_nights += 1
            current_date += timedelta(days=1)
        
        return weekend_nights * self.room.price_per_night * self.WEEKEND_SURCHARGE_RATE
    
    def _calculate_loyalty_discount(self):
        """Calculate loyalty discount on total before discount"""
        subtotal = (self.base_cost + 
                   self._calculate_seasonal_adjustment() + 
                   self._calculate_weekend_surcharge())
        return subtotal * self.customer.loyalty_tier.discount_rate
    
    def _calculate_total_cost(self):
        """Calculate final total cost with all adjustments"""
        total = (self.base_cost + 
                self.seasonal_adjustment + 
                self.weekend_surcharge - 
                self.loyalty_discount)
        return round(total, 2)
    
    def get_pricing_breakdown(self):
        """Return detailed pricing breakdown"""
        nights = self.get_number_of_nights()
        return {
            'nights': nights,
            'room_rate': self.room.price_per_night,
            'base_cost': self.base_cost,
            'seasonal_adjustment': self.seasonal_adjustment,
            'weekend_surcharge': self.weekend_surcharge,
            'subtotal': self.base_cost + self.seasonal_adjustment + self.weekend_surcharge,
            'loyalty_discount': self.loyalty_discount,
            'total_cost': self.total_cost
        }
    
    def display_pricing_breakdown(self):
        """Print formatted pricing breakdown"""
        breakdown = self.get_pricing_breakdown()
        
        print(f"\n{'Pricing Breakdown':-^50}")
        print(f"Base Rate: ${self.room.price_per_night}/night × {breakdown['nights']} nights = ${breakdown['base_cost']:.2f}")
        
        if breakdown['seasonal_adjustment'] != 0:
            sign = '+' if breakdown['seasonal_adjustment'] > 0 else ''
            print(f"Seasonal Adjustment ({self.season.season_name}): {sign}${breakdown['seasonal_adjustment']:.2f}")
        
        if breakdown['weekend_surcharge'] > 0:
            print(f"Weekend Surcharge: +${breakdown['weekend_surcharge']:.2f}")
        
        print(f"Subtotal: ${breakdown['subtotal']:.2f}")
        
        if breakdown['loyalty_discount'] > 0:
            print(f"Loyalty Discount ({self.customer.loyalty_tier.tier_name}): -${breakdown['loyalty_discount']:.2f}")
        
        print(f"{'-'*50}")
        print(f"Total Cost: ${breakdown['total_cost']:.2f}")
    
    def confirm_booking(self):
        """Confirm booking after successful payment"""
        if self.status == BookingStatus.CONFIRMED:
            print("Booking already confirmed")
            return
        
        self.status = BookingStatus.CONFIRMED
        print(f"✅ Booking confirmed! Confirmation Number: {self.confirmation_number}")
    
    def cancel_booking(self):
        """
        Cancel booking with refund calculation based on cancellation policy
        
        Returns:
            float: Refund amount
        """
        if self.status == BookingStatus.CANCELLED:
            print("❌ Booking already cancelled")
            return 0.0
        
        if self.status == BookingStatus.COMPLETED:
            print("❌ Cannot cancel completed booking")
            return 0.0
        
        # Calculate days until check-in
        days_until_checkin = (self.check_in_date - datetime.now()).days
        
        # Determine refund percentage based on cancellation policy
        if days_until_checkin > self.FULL_REFUND_DAYS:
            refund_percentage = 1.0  # 100% refund
            policy = f"Full refund (>{self.FULL_REFUND_DAYS} days notice)"
        elif days_until_checkin >= self.PARTIAL_REFUND_DAYS:
            refund_percentage = self.PARTIAL_REFUND_PERCENTAGE  # 50% refund
            policy = f"Partial refund ({self.PARTIAL_REFUND_PERCENTAGE*100}% - {self.PARTIAL_REFUND_DAYS}-{self.FULL_REFUND_DAYS} days notice)"
        else:
            refund_percentage = 0.0  # No refund
            policy = f"No refund (<{self.PARTIAL_REFUND_DAYS} days notice)"
        
        refund_amount = self.total_cost * refund_percentage
        
        # Update status
        self.status = BookingStatus.CANCELLED
        
        # Update payment status if exists
        if self.payment:
            if refund_amount > 0:
                self.payment.status = PaymentStatus.REFUNDED
        
        print(f"\n{'Cancellation Summary':-^50}")
        print(f"Booking: {self.confirmation_number}")
        print(f"Original Cost: ${self.total_cost:.2f}")
        print(f"Days Until Check-in: {days_until_checkin}")
        print(f"Policy: {policy}")
        print(f"Refund Amount: ${refund_amount:.2f}")
        print(f"{'-'*50}")
        
        return refund_amount
    
    def complete_booking(self):
        """Mark booking as completed (after checkout)"""
        if self.status != BookingStatus.CONFIRMED:
            print("❌ Can only complete confirmed bookings")
            return
        
        self.status = BookingStatus.COMPLETED
        self.customer.upgrade_loyalty_tier()  # Check for tier upgrade
        print(f"✅ Booking {self.confirmation_number} completed. Thank you for staying!")
    
    def add_rating(self, score, comment):
        """
        Add rating after completed stay
        
        Args:
            score: Rating score (1-5)
            comment: Review text
            
        Returns:
            Rating: Created rating object
        """
        if self.status != BookingStatus.COMPLETED:
            raise ValueError("Can only rate completed bookings")
        
        if self.rating:
            print("⚠️  This booking already has a rating")
            return self.rating
        
        self.rating = Rating(self, score, comment)
        
        # Add rating to hotel
        for hotel in Hotel.all_hotels:
            if self.room in hotel.rooms_list:
                hotel.add_rating(self.rating)
                break
        
        print(f"✅ Rating added successfully!")
        return self.rating
    
    def __str__(self):
        return (f"Booking {self.confirmation_number} | "
                f"{self.customer.name} | "
                f"Room {self.room.room_number} | "
                f"{self.check_in_date.strftime('%Y-%m-%d')} to {self.check_out_date.strftime('%Y-%m-%d')} | "
                f"${self.total_cost:.2f} | "
                f"[{self.status.value}]")
    
    def __repr__(self):
        return f"Booking({self.confirmation_number}, {self.customer.name})"


# ======================== PAYMENT CLASS ========================

class Payment:
    """Payment transaction processing and tracking"""
    
    def __init__(self, booking, payment_method):
        """
        Create payment for booking
        
        Args:
            booking: Associated Booking object
            payment_method: PaymentMethod enum
        """
        self.booking = booking
        self.amount = booking.total_cost
        self.payment_method = payment_method
        self.transaction_id = self._generate_transaction_id()
        self.status = PaymentStatus.PENDING
        self.created_at = datetime.now()
        self.completed_at = None
        
        # Link payment to booking
        booking.payment = self
    
    def _generate_transaction_id(self):
        """Generate unique transaction ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_num = random.randint(1000, 9999)
        return f"TXN{timestamp}{random_num}"
    
    def process_payment(self):
        """
        Process payment transaction
        
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"\n{'Processing Payment':-^50}")
        print(f"Amount: ${self.amount:.2f}")
        print(f"Method: {self.payment_method.value}")
        print(f"Transaction ID: {self.transaction_id}")
        print("Processing...", end=" ")
        
        # Simulate payment processing (90% success rate)
        import time
        time.sleep(1)  # Simulate network delay
        
        if random.random() < 0.9:  # 90% success rate
            self.status = PaymentStatus.COMPLETED
            self.completed_at = datetime.now()
            self.booking.confirm_booking()
            print("✅ SUCCESS")
            print(f"{'-'*50}")
            return True
        else:
            self.status = PaymentStatus.FAILED
            print("❌ FAILED")
            print("Please try again or use a different payment method")
            print(f"{'-'*50}")
            return False
    
    def refund(self, amount):
        """Process refund transaction"""
        if self.status != PaymentStatus.COMPLETED:
            print("❌ Cannot refund: Payment not completed")
            return False
        
        if amount > self.amount:
            print("❌ Refund amount exceeds payment amount")
            return False
        
        self.status = PaymentStatus.REFUNDED
        print(f"✅ Refunded ${amount:.2f} to {self.payment_method.value}")
        return True
    
    def __str__(self):
        return (f"Payment {self.transaction_id} | "
                f"${self.amount:.2f} via {self.payment_method.value} | "
                f"[{self.status.value}]")
    
    def __repr__(self):
        return f"Payment({self.transaction_id}, ${self.amount:.2f})"


# ======================== DEMONSTRATION ========================

def main():
    """Comprehensive demonstration of the hotel reservation system"""
    
    print("\n" + "="*70)
    print(" "*20 + "🏨 HOTEL RESERVATION SYSTEM")
    print("="*70)
    
    # ========== STEP 1: Create Hotels ==========
    print("\n" + "="*70)
    print("STEP 1: Creating Hotels")
    print("="*70)
    
    hotel_paris = Hotel(
        "Le Grand Palace",
        "Paris, France",
        5,
        ["Pool", "Spa", "Restaurant", "Gym", "WiFi", "Room Service"]
    )
    
    hotel_london = Hotel(
        "Thames View Hotel",
        "London, UK",
        4,
        ["WiFi", "Restaurant", "Bar", "Concierge"]
    )
    
    hotel_budget = Hotel(
        "Budget Stay Inn",
        "Paris, France",
        3,
        ["WiFi", "Parking"]
    )
    
    # ========== STEP 2: Add Rooms ==========
    print("\n" + "="*70)
    print("STEP 2: Adding Rooms to Hotels")
    print("="*70)
    
    # Le Grand Palace rooms
    hotel_paris.add_room(Room(101, RoomType.SINGLE, 120))
    hotel_paris.add_room(Room(102, RoomType.SINGLE, 120))
    hotel_paris.add_room(Room(201, RoomType.DOUBLE, 180))
    hotel_paris.add_room(Room(202, RoomType.DOUBLE, 180))
    hotel_paris.add_room(Room(301, RoomType.SUITE, 350))
    hotel_paris.add_room(Room(302, RoomType.SUITE, 350))
    
    # Thames View Hotel rooms
    hotel_london.add_room(Room(101, RoomType.SINGLE, 100))
    hotel_london.add_room(Room(102, RoomType.DOUBLE, 150))
    hotel_london.add_room(Room(201, RoomType.SUITE, 280))
    
    # Budget Stay Inn rooms
    hotel_budget.add_room(Room(101, RoomType.SINGLE, 60))
    hotel_budget.add_room(Room(102, RoomType.DOUBLE, 85))
    
    # ========== STEP 3: Create Customers ==========
    print("\n" + "="*70)
    print("STEP 3: Creating Customers")
    print("="*70)
    
    customer_john = Customer(
        "John Smith",
        "john.smith@email.com",
        "+1-555-0101",
        LoyaltyTier.GOLD
    )
    print(f"Created: {customer_john}")
    
    customer_emma = Customer(
        "Emma Johnson",
        "emma.j@email.com",
        "+1-555-0202",
        LoyaltyTier.BRONZE
    )
    print(f"Created: {customer_emma}")
    
    customer_alice = Customer(
        "Alice Williams",
        "alice.w@email.com",
        "+44-20-1234-5678",
        LoyaltyTier.PLATINUM
    )
    print(f"Created: {customer_alice}")
    
    # ========== STEP 4: Search Hotels ==========
    print("\n" + "="*70)
    print("STEP 4: Searching Hotels")
    print("="*70)
    
    print("\n🔍 Search: Hotels in Paris with price range $50-$200")
    print("-" * 70)
    results = Hotel.find_hotels(location="Paris", min_price=50, max_price=200)
    for hotel in results:
        print(f"  {hotel}")
        print(f"     Rooms from: ${min(r.price_per_night for r in hotel.rooms_list)}/night")
    
    print("\n🔍 Search: All 5-star hotels")
    print("-" * 70)
    five_star = [h for h in Hotel.all_hotels if h.star_rating == 5]
    for hotel in five_star:
        print(f"  {hotel}")
    
    # ========== STEP 5: Check Availability ==========
    print("\n" + "="*70)
    print("STEP 5: Checking Room Availability")
    print("="*70)
    
    check_in_1 = datetime.now() + timedelta(days=15)  # 15 days from now
    check_out_1 = datetime.now() + timedelta(days=18)  # 3 nights
    
    print(f"\n📅 Date Range: {check_in_1.strftime('%Y-%m-%d')} to {check_out_1.strftime('%Y-%m-%d')}")
    print(f"   (3 nights, {check_in_1.strftime('%A')} to {check_out_1.strftime('%A')})")
    
    available = hotel_paris.find_available_rooms(check_in_1, check_out_1, RoomType.SUITE)
    print(f"\n✅ Available Suites at {hotel_paris.name}:")
    for room in available:
        print(f"   {room}")
    
    # ========== STEP 6: Create Booking with Dynamic Pricing ==========
    print("\n" + "="*70)
    print("STEP 6: Creating Booking with Dynamic Pricing")
    print("="*70)
    
    suite_room = hotel_paris.rooms_list[4]  # Suite 301
    
    print(f"\n🛏️  Selected Room: {suite_room}")
    print(f"👤 Customer: {customer_john.name} ({customer_john.loyalty_tier.tier_name})")
    print(f"📅 Check-in: {check_in_1.strftime('%Y-%m-%d %A')}")
    print(f"📅 Check-out: {check_out_1.strftime('%Y-%m-%d %A')}")
    print(f"🌞 Season: PEAK_SEASON (Summer vacation)")
    
    try:
        booking_1 = Booking(
            customer_john,
            suite_room,
            check_in_1,
            check_out_1,
            Season.PEAK_SEASON
        )
        
        print(f"\n{booking_1}")
        booking_1.display_pricing_breakdown()
        
    except ValueError as e:
        print(f"❌ Error: {e}")
    
    # ========== STEP 7: Process Payment ==========
    print("\n" + "="*70)
    print("STEP 7: Processing Payment")
    print("="*70)
    
    payment_1 = Payment(booking_1, PaymentMethod.CREDIT_CARD)
    success = payment_1.process_payment()
    
    if success:
        print(f"\n📧 Confirmation email sent to {customer_john.email}")
        print(f"🎫 Confirmation Number: {booking_1.confirmation_number}")
    
    # ========== STEP 8: Create Another Booking (Different Customer) ==========
    print("\n" + "="*70)
    print("STEP 8: Second Booking - Weekend Stay")
    print("="*70)
    
    # Book for a weekend (includes Friday and Saturday)
    check_in_2 = datetime.now() + timedelta(days=10)
    # Make sure it's a Friday
    while check_in_2.weekday() != 4:  # 4 = Friday
        check_in_2 += timedelta(days=1)
    check_out_2 = check_in_2 + timedelta(days=2)  # Friday to Sunday (2 nights)
    
    print(f"\n📅 Weekend Stay: {check_in_2.strftime('%Y-%m-%d %A')} to {check_out_2.strftime('%Y-%m-%d %A')}")
    print(f"👤 Customer: {customer_emma.name} ({customer_emma.loyalty_tier.tier_name})")
    
    double_room = hotel_paris.rooms_list[2]  # Double room 201
    
    try:
        booking_2 = Booking(
            customer_emma,
            double_room,
            check_in_2,
            check_out_2,
            Season.REGULAR
        )
        
        print(f"\n{booking_2}")
        booking_2.display_pricing_breakdown()
        
        payment_2 = Payment(booking_2, PaymentMethod.PAYPAL)
        payment_2.process_payment()
        
    except ValueError as e:
        print(f"❌ Error: {e}")
    
    # ========== STEP 9: Test Double Booking Prevention ==========
    print("\n" + "="*70)
    print("STEP 9: Testing Double Booking Prevention")
    print("="*70)
    
    print(f"\n⚠️  Attempting to book Suite 301 (already booked for {check_in_1.strftime('%Y-%m-%d')} to {check_out_1.strftime('%Y-%m-%d')})")
    print(f"   New request: {(check_in_1 + timedelta(days=1)).strftime('%Y-%m-%d')} to {(check_out_1 + timedelta(days=1)).strftime('%Y-%m-%d')} (overlapping dates)")
    
    try:
        booking_fail = Booking(
            customer_alice,
            suite_room,
            check_in_1 + timedelta(days=1),  # Overlapping dates
            check_out_1 + timedelta(days=1),
            Season.REGULAR
        )
    except ValueError as e:
        print(f"✅ System correctly prevented double booking!")
        print(f"   Error message: {e}")
    
    # ========== STEP 10: Test Cancellation Policy ==========
    print("\n" + "="*70)
    print("STEP 10: Testing Cancellation Policies")
    print("="*70)
    
    # Scenario A: Cancel with 20 days notice (full refund)
    print("\n📋 Scenario A: Cancellation with 20 days notice")
    check_in_cancel_1 = datetime.now() + timedelta(days=20)
    check_out_cancel_1 = check_in_cancel_1 + timedelta(days=2)
    
    booking_cancel_1 = Booking(
        customer_alice,
        hotel_paris.rooms_list[0],  # Single room
        check_in_cancel_1,
        check_out_cancel_1,
        Season.REGULAR
    )
    
    payment_cancel_1 = Payment(booking_cancel_1, PaymentMethod.CREDIT_CARD)
    payment_cancel_1.process_payment()
    
    print(f"\n🎫 Booking: {booking_cancel_1.confirmation_number}")
    print(f"💰 Original cost: ${booking_cancel_1.total_cost:.2f}")
    refund_1 = booking_cancel_1.cancel_booking()
    
    # Scenario B: Cancel with 10 days notice (partial refund)
    print("\n\n📋 Scenario B: Cancellation with 10 days notice")
    check_in_cancel_2 = datetime.now() + timedelta(days=10)
    check_out_cancel_2 = check_in_cancel_2 + timedelta(days=3)
    
    booking_cancel_2 = Booking(
        customer_alice,
        hotel_london.rooms_list[1],  # Double room
        check_in_cancel_2,
        check_out_cancel_2,
        Season.REGULAR
    )
    
    payment_cancel_2 = Payment(booking_cancel_2, PaymentMethod.DEBIT_CARD)
    payment_cancel_2.process_payment()
    
    print(f"\n🎫 Booking: {booking_cancel_2.confirmation_number}")
    print(f"💰 Original cost: ${booking_cancel_2.total_cost:.2f}")
    refund_2 = booking_cancel_2.cancel_booking()
    
    # Scenario C: Cancel with 3 days notice (no refund)
    print("\n\n📋 Scenario C: Cancellation with 3 days notice")
    check_in_cancel_3 = datetime.now() + timedelta(days=3)
    check_out_cancel_3 = check_in_cancel_3 + timedelta(days=2)
    
    booking_cancel_3 = Booking(
        customer_emma,
        hotel_budget.rooms_list[0],
        check_in_cancel_3,
        check_out_cancel_3,
        Season.REGULAR
    )
    
    payment_cancel_3 = Payment(booking_cancel_3, PaymentMethod.CREDIT_CARD)
    payment_cancel_3.process_payment()
    
    print(f"\n🎫 Booking: {booking_cancel_3.confirmation_number}")
    print(f"💰 Original cost: ${booking_cancel_3.total_cost:.2f}")
    refund_3 = booking_cancel_3.cancel_booking()
    
    # ========== STEP 11: Complete Booking & Add Reviews ==========
    print("\n" + "="*70)
    print("STEP 11: Completing Stay & Adding Reviews")
    print("="*70)
    
    print("\n✅ Simulating checkout for booking 1...")
    booking_1.complete_booking()
    
    print(f"\n⭐ {customer_john.name} adding review...")
    rating_1 = booking_1.add_rating(
        5,
        "Absolutely magnificent stay! The suite was luxurious, staff was incredibly friendly, "
        "and the amenities were top-notch. The spa was especially relaxing. Will definitely return!"
    )
    
    print("\n✅ Simulating checkout for booking 2...")
    booking_2.complete_booking()
    
    print(f"\n⭐ {customer_emma.name} adding review...")
    rating_2 = booking_2.add_rating(
        4,
        "Great hotel with excellent location. Room was clean and comfortable. "
        "Only minor issue was some noise from the street, but overall very satisfied."
    )
    
    # ========== STEP 12: Hotel Responds to Reviews ==========
    print("\n" + "="*70)
    print("STEP 12: Hotel Management Responding to Reviews")
    print("="*70)
    
    print(f"\n🏨 {hotel_paris.name} management responding to reviews...")
    rating_1.add_hotel_response(
        "Thank you so much for your wonderful review! We're thrilled you enjoyed "
        "your stay and our spa facilities. We look forward to welcoming you back soon!"
    )
    
    rating_2.add_hotel_response(
        "Thank you for your feedback! We're glad you enjoyed your stay. "
        "We apologize for the street noise and will look into better soundproofing. "
        "We appreciate your understanding and hope to see you again."
    )
    
    # ========== STEP 13: Display Hotel Information with Reviews ==========
    print("\n" + "="*70)
    print("STEP 13: Hotel Information & Reviews")
    print("="*70)
    
    hotel_paris.display_info()
    
    if hotel_paris.ratings:
        print(f"\n{'Customer Reviews':-^60}")
        for rating in hotel_paris.ratings:
            print(f"\n{rating}")
        
        distribution = hotel_paris.get_rating_distribution()
        print(f"\n{'Rating Distribution':-^60}")
        for score in range(5, 0, -1):
            stars = "⭐" * score
            bar = "█" * distribution[score]
            print(f"{stars} ({score}): {bar} ({distribution[score]} reviews)")
    
    # ========== STEP 14: Display Customer Profiles ==========
    print("\n" + "="*70)
    print("STEP 14: Customer Profiles & Statistics")
    print("="*70)
    
    customer_john.display_profile()
    customer_emma.display_profile()
    customer_alice.display_profile()
    
    # ========== STEP 15: Low Season Booking ==========
    print("\n" + "="*70)
    print("STEP 15: Low Season Booking (Discount Pricing)")
    print("="*70)
    
    check_in_low = datetime.now() + timedelta(days=60)  # 2 months ahead (off-season)
    check_out_low = check_in_low + timedelta(days=5)  # 5-night stay
    
    print(f"\n🍂 Low Season Booking")
    print(f"📅 {check_in_low.strftime('%Y-%m-%d')} to {check_out_low.strftime('%Y-%m-%d')} (5 nights)")
    print(f"👤 Customer: {customer_alice.name} ({customer_alice.loyalty_tier.tier_name})")
    
    booking_low = Booking(
        customer_alice,
        hotel_london.rooms_list[2],  # Suite
        check_in_low,
        check_out_low,
        Season.LOW_SEASON
    )
    
    print(f"\n{booking_low}")
    booking_low.display_pricing_breakdown()
    
    payment_low = Payment(booking_low, PaymentMethod.BANK_TRANSFER)
    payment_low.process_payment()
    
    # ========== STEP 16: System Summary ==========
    print("\n" + "="*70)
    print("STEP 16: System Summary")
    print("="*70)
    
    print(f"\n📊 SYSTEM STATISTICS")
    print("-" * 70)
    print(f"Total Hotels: {len(Hotel.all_hotels)}")
    print(f"Total Rooms: {sum(len(h.rooms_list) for h in Hotel.all_hotels)}")
    print(f"Total Customers: {len([customer_john, customer_emma, customer_alice])}")
    
    all_bookings = customer_john.booking_history + customer_emma.booking_history + customer_alice.booking_history
    confirmed = sum(1 for b in all_bookings if b.status == BookingStatus.CONFIRMED)
    completed = sum(1 for b in all_bookings if b.status == BookingStatus.COMPLETED)
    cancelled = sum(1 for b in all_bookings if b.status == BookingStatus.CANCELLED)
    
    print(f"\nTotal Bookings: {len(all_bookings)}")
    print(f"  ✅ Confirmed: {confirmed}")
    print(f"  ✓  Completed: {completed}")
    print(f"  ✗  Cancelled: {cancelled}")
    
    total_revenue = sum(b.total_cost for b in all_bookings 
                       if b.status in [BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
    print(f"\n💰 Total Revenue: ${total_revenue:.2f}")
    
    print(f"\n⭐ Average Hotel Rating: {hotel_paris.get_average_rating()}/5 "
          f"({len(hotel_paris.ratings)} reviews)")
    
    # ========== STEP 17: Advanced Search Examples ==========
    print("\n" + "="*70)
    print("STEP 17: Advanced Search Examples")
    print("="*70)
    
    print("\n🔍 Search: Hotels in Paris with minimum 4-star rating")
    print("-" * 70)
    results = Hotel.find_hotels(location="Paris", min_rating=4.0)
    for hotel in results:
        print(f"  {hotel}")
    
    print("\n🔍 Search: Luxury hotels (5-star)")
    print("-" * 70)
    luxury = [h for h in Hotel.all_hotels if h.star_rating == 5]
    for hotel in luxury:
        hotel.display_info()
    
    # ========== STEP 18: Booking History ==========
    print("\n" + "="*70)
    print("STEP 18: Customer Booking History")
    print("="*70)
    
    print(f"\n📜 {customer_john.name}'s Booking History:")
    print("-" * 70)
    for booking in customer_john.booking_history:
        print(f"  {booking}")
        if booking.rating:
            print(f"     Rating: {'⭐' * int(booking.rating.score)}")
    
    print(f"\n📜 {customer_emma.name}'s Booking History:")
    print("-" * 70)
    for booking in customer_emma.booking_history:
        print(f"  {booking}")
        if booking.rating:
            print(f"     Rating: {'⭐' * int(booking.rating.score)}")
    
    print(f"\n📜 {customer_alice.name}'s Booking History:")
    print("-" * 70)
    for booking in customer_alice.booking_history:
        print(f"  {booking}")
    
    # ========== FINAL SUMMARY ==========
    print("\n" + "="*70)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*70)
    
    print("\n🎯 Features Demonstrated:")
    features = [
        "✓ Hotel and room management (composition)",
        "✓ Customer loyalty tiers with discounts",
        "✓ Dynamic pricing (seasonal, weekend surcharge)",
        "✓ Loyalty discount calculation",
        "✓ Room availability checking",
        "✓ Double booking prevention",
        "✓ Unique confirmation number generation",
        "✓ Payment processing simulation",
        "✓ Cancellation with refund calculation",
        "✓ Review and rating system",
        "✓ Hotel responses to reviews",
        "✓ Hotel search by location and price",
        "✓ Customer booking history tracking",
        "✓ Automatic loyalty tier upgrades"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n" + "="*70)
    print(" " * 15 + "Thank you for using our system!")
    print("="*70 + "\n")


# ======================== ENTRY POINT ========================

if __name__ == "__main__":
    main()