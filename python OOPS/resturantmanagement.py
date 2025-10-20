class Employee:
 # represent all employes
    
    # Class variables - shared across ALL employee instances
    restaurant_name = "Broadway Resturant"
    restaurant_location = "Saltlake, Sector-v,Bidhannagar"
    
    def __init__(self, name, emp_id, salary, hours_worked):
      # intialize a new employee with all the attributes
        self.name = name
        self.emp_id = emp_id
        self.salary = salary
        self.hours_worked = hours_worked
    
    def calculate_salary(self): # calculate the base salary 
    
        return self.salary
    
    def get_employee_details(self): # Generate Employee Details
        
        details = f"""
        
{'='*60}
RESTAURANT: {Employee.restaurant_name}
LOCATION: {Employee.restaurant_location}
{'='*60}
Employee Name    : {self.name}
Employee ID      : {self.emp_id}
Position         : {self.__class__.__name__}
Base Salary      : ${self.salary:,.2f}
Hours Worked     : {self.hours_worked} hrs
Total Salary     : ${self.calculate_salary():,.2f}
{'='*60}
"""
        return details
    
    @staticmethod
    def calculate_total_payroll(employees_list): # calculate total payroll based on the employee list
      
        if not employees_list: # if the Employee list is empty then total payroll is not calculated
            return 0.0
        
        total_payroll = sum(employee.calculate_salary() for employee in employees_list)
        return total_payroll
    
    def __str__(self):
        """String representation of employee."""
        return f"{self.__class__.__name__}: {self.name} (ID: {self.emp_id})"
    
    def __repr__(self):# developer friendly representation for debugging
        
        return f"{self.__class__.__name__}('{self.name}', '{self.emp_id}', {self.salary}, {self.hours_worked})"


class Chef(Employee): # Represent the Chef class
   
     # Class variable with constant value
    BONUS_PER_DISH = 5  # $5 per dish prepared
    
    def __init__(self, name, emp_id, salary, hours_worked, specialization, dishes_prepared):
       # Intialize the chef class with extra attribute specialization,dishes_prepared
        # Call parent class constructor
        super().__init__(name, emp_id, salary, hours_worked)
        
        self.specialization = specialization.lower()
        self.dishes_prepared = dishes_prepared
    
    def calculate_salary(self):
     # calculate salary of employee 
        dish_bonus = self.dishes_prepared * Chef.BONUS_PER_DISH
        total_salary = self.salary + dish_bonus
        return total_salary
    
    def get_employee_details(self):
       # Chef Specific details
        dish_bonus = self.dishes_prepared * Chef.BONUS_PER_DISH
        
        details = f"""
{'='*60}
RESTAURANT: {Employee.restaurant_name}
LOCATION: {Employee.restaurant_location}
{'='*60}
Employee Name    : {self.name}
Employee ID      : {self.emp_id}
Position         : Chef
Specialization   : {self.specialization.title()}
Base Salary      : ${self.salary:,.2f}
Hours Worked     : {self.hours_worked} hrs
Dishes Prepared  : {self.dishes_prepared}
Dish Bonus       : ${dish_bonus:,.2f} ({self.dishes_prepared} × ${Chef.BONUS_PER_DISH})
Total Salary     : ${self.calculate_salary():,.2f}
{'='*60}
"""
        return details


class Waiter(Employee):
  # Represents Waiter Class
    
    def __init__(self, name, emp_id, salary, hours_worked, tables_assigned, tips_collected):
        
       # Initialize a Waiter employee.
        
       
        # Call parent class constructor
        super().__init__(name, emp_id, salary, hours_worked)
        
        # Waiter-specific attributes
        self.tables_assigned = tables_assigned
        self.tips_collected = tips_collected
    
    def calculate_salary(self):
    
      #  Calculate waiter's total salary.
       # Formula: Base Salary + Tips Collected
        
       
        total_salary = self.salary + self.tips_collected
        return total_salary
    
    def get_employee_details(self):
     # Generate Employee Details
        details = f"""
{'='*60}
RESTAURANT: {Employee.restaurant_name}
LOCATION: {Employee.restaurant_location}
{'='*60}
Employee Name    : {self.name}
Employee ID      : {self.emp_id}
Position         : Waiter
Tables Assigned  : {self.tables_assigned}
Base Salary      : ${self.salary:,.2f}
Hours Worked     : {self.hours_worked} hrs
Tips Collected   : ${self.tips_collected:,.2f}
Total Salary     : ${self.calculate_salary():,.2f}
{'='*60}
"""
        return details


class Manager(Employee):
  # Represent Manager Class
    
    def __init__(self, name, emp_id, salary, hours_worked, department, team_size, bonus_percentage):
        
       # Initialize a Manager employee.
        
        
       
        # Call parent class constructor
        super().__init__(name, emp_id, salary, hours_worked)
        
        # Manager-specific attributes
        self.department = department
        self.team_size = team_size
        self.bonus_percentage = bonus_percentage
    
    def calculate_salary(self):
        
       # Calculate manager's total salary.
      #  Formula: Base Salary + (Base Salary × Bonus Percentage / 100)
        
       
        bonus_amount = self.salary * (self.bonus_percentage / 100)
        total_salary = self.salary + bonus_amount
        return total_salary
    
    def get_employee_details(self):
      # Generate manager details
        bonus_amount = self.salary * (self.bonus_percentage / 100)
        
        details = f"""
{'='*60}
RESTAURANT: {Employee.restaurant_name}
LOCATION: {Employee.restaurant_location}
{'='*60}
Employee Name    : {self.name}
Employee ID      : {self.emp_id}
Position         : Manager
Department       : {self.department}
Team Size        : {self.team_size} employees
Base Salary      : ${self.salary:,.2f}
Hours Worked     : {self.hours_worked} hrs
Bonus Percentage : {self.bonus_percentage}%
Bonus Amount     : ${bonus_amount:,.2f}
Total Salary     : ${self.calculate_salary():,.2f}
{'='*60}
"""
        return details



#                           DEMONSTRATION & TESTING


def print_header(text):
    """Helper function to print formatted headers."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def main():
    """Main function to demonstrate the restaurant management system."""
    
    print("\n" + "*"*60)
    print("   RESTAURANT STAFF MANAGEMENT SYSTEM  ")
    print("*"*60)
    
    # ========== CREATE EMPLOYEES ==========
    print_header("CREATING EMPLOYEE RECORDS")
    
    # Create Chef employees
    chef1 = Chef(
        name="Sayantan",
        emp_id="CH001",
        salary=35000.00,
        hours_worked=160,
        specialization ="Indian",
        dishes_prepared=240
    )
    
    chef2 = Chef(
        name="Debasish",
        emp_id="CH002",
        salary=3900.00,
        hours_worked=160,
        specialization="chinese",
        dishes_prepared=280
    )
    
    chef3 = Chef(
        name="Priya Barman",
        emp_id="CH003",
        salary=3600.00,
        hours_worked=160,
        specialization="chinies",
        dishes_prepared=220
    )
    
    # Create Waiter employees
    waiter1 = Waiter(
        name="Ramesh",
        emp_id="WT001",
        salary=2200.00,
        hours_worked=160,
        tables_assigned=8,
        tips_collected=950.00
    )
    
    waiter2 = Waiter(
        name="Sourav",
        emp_id="WT002",
        salary=2200.00,
        hours_worked=160,
        tables_assigned=6,
        tips_collected=720.00
    )
    
    waiter3 = Waiter(
        name="Arko",
        emp_id="WT003",
        salary=2200.00,
        hours_worked=160,
        tables_assigned=7,
        tips_collected=880.00
    )
    
    # Create Manager employees
    manager1 = Manager(
        name="Pravash Ghosh",
        emp_id="MG001",
        salary=5900.00,
        hours_worked=170,
        department="Kitchen",
        team_size=12,
        bonus_percentage=20
    )
    
    manager2 = Manager(
        name="Santu Roy",
        emp_id="MG002",
        salary=5500.00,
        hours_worked=160,
        department="Service",
        team_size=10,
        bonus_percentage=18
    )
    
    # Store all employees in a list
    all_employees = [chef1, chef2, chef3, waiter1, waiter2, waiter3, manager1, manager2]
    
    print(f"\n Created {len(all_employees)} employee records successfully!")
    
    # ========== DISPLAY INDIVIDUAL EMPLOYEE DETAILS ==========
    print_header("INDIVIDUAL EMPLOYEE DETAILS")
    
    for i, employee in enumerate(all_employees, 1):
        print(f"\n--- Employee {i} ---")
        print(employee.get_employee_details())
    
    # ========== CALCULATE TOTAL PAYROLL ==========
    print_header("PAYROLL SUMMARY")
    
    total_payroll = Employee.calculate_total_payroll(all_employees)
    
    print(f"\n Total Employees: {len(all_employees)}")
    print(f" Total Monthly Payroll: ${total_payroll:,.2f}\n")
    
    # ========== BREAKDOWN BY ROLE ==========
    print_header("PAYROLL BREAKDOWN BY ROLE")
    
    # Filter employees by type
    chefs = [emp for emp in all_employees if isinstance(emp, Chef)]
    waiters = [emp for emp in all_employees if isinstance(emp, Waiter)]
    managers = [emp for emp in all_employees if isinstance(emp, Manager)]
    
    # Calculate payroll for each role
    chef_payroll = Employee.calculate_total_payroll(chefs)
    waiter_payroll = Employee.calculate_total_payroll(waiters)
    manager_payroll = Employee.calculate_total_payroll(managers)
    
    print(f"\n CHEFS ({len(chefs)} employees)")
    print(f"   Total Payroll: ${chef_payroll:,.2f}")
    for chef in chefs:
        print(f"   - {chef.name}: ${chef.calculate_salary():,.2f}")
    
    print(f"\n  WAITERS ({len(waiters)} employees)")
    print(f"   Total Payroll: ${waiter_payroll:,.2f}")
    for waiter in waiters:
        print(f"   - {waiter.name}: ${waiter.calculate_salary():,.2f}")
    
    print(f"\n MANAGERS ({len(managers)} employees)")
    print(f"   Total Payroll: ${manager_payroll:,.2f}")
    for manager in managers:
        print(f"   - {manager.name}: ${manager.calculate_salary():,.2f}")
    
    # ========== STATISTICS ==========
    print_header("STATISTICS")
    
    avg_salary = total_payroll / len(all_employees)
    highest_paid = max(all_employees, key=lambda emp: emp.calculate_salary())
    lowest_paid = min(all_employees, key=lambda emp: emp.calculate_salary())
    
    print(f"\n Average Salary: ${avg_salary:,.2f}")
    print(f"⬆ Highest Paid: {highest_paid.name} - ${highest_paid.calculate_salary():,.2f}")
    print(f"⬇  Lowest Paid: {lowest_paid.name} - ${lowest_paid.calculate_salary():,.2f}")
    
    print("\n" + "="*60)
    print("   Restaurant Management System - Report Complete")
    print("="*60 + "\n")


# Run the demonstration
if __name__ == "__main__":
    main()