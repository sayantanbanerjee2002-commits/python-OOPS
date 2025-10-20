from abc import ABC, abstractmethod
class Shoppingcart: # Represent the items in shopping cart
    
    def __init__(self):
        """Initialize an empty shopping cart with an empty list of items."""
        self.__items = []  # Private attribute: list of dictionaries with 'name' and 'price'
    
    def add_item(self, item_name, price): # Add item and price into the list
       
        # Validate that price is positive
        if price <= 0:
            print(f"Error: Price must be positive. Cannot add {item_name}.")
            return
        
        # Add item as a dictionary to the cart
        item = {'name': item_name, 'price': price}
        self.__items.append(item)
        print(f"Added {item_name} (${price:.2f}) to cart.")
    
    def remove_item(self, item_name): # remove item from list
     
        # Search for the item in the cart
        for item in self.__items:
            if item['name'] == item_name:
                self.__items.remove(item)
                print(f"Removed {item_name} from cart.")
                return
        
            else:
                print(f"Error: {item_name} not found in cart.")
    
    def calculate_total(self): # calculate Total price
      
        total = sum(item['price'] for item in self.__items)
        return total
    
    def display_cart(self):
        """Display all items currently in the cart."""
        if not self.__items: # negatation logic
            print("Your cart is empty.")
            return
        
        print("\n--- Shopping Cart ---")
        for item in self.__items:
            print(f"  {item['name']}: ${item['price']:.2f}")
        print(f"Subtotal: ${self.calculate_total():.2f}")
        print("---------------------\n")


# ABSTRACT BASE CLASS FOR PAYMENT METHODS


