from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict


class Product:
    """Represents a product in the store"""
    
    def __init__(self, product_id: str, name: str, category: str, 
                 price: float, supplier: 'Supplier', reorder_level: int):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.supplier = supplier
        self.reorder_level = reorder_level
    
    def __repr__(self):
        return f"Product({self.product_id}, {self.name}, ${self.price})"


class Supplier:
    """Represents a supplier who provides products"""
    
    def __init__(self, supplier_id: str, name: str, reliability_rating: float):
        self.supplier_id = supplier_id
        self.name = name
        self.reliability_rating = reliability_rating  # 0-5 rating
        self.products_supplied: List[Product] = []
    
    def add_product(self, product: Product):
        """Add a product to supplier's product list"""
        if product not in self.products_supplied:
            self.products_supplied.append(product)
    
    def __repr__(self):
        return f"Supplier({self.name}, Rating: {self.reliability_rating})"


class StockAlert:
    """Represents a stock alert when product quantity is low"""
    
    def __init__(self, product: Product, current_quantity: int, threshold: int):
        self.product = product
        self.current_quantity = current_quantity
        self.threshold = threshold
        self.alert_date = datetime.now()
    
    def __repr__(self):
        return (f"ALERT: {self.product.name} - Current: {self.current_quantity}, "
                f"Threshold: {self.threshold}, Date: {self.alert_date.strftime('%Y-%m-%d %H:%M')}")


class Transaction:
    """Records stock movements (in/out)"""
    
    def __init__(self, product: Product, quantity: int, 
                 transaction_type: str, timestamp: datetime = None):
        self.product = product
        self.quantity = quantity
        self.transaction_type = transaction_type  # 'IN' or 'OUT'
        self.timestamp = timestamp or datetime.now()
    
    def __repr__(self):
        return (f"Transaction({self.transaction_type}, {self.product.name}, "
                f"Qty: {self.quantity}, {self.timestamp.strftime('%Y-%m-%d %H:%M')})")


class Inventory:
    """Manages product stock levels and warehouse locations"""
    
    def __init__(self):
        # Dictionary to store products and their stock info
        self._stock: Dict[str, Dict] = {}
        self.stock_alerts: List[StockAlert] = []
        self.transactions: List[Transaction] = []
    
    def add_product(self, product: Product, quantity: int, location: str):
        """Add a new product to inventory"""
        if quantity < 0:
            raise ValueError("Initial quantity cannot be negative")
        
        self._stock[product.product_id] = {
            'product': product,
            'quantity': quantity,
            'location': location
        }
        
        # Record transaction
        transaction = Transaction(product, quantity, 'IN')
        self.transactions.append(transaction)
        
        # Check if alert needed
        self._check_stock_alert(product)
    
    def get_quantity(self, product_id: str) -> int:
        """Get current quantity of a product"""
        if product_id not in self._stock:
            return 0
        return self._stock[product_id]['quantity']
    
    def set_quantity(self, product_id: str, new_quantity: int):
        """Set quantity with validation (prevents negative stock)"""
        if new_quantity < 0:
            raise ValueError(f"Cannot set negative stock for product {product_id}")
        
        if product_id not in self._stock:
            raise ValueError(f"Product {product_id} not in inventory")
        
        old_quantity = self._stock[product_id]['quantity']
        self._stock[product_id]['quantity'] = new_quantity
        
        # Record transaction
        diff = new_quantity - old_quantity
        if diff != 0:
            trans_type = 'IN' if diff > 0 else 'OUT'
            transaction = Transaction(
                self._stock[product_id]['product'], 
                abs(diff), 
                trans_type
            )
            self.transactions.append(transaction)
        
        # Check for alert
        self._check_stock_alert(self._stock[product_id]['product'])
    
    def _check_stock_alert(self, product: Product):
        """Internal method to check if stock alert should be triggered"""
        current_qty = self.get_quantity(product.product_id)
        
        if current_qty < product.reorder_level:
            # Check if alert already exists for this product
            existing_alert = any(
                alert.product.product_id == product.product_id 
                for alert in self.stock_alerts
            )
            
            if not existing_alert:
                alert = StockAlert(product, current_qty, product.reorder_level)
                self.stock_alerts.append(alert)
                print(f"  {alert}")
    
    def reduce_stock(self, product_id: str, quantity: int):
        """Reduce stock by given quantity (used during sales)"""
        current = self.get_quantity(product_id)
        new_quantity = current - quantity
        
        if new_quantity < 0:
            raise ValueError(
                f"Insufficient stock for {product_id}. "
                f"Available: {current}, Requested: {quantity}"
            )
        
        self.set_quantity(product_id, new_quantity)
    
    def calculate_total_value(self) -> float:
        """Calculate total value of all inventory"""
        total = 0
        for item in self._stock.values():
            product = item['product']
            quantity = item['quantity']
            total += product.price * quantity
        return total
    
    def get_location(self, product_id: str) -> Optional[str]:
        """Get warehouse location of a product"""
        if product_id in self._stock:
            return self._stock[product_id]['location']
        return None
    
    def __iter__(self):
        """Iterator to loop through low-stock items"""
        for item in self._stock.values():
            product = item['product']
            quantity = item['quantity']
            if quantity < product.reorder_level:
                yield {
                    'product': product,
                    'quantity': quantity,
                    'location': item['location']
                }
    
    def __repr__(self):
        return f"Inventory(Products: {len(self._stock)}, Alerts: {len(self.stock_alerts)})"


class Sale:
    """Records a sale transaction"""
    
    def __init__(self, sale_id: str, customer: str, 
                 inventory: Inventory, discount_applied: float = 0):
        self.sale_id = sale_id
        self.customer = customer
        self.products_sold: List[Dict] = []  # {'product': Product, 'quantity': int}
        self.timestamp = datetime.now()
        self.discount_applied = discount_applied  # percentage (0-100)
        self.inventory = inventory
    
    def add_product(self, product: Product, quantity: int):
        """Add a product to this sale"""
        # Check if enough stock available
        available = self.inventory.get_quantity(product.product_id)
        if available < quantity:
            raise ValueError(
                f"Cannot sell {quantity} units of {product.name}. "
                f"Only {available} available."
            )
        
        # Reduce stock in inventory
        self.inventory.reduce_stock(product.product_id, quantity)
        
        # Add to sale record
        self.products_sold.append({
            'product': product,
            'quantity': quantity
        })
    
    def calculate_total(self) -> float:
        """Calculate total sale amount after discount"""
        subtotal = sum(
            item['product'].price * item['quantity'] 
            for item in self.products_sold
        )
        discount_amount = subtotal * (self.discount_applied / 100)
        return subtotal - discount_amount
    
    def __repr__(self):
        return (f"Sale({self.sale_id}, Customer: {self.customer}, "
                f"Items: {len(self.products_sold)}, Total: ${self.calculate_total():.2f})")


class StoreAnalytics:
    """Provides sales analytics and business insights"""
    
    def __init__(self, sales: List[Sale], inventory: Inventory):
        self.sales = sales
        self.inventory = inventory
    
    def best_selling_products(self, top_n: int = 5) -> List[Dict]:
        """Find top N best-selling products by quantity"""
        product_sales = defaultdict(int)
        
        for sale in self.sales:
            for item in sale.products_sold:
                product = item['product']
                quantity = item['quantity']
                product_sales[product.product_id] += quantity
        
        # Sort by quantity sold (descending)
        sorted_products = sorted(
            product_sales.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        result = []
        for product_id, total_qty in sorted_products[:top_n]:
            # Find product object
            for item in self.inventory._stock.values():
                if item['product'].product_id == product_id:
                    result.append({
                        'product': item['product'],
                        'total_sold': total_qty
                    })
                    break
        
        return result
    
    def revenue_by_category(self) -> Dict[str, float]:
        """Calculate total revenue grouped by product category"""
        category_revenue = defaultdict(float)
        
        for sale in self.sales:
            for item in sale.products_sold:
                product = item['product']
                quantity = item['quantity']
                category = product.category
                
                # Calculate revenue (considering sale's discount)
                item_revenue = product.price * quantity
                discount_factor = 1 - (sale.discount_applied / 100)
                category_revenue[category] += item_revenue * discount_factor
        
        return dict(category_revenue)
    
    def total_revenue(self) -> float:
        """Calculate total revenue from all sales"""
        return sum(sale.calculate_total() for sale in self.sales)


class StoreManager:
    """Main class to manage the entire store operations"""
    
    def __init__(self):
        self.inventory = Inventory()
        self.sales: List[Sale] = []
        self.suppliers: List[Supplier] = []
    
    def add_supplier(self, supplier: Supplier):
        """Add a supplier to the store"""
        self.suppliers.append(supplier)
    
    def batch_update_prices(self, category: str, percentage_change: float):
        """Update prices for all products in a category"""
        updated_count = 0
        
        for item in self.inventory._stock.values():
            product = item['product']
            if product.category == category:
                # Calculate new price
                multiplier = 1 + (percentage_change / 100)
                product.price = round(product.price * multiplier, 2)
                updated_count += 1
        
        print(f" Updated {updated_count} products in '{category}' category "
              f"by {percentage_change:+.1f}%")
    
    def create_sale(self, sale_id: str, customer: str, discount: float = 0) -> Sale:
        """Create a new sale"""
        sale = Sale(sale_id, customer, self.inventory, discount)
        self.sales.append(sale)
        return sale
    
    def get_analytics(self) -> StoreAnalytics:
        """Get analytics object for business insights"""
        return StoreAnalytics(self.sales, self.inventory)
    
    def display_low_stock_items(self):
        """Display all items with low stock using iterator"""
        print("\n LOW STOCK ITEMS:")
        print("-" * 60)
        
        low_stock_items = list(self.inventory)
        
        if not low_stock_items:
            print(" No low stock items!")
        else:
            for item in low_stock_items:
                product = item['product']
                print(f"• {product.name} ({product.product_id})")
                print(f"  Current: {item['quantity']} | "
                      f"Reorder Level: {product.reorder_level} | "
                      f"Location: {item['location']}")
    
    def display_inventory_summary(self):
        """Display comprehensive inventory summary"""
        print("\n" + "="*60)
        print("INVENTORY SUMMARY")
        print("="*60)
        
        print(f"\nTotal Products: {len(self.inventory._stock)}")
        print(f"Total Inventory Value: ${self.inventory.calculate_total_value():,.2f}")
        print(f"Active Alerts: {len(self.inventory.stock_alerts)}")
        print(f"Total Transactions: {len(self.inventory.transactions)}")


# == DEMONSTRATION ==

def main():
    """Demonstrate the retail store management system"""
    
    print(" RETAIL STORE MANAGEMENT SYSTEM")
    print("="*60)
    
    # Create store manager
    store = StoreManager()
    
    # Create suppliers
    supplier1 = Supplier("SUP001", "TechWorld Inc", 4.5)
    supplier2 = Supplier("SUP002", "Fashion Hub Ltd", 4.0)
    supplier3 = Supplier("SUP003", "Home Essentials Co", 4.8)
    
    store.add_supplier(supplier1)
    store.add_supplier(supplier2)
    store.add_supplier(supplier3)
    
    # Create products
    laptop = Product("P001", "Gaming Laptop", "Electronics", 1200.00, supplier1, 5)
    mouse = Product("P002", "Wireless Mouse", "Electronics", 25.00, supplier1, 20)
    keyboard = Product("P003", "Mechanical Keyboard", "Electronics", 80.00, supplier1, 15)
    tshirt = Product("P004", "Cotton T-Shirt", "Clothing", 20.00, supplier2, 50)
    jeans = Product("P005", "Denim Jeans", "Clothing", 50.00, supplier2, 30)
    lamp = Product("P006", "LED Lamp", "Home", 35.00, supplier3, 10)
    
    # Add products to suppliers
    supplier1.add_product(laptop)
    supplier1.add_product(mouse)
    supplier1.add_product(keyboard)
    supplier2.add_product(tshirt)
    supplier2.add_product(jeans)
    supplier3.add_product(lamp)
    
    # Add products to inventory
    print("\n Adding Products to Inventory...")
    store.inventory.add_product(laptop, 10, "Warehouse-A-Shelf-1")
    store.inventory.add_product(mouse, 50, "Warehouse-A-Shelf-2")
    store.inventory.add_product(keyboard, 25, "Warehouse-A-Shelf-3")
    store.inventory.add_product(tshirt, 100, "Warehouse-B-Rack-1")
    store.inventory.add_product(jeans, 60, "Warehouse-B-Rack-2")
    store.inventory.add_product(lamp, 15, "Warehouse-C-Shelf-1")
    
    # Display initial inventory
    store.display_inventory_summary()
    
    # Create some sales
    print("\n\n PROCESSING SALES...")
    print("-" * 60)
    
    # Sale 1
    sale1 = store.create_sale("SALE001", "John Doe", discount=10)
    sale1.add_product(laptop, 2)
    sale1.add_product(mouse, 1)
    print(f" {sale1}")
    
    # Sale 2
    sale2 = store.create_sale("SALE002", "Jane Smith", discount=5)
    sale2.add_product(tshirt, 5)
    sale2.add_product(jeans, 2)
    print(f" {sale2}")
    
    # Sale 3
    sale3 = store.create_sale("SALE003", "Bob Johnson")
    sale3.add_product(keyboard, 3)
    sale3.add_product(lamp, 2)
    print(f"✅ {sale3}")
    
    # Sale 4 - This will trigger low stock alert
    print("\n  Processing sale that triggers alerts...")
    sale4 = store.create_sale("SALE004", "Alice Brown", discount=15)
    sale4.add_product(laptop, 6)  # Only 2 left now (< reorder level of 5)
    print(f" {sale4}")
    
    # Display low stock items using iterator
    store.display_low_stock_items()
    
    # Batch price update
    print("\n\n BATCH PRICE UPDATE:")
    print("-" * 60)
    store.batch_update_prices("Electronics", 10)  # Increase electronics by 10%
    
    # Analytics
    print("\n\n SALES ANALYTICS:")
    print("-" * 60)
    
    analytics = store.get_analytics()
    
    print("\n Best Selling Products:")
    for i, item in enumerate(analytics.best_selling_products(3), 1):
        print(f"{i}. {item['product'].name} - {item['total_sold']} units sold")
    
    print("\n Revenue by Category:")
    for category, revenue in analytics.revenue_by_category().items():
        print(f"• {category}: ${revenue:,.2f}")
    
    print(f"\n Total Revenue: ${analytics.total_revenue():,.2f}")
    
    # Final inventory summary
    store.display_inventory_summary()
    
    # Display recent transactions
    print("\n\n RECENT TRANSACTIONS (Last 5):")
    print("-" * 60)
    for trans in store.inventory.transactions[-5:]:
        print(f"• {trans}")


if __name__ == "__main__":
    main()