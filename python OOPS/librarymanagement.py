from datetime import datetime, timedelta


# MIXIN CLASSES :- That can be combine with other super classes


class Borrowable:
    """Mixin class for items that can be borrowed"""
    
    def __init__(self, **kwargs):
        # Initialize borrowing-related attributes
        self.is_checked_out = False  # Track if item is currently borrowed
        self.borrower = None  # Who borrowed it
        self.checkout_date = None  # When it was borrowed
        self.due_date_value = None  # When it's due back
        self.fine_per_day = 0.50  # Fine for overdue items ($0.50/day)
        # Call by use  MRO (Method Resolution Order)
        super().__init__(**kwargs)
    
    def check_out(self, borrower_name, days=14):
        """Check out the item to a borrower"""
        if self.is_checked_out:
            return f"Error: Item is already checked out to {self.borrower}"
        
        # Mark as checked out and record details
        self.is_checked_out = True
        self.borrower = borrower_name
        self.checkout_date = datetime.now()
        self.due_date_value = self.checkout_date + timedelta(days=days)
        
        return f"Checked out to {borrower_name}. Due date: {self.due_date_value.strftime('%Y-%m-%d')}"
    
    def return_item(self): #Return the borrowed item and calculate any fines
        
        if not self.is_checked_out: # negatation logic is used
            return "Error: Item is not checked out"
        
        # Calculate if there's a fine for late return
        return_date = datetime.now()
        fine = 0
        
        if return_date > self.due_date_value:# condition is True if return_dateis grater than due_date_value
            # Calculate days overdue: (return date - due_date_value )
            days_overdue = (return_date - self.due_date_value).days
            fine = days_overdue * self.fine_per_day
        
        # Reset borrowing status
        borrower = self.borrower
        self.is_checked_out = False
        self.borrower = None
        self.checkout_date = None
        self.due_date_value = None
        
        if fine > 0:# if fine is positive then book is returned
            return f"Returned by {borrower}. Fine: ${fine:.2f} ({days_overdue} days overdue)"
        return f"Returned by {borrower}. No fine."
    
    def due_date(self):
        """Get the due date as a formatted string"""
        if not self.is_checked_out:
            return "Item is not checked out"
        return self.due_date_value.strftime('%Y-%m-%d %H:%M')


class Downloadable:
    """Mixin class for items that can be downloaded"""
    
    def __init__(self, file_size_mb=0, download_limit=5, **kwargs):
        # Initialize download-related attributes
        self.file_size_mb = file_size_mb  # Size in megabytes
        self.download_limit = download_limit  # download limit tells about maximum download 
        self.download_count_value = 0  # Current download count
        # Call next class in MRO
        super().__init__(**kwargs)
    
    def download(self, user):
        """Download the digital content"""
        # Check if download limit is reached
        if self.download_count_value >= self.download_limit:
            print( f"Error: Download limit ({self.download_limit}) reached for this item")
        
        self.download_count_value += 1
        remaining = self.download_limit - self.download_count_value
        
        print( f"Downloaded by {user}. Size: {self.file_size_mb}MB. {remaining} downloads remaining.")
    
    def file_size(self):
        """Get the file size"""
        return f"{self.file_size_mb} MB"
    
    def download_count(self):
        """Get current download count"""
        return f"{self.download_count_value}/{self.download_limit} downloads used"


class Physical:
    """Mixin class for physical items with a location"""
    
    def __init__(self, shelf_location="Unknown", condition="new", **kwargs):
        # Initialize physical item attributes
        self.shelf_location = shelf_location  # Where the item is stored
        self.condition = condition  # Condition: new, good, or worn
        # Call next class in MRO
        super().__init__(**kwargs)
    
    def get_location(self):
        """Get the shelf location"""
        return f"Shelf: {self.shelf_location}"
    
    def update_condition(self, new_condition):
        """Update the condition of the item"""
        valid_conditions = ["new", "good", "worn"]
        if new_condition.lower() in valid_conditions:
            self.condition = new_condition.lower()
            return f"Condition updated to: {self.condition}"
        return f"Error: Invalid condition. Must be one of {valid_conditions}"
    
    def get_condition(self):
        """Get the current condition"""
        return f"Condition: {self.condition}"



# BASE ITEM CLASS


class LibraryItem:
    """Base class for all library items"""
    
    def __init__(self, title, author_creator, year, **kwargs):
        # Basic attributes for all items
        self.title = title
        self.author_creator = author_creator
        self.year = year
        # Call super to handle any remaining kwargs for mixins
        super().__init__(**kwargs)
    
    def get_info(self):
        """Get basic information about the item"""
        return f"{self.title} by {self.author_creator} ({self.year})"



# CONCRETE ITEM CLASSES (Combining Mixins)


class EBook(Borrowable, Downloadable, LibraryItem):
    """EBook: Can be borrowed AND downloaded"""
    
    def __init__(self, title, author_creator, year, file_size_mb, download_limit=5, format="PDF"):
        # Store eBook-specific attributes
        self.format = format  # File format (PDF, EPUB, etc.)
        
        # Call parent constructors using super()
        # order of the Method call: 1)EBook -> 2)Borrowable -> 3)Downloadable -> 4)LibraryItem -> 5)object
        super().__init__(
            title=title,
            author_creator=author_creator,
            year=year,
            file_size_mb=file_size_mb,
            download_limit=download_limit
        )
    
    def __str__(self):
        return f"EBook: {self.get_info()} [{self.format}]"


class AudioBook(Borrowable, Downloadable, LibraryItem):
    """AudioBook: Can be borrowed AND downloaded"""
    
    def __init__(self, title, author_creator, year, file_size_mb, duration_minutes, download_limit=3):
        # Store audiobook-specific attributes
        self.duration_minutes = duration_minutes  # Length of audiobook
        
        # Call parent constructors
        # order of the Method Call: 1)AudioBook -> 2)Borrowable -> 3)Downloadable -> 4)LibraryItem -> 5)object
        super().__init__(
            title=title,
            author_creator=author_creator,
            year=year,
            file_size_mb=file_size_mb,
            download_limit=download_limit
        )
    
    def get_duration(self):
        """Get formatted duration"""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        return f"{hours}h {minutes}m"
    
    def __str__(self):
        return f"AudioBook: {self.get_info()} [Duration: {self.get_duration()}]"


class PrintedBook(Borrowable, Physical, LibraryItem):
    """Printed Book: Can be borrowed AND is physical"""
    
    def __init__(self, title, author_creator, year, shelf_location, condition="new", isbn=None):
        # Store printed book-specific attributes
        self.isbn = isbn  # International Standard Book Number
        
        # Call parent constructors
        # MRO:1) PrintedBook ->2) Borrowable ->3) Physical -> 4)LibraryItem -> 5)object
        super().__init__(
            title=title,
            author_creator=author_creator,
            year=year,
            shelf_location=shelf_location,
            condition=condition
        )
    
    def __str__(self):
        isbn_info = f" [ISBN: {self.isbn}]" if self.isbn else ""
        return f"Printed Book: {self.get_info()}{isbn_info}"


class Magazine(Physical, LibraryItem):
    """Magazine: Only physical, cannot be borrowed"""
    
    def __init__(self, title, publisher, year, issue_number, shelf_location, condition="new"):
        # Store magazine-specific attributes
        self.publisher = publisher  # Magazine publisher
        self.issue_number = issue_number  # Issue number
        
        # Call parent constructors
        # MRO:1) Magazine -> 2)Physical ->3) LibraryItem ->4) object
        super().__init__(
            title=title,
            author_creator=publisher,  # Use publisher as creator
            year=year,
            shelf_location=shelf_location,
            condition=condition
        )
    
    def __str__(self):
        return f"Magazine: {self.title} Issue #{self.issue_number} by {self.publisher} ({self.year})"



# DEMONSTRATION


def main():
    print("=" * 60)
    print("DIGITAL LIBRARY SYSTEM DEMO")
    print("=" * 60)
    
    # Create different library items
    print("\n1. Creating Items...")
    print("-" * 60)
    
    ebook = EBook(
        title="Python Programming",
        author_creator="John Doe",
        year=2024,
        file_size_mb=5.2,
        download_limit=10,
        format="EPUB"
    )
    print(f" {ebook}")
    
    audiobook = AudioBook(
        title="The Great Novel",
        author_creator="Ian Smith",
        year=2023,
        file_size_mb=250.5,
        duration_minutes=540,
        download_limit=5
    )
    print(f" {audiobook}")
    
    printed_book = PrintedBook(
        title="Classic Book",
        author_creator="William Shakespeare",
        year=1995,
        shelf_location="A-15",
        condition="good",
        isbn="978-0-123456-78-9"
    )
    print(f"{printed_book}")
    
    magazine = Magazine(
        title="ABP Ananda",
        
        publisher="Indian magazine.",
        year=2024,
        issue_number=42,
        shelf_location="MAG-05",
        condition="new"
    )
    print(f" {magazine}")
    
    # Demonstrate EBook functionality
    print("\n2. EBook Operations (Borrowable + Downloadable)")
    print("-" * 60)
    print(f"File Size: {ebook.file_size()}")
    print(ebook.download("Sayantan"))
    print(ebook.download("Debasish"))
    print(f"Downloads: {ebook.download_count()}")
    print(ebook.check_out("Shayamal", days=7))
    print(f"Due Date: {ebook.due_date()}")
    
    # Demonstrate AudioBook functionality
    print("\n3. AudioBook Operations (Borrowable + Downloadable)")
    print("-" * 60)
    print(f"Duration: {audiobook.get_duration()}")
    print(audiobook.check_out("Dabu", days=14))
    print(audiobook.download("Dabu"))
    
    # Demonstrate PrintedBook functionality
    print("\n4. Printed Book Operations (Borrowable + Physical)")
    print("-" * 60)
    print(printed_book.get_location())
    print(printed_book.get_condition())
    print(printed_book.check_out("Priyanka", days=21))
    
    # Demonstrate Magazine functionality
    print("\n5. Magazine Operations (Physical Only)")
    print("-" * 60)
    print(magazine.get_location())
    print(magazine.get_condition())
    print(magazine.update_condition("good"))
    # Note: Magazines don't have check_out method!
    
    # Demonstrate return with fine
    print("\n6. Returning Items with Fines")
    print("-" * 60)
    # Simulate overdue return by manipulating due date
    import datetime as dt
    ebook.due_date_value = dt.datetime.now() - dt.timedelta(days=3)  # 3 days overdue
    print(ebook.return_item())
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()