class PaymentMethod(ABC):
    """
    Abstract base class for all payment methods.
    Defines the common interface that all payment methods must implement.
    """
    
    @abstractmethod
    def process_payment(self, amount):
        """
        Abstract method that must be implemented by all child classes.
        
        Args:
            amount (float): The amount to be paid
            
        Returns:
            bool: True if payment successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_payment_details(self):
        """
        Abstract method to display payment method details.
        
        Returns:
            str: String representation of payment details
        """
        pass



# CREDIT CARD PAYMENT METHOD


class CreditCard(PaymentMethod):
    """
    Credit card payment with 2% processing fee.
    """
    
    def __init__(self, card_number, cvv, expiry): # intialize credit card with sensitive information
       
        # Validate inputs
        if not self.__validate_card_number(card_number):
            raise ValueError("Invalid card number. Must be 16 digits.")
        if not self.__validate_cvv(cvv):
            raise ValueError("Invalid CVV. Must be 3 digits.")
        if not self.__validate_expiry(expiry):
            raise ValueError("Invalid expiry date. Use MM/YY format.")
        
        # Private attributes for encapsulation (data hiding)
        self.__card_number = card_number
        self.__cvv = cvv
        self.__expiry = expiry
        self.__processing_fee_rate = 0.02  # 2% fee
    
    def __validate_card_number(self, card_number):
        """Private method to validate card number (16 digits)."""
        return len(card_number) == 16 and card_number.isdigit()
    
    def __validate_cvv(self, cvv):
        """Private method to validate CVV (3 digits)."""
        return len(cvv) == 3 and cvv.isdigit()
    
    def __validate_expiry(self, expiry):
        """Private method to validate expiry date format (MM/YY)."""
        if len(expiry) != 5 or expiry[2] != '/':
            return False
        month, year = expiry.split('/')
        return month.isdigit() and year.isdigit() and 1 <= int(month) <= 12
    
    def process_payment(self, amount): # process payment including credit card
        
        # Calculate total with processing fee
        processing_fee = amount * self.__processing_fee_rate
        total_amount = amount + processing_fee
        
        print(f"\nProcessing Credit Card payment...")
        print(f"Card ending in: {self.__card_number[-4:]}")
        print(f"Subtotal: ${amount:.2f}")
        print(f"Processing Fee (2%): ${processing_fee:.2f}")
        print(f"Total Charged: ${total_amount:.2f}")
        print("✓Payment successful!")
        return True
    
    def get_payment_details(self):
        
        return f"Credit Card ending in {self.__card_number[-4:]}"



# DEBIT CARD PAYMENT METHOD


class DebitCard(PaymentMethod):
    """
    Debit card payment with 1% processing fee.
    """
    
    def __init__(self, card_number, pin): # Intialize debit card with card number and pin
        
        # Validate inputs
        if not self.__validate_card_number(card_number):
            raise ValueError("Invalid card number. Must be 16 digits.")
        if not self.__validate_pin(pin):
            raise ValueError("Invalid PIN. Must be 4 digits.")
        
        # Private attributes
        self.__card_number = card_number
        self.__pin = pin
        self.__processing_fee_rate = 0.01  # 1% fee
    
    def __validate_card_number(self, card_number):
        """Private method to validate card number."""
        return len(card_number) == 16 and card_number.isdigit()
    
    def __validate_pin(self, pin):
        """Private method to validate PIN (4 digits)."""
        return len(pin) == 4 and pin.isdigit()
    
    def process_payment(self, amount): # process payment with debit card including processing fee
       
        # Calculate total with processing fee
        processing_fee = amount * self.__processing_fee_rate
        total_amount = amount + processing_fee
        
        print(f"\nProcessing Debit Card payment...")
        print(f"Card ending in: {self.__card_number[-4:]}")
        print(f"Subtotal: ${amount:.2f}")
        print(f"Processing Fee (1%): ${processing_fee:.2f}")
        print(f"Total Charged: ${total_amount:.2f}")
        print(" Payment successful!")
        return True
    
    def get_payment_details(self):
        return f"Debit Card ending in {self.__card_number[-4:]}"


# DIGITAL WALLET PAYMENT METHOD


class DigitalWallet(PaymentMethod): # Digital wallet payment with no processinf fee
   
    
    def __init__(self, wallet_id, balance): # intialize Digitalwallet with wallet_id and balance
       
        
        # Validate inputs
        if not wallet_id:
            raise ValueError("Wallet ID cannot be empty.")
        if balance < 0:
            raise ValueError("Balance cannot be negative.")
        
        # Private attributes
        self.__wallet_id = wallet_id
        self.__balance = balance
    
    def get_balance(self): #Public method to check current balance.
        
        return self.__balance
    
    def process_payment(self, amount):
      # process payment from Digital wallet with sufficient balance
        print(f"\nProcessing Digital Wallet payment...")
        print(f"Wallet ID: {self.__wallet_id}")
        print(f"Current Balance: ${self.__balance:.2f}")
        print(f"Amount to Pay: ${amount:.2f}")
        
        # Check for sufficient balance
        if self.__balance < amount:
            print(f" Payment failed: Insufficient balance!")
            print(f"  You need ${amount - self.__balance:.2f} more.")
            return False
        
        # Deduct amount from balance
        self.__balance -= amount
        print(f"New Balance: ${self.__balance:.2f}")
        print(" Payment successful!")
        return True
    
    def get_payment_details(self):
        """Return wallet details."""
        return f"Digital Wallet ({self.__wallet_id}) - Balance: ${self.__balance:.2f}"


# CASH ON DELIVERY PAYMENT METHOD


class CashOnDelivery(PaymentMethod):
    """
    Cash on delivery payment with $5 handling charge.
    """
    
    def __init__(self, address): # intialize cash on delivery with address attribute
        
        # Validate address
        if not address or len(address.strip()) < 10:
            raise ValueError("Please provide a complete delivery address.")
        
        # Private attributes
        self.__address = address
        self.__handling_charge = 5.00  # Fixed $5 handling fee
    
    def process_payment(self, amount):
      # process payment including cash on delivery with proper amount
        total_amount = amount + self.__handling_charge
        
        print(f"\nProcessing Cash on Delivery order...")
        print(f"Delivery Address: {self.__address}")
        print(f"Subtotal: ${amount:.2f}")
        print(f"Handling Charge: ${self.__handling_charge:.2f}")
        print(f"Total to Pay on Delivery: ${total_amount:.2f}")
        print(" Order confirmed! Pay the delivery person.")
        return True
    
    def get_payment_details(self):
        """Return COD details."""
        return f"Cash on Delivery to {self.__address}"



# DEMONSTRATION / TESTING


def main():
    """Main function to demonstrate the e-commerce payment system."""
    
    print("=" * 60)
    print(" WELCOME TO THE E-COMMERCE PAYMENT SYSTEM")
    print("=" * 60)
    
    # Create shopping cart
    cart = Shoppingcart()
    
    # Add items to cart
    print("\n--- Adding Items to Cart ---")
    cart.add_item("Laptop", 999.99)
    cart.add_item("Mouse", 25.50)
    cart.add_item("Keyboard", 75.00)
    
    # Display cart
    cart.display_cart()
    
    # Calculate total
    total = cart.calculate_total()
    
    # Try different payment methods (Polymorphism in action!)
    print("\n" + "=" * 60)
    print("     TESTING DIFFERENT PAYMENT METHODS")
    print("=" * 60)
    
    # Test 1: Credit Card
    print("\n Test 1: Credit Card Payment ")
    try:
        credit_card = CreditCard("1234567890123456", "123", "12/26")
        print(f"Using: {credit_card.get_payment_details()}")
        credit_card.process_payment(total)
    except ValueError as e:
        print(f"Error: {e}")
    
    # Test 2: Debit Card
    print("\nTest 2: Debit Card Payment ")
    try:
        debit_card = DebitCard("9876543210987654", "4567")
        print(f"Using: {debit_card.get_payment_details()}")
        debit_card.process_payment(total)
    except ValueError as e:
        print(f"Error: {e}")
    
    # Test 3: Digital Wallet (Sufficient Balance)
    print("\n Test 3: Digital Wallet Payment (Sufficient Balance) ")
    try:
        wallet = DigitalWallet("user@email.com", 1500.00)
        print(f"Using: {wallet.get_payment_details()}")
        wallet.process_payment(total)
    except ValueError as e:
        print(f"Error: {e}")
    
    # Test 4: Digital Wallet (Insufficient Balance)
    print("\nTest 4: Digital Wallet Payment (Insufficient Balance) ")
    try:
        wallet_low = DigitalWallet("poor@email.com", 50.00)
        print(f"Using: {wallet_low.get_payment_details()}")
        wallet_low.process_payment(total)
    except ValueError as e:
        print(f"Error: {e}")
    
    # Test 5: Cash on Delivery
    print("\n Test 5: Cash on Delivery ")
    try:
        cod = CashOnDelivery("123 Main Street, Apt 4B, New York, NY 10001")
        print(f"Using: {cod.get_payment_details()}")
        cod.process_payment(total)
    except ValueError as e:
        print(f"Error: {e}")
    
    # Demonstrate polymorphism
    print("\n" + "=" * 60)
    print("     DEMONSTRATING POLYMORPHISM")
    print("=" * 60)
    print("\nProcessing payment with different methods using same interface:")
    
    # Create a list of different payment methods
    payment_methods = [
        CreditCard("1111222233334444", "999", "11/27"),
        DebitCard("5555666677778888", "1234"),
        DigitalWallet("poly@example.com", 2000.00),
        CashOnDelivery("456 Oak Avenue, Suite 12, Boston, MA 02101")
    ]
    
    # Process payment using each method (same interface, different behavior)
    for i, payment_method in enumerate(payment_methods, 1):
        print(f"\n--- Payment Method #{i} ---")
        payment_method.process_payment(100.00)
    
    print("\n" + "=" * 60)
    print("     THANK YOU FOR SHOPPING WITH US!")
    print("=" * 60)


# Run the demonstration
if __name__ == "__main__":
    main()