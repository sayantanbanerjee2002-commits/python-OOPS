from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional


# ============== CUSTOM EXCEPTIONS ==============
class InsufficientFundsError(Exception):
    """Raised when account doesn't have enough balance for transaction"""
    pass


class InvalidAmountError(Exception):
    """Raised when transaction amount is invalid (negative or zero)"""
    pass


class WithdrawalLimitExceededError(Exception):
    """Raised when withdrawal exceeds the allowed limit"""
    pass


class MinimumBalanceError(Exception):
    """Raised when balance falls below minimum required"""
    pass


# ============== TRANSACTION CLASS ==============
class Transaction: # Records individual transaction details
   
    
    def __init__(self, transaction_type: str, amount: float, balance_after: float, description: str = ""):
        self.transaction_type = transaction_type  # 'deposit', 'withdraw', 'transfer'
        self.amount = amount
        self.balance_after = balance_after
        self.description = description
        self.timestamp = datetime.now()
    
    def __str__(self): # readable format for the users 
        return (f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
                f"{self.transaction_type.upper()}: ${self.amount:.2f} | "
                f"Balance: ${self.balance_after:.2f} | {self.description}")


# ============== ABSTRACT BASE CLASS ==============
class BankAccount(ABC): # Represent Abstract bass class for all types of Bank account
    
    def __init__(self, account_number: str, account_holder: str, initial_balance: float = 0.0):
        self.account_number = account_number
        self.account_holder = account_holder
        self._balance = initial_balance  # Private attribute 
        self._transaction_history: List[Transaction] = []  #taken only  list of Transaction objects
        
        # Record initial deposit if any
        if initial_balance > 0:
            self._add_transaction("deposit", initial_balance, "Initial deposit")
    
    # Property decorator - makes balance read-only from outside
    @property
    def balance(self): # used the method as read only attribute
        return self._balance
    
    # Abstract methods - must be implemented by child classes
    @abstractmethod
    def deposit(self, amount: float) -> None:
        """Deposit money into account"""
        pass
    
    @abstractmethod
    def withdraw(self, amount: float) -> None:
        """Withdraw money from account"""
        pass
    
    @abstractmethod
    def transfer(self, recipient_account, amount: float) -> None:
        """Transfer money to another account"""
        pass
    
    # Protected method for internal use
    def _add_transaction(self, trans_type: str, amount: float, description: str = "") -> None:
        """Internal method to record transactions"""
        transaction = Transaction(trans_type, amount, self._balance, description)
        self._transaction_history.append(transaction)
    
    # Common validation method
    def _validate_amount(self, amount: float) -> None:
        """Validate transaction amount"""
        if amount <= 0:
            raise InvalidAmountError("Amount must be positive and greater than zero")
    
    def get_transaction_history(self, last_n: Optional[int] = None) -> List[Transaction]:
        """Get transaction history (optionally last N transactions)"""
        if last_n:
            return self._transaction_history[-last_n:]
        return self._transaction_history
    
    def print_statement(self, last_n: Optional[int] = None) -> None:
        """Print account statement"""
        print(f"\n{'='*70}")
        print(f"Account Statement - {self.account_holder}")
        print(f"Account Number: {self.account_number}")
        print(f"Current Balance: ${self._balance:.2f}")
        print(f"{'='*70}")
        
        transactions = self.get_transaction_history(last_n)
        if transactions:
            for trans in transactions:
                print(trans)
        else:
            print("No transactions yet.")
        print(f"{'='*70}\n")
    
    def __repr__(self):
        """Developer-friendly representation"""
        return (f"{self.__class__.__name__}(account_number='{self.account_number}', "
                f"account_holder='{self.account_holder}', balance={self._balance:.2f})")
    
    def __str__(self):
        """User-friendly representation"""
        return (f"{self.__class__.__name__} | Holder: {self.account_holder} | "
                f"Account #: {self.account_number} | Balance: ${self._balance:.2f}")


# ============== SAVINGS ACCOUNT ==============
class SavingsAccount(BankAccount):
    """Savings account with interest, minimum balance, and withdrawal limits"""
    
    def __init__(self, account_number: str, account_holder: str, initial_balance: float,
                 interest_rate: float = 3.5, minimum_balance: float = 500.0, 
                 withdrawal_limit: float = 5000.0):
        super().__init__(account_number, account_holder, initial_balance)
        self.interest_rate = interest_rate  # Annual interest rate in percentage
        self.minimum_balance = minimum_balance
        self.withdrawal_limit = withdrawal_limit
    
    def deposit(self, amount: float) -> None:
        """Deposit money into savings account"""
        self._validate_amount(amount)
        self._balance += amount
        self._add_transaction("deposit", amount, "Deposit to Savings Account")
        print(f"✓ Deposited ${amount:.2f}. New balance: ${self._balance:.2f}")
    
    def withdraw(self, amount: float) -> None:
        """Withdraw money from savings account with restrictions"""
        self._validate_amount(amount)
        
        # Check withdrawal limit
        if amount > self.withdrawal_limit:
            raise WithdrawalLimitExceededError(
                f"Withdrawal amount ${amount:.2f} exceeds limit of ${self.withdrawal_limit:.2f}"
            )
        
        # Check sufficient funds
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Insufficient funds. Available: ${self._balance:.2f}, Requested: ${amount:.2f}"
            )
        
        # Check minimum balance requirement
        if (self._balance - amount) < self.minimum_balance:
            raise MinimumBalanceError(
                f"Transaction would violate minimum balance of ${self.minimum_balance:.2f}"
            )
        
        self._balance -= amount
        self._add_transaction("withdraw", amount, "Withdrawal from Savings Account")
        print(f"✓ Withdrawn ${amount:.2f}. New balance: ${self._balance:.2f}")
    
    def transfer(self, recipient_account: BankAccount, amount: float) -> None:
        """Transfer money to another account"""
        self._validate_amount(amount)
        
        # Use withdraw to enforce all checks
        try:
            self.withdraw(amount)
            recipient_account.deposit(amount)
            self._add_transaction("transfer_out", amount, 
                                f"Transfer to {recipient_account.account_number}")
            print(f" Transferred ${amount:.2f} to {recipient_account.account_holder}")
        except Exception as e:
            # If recipient deposit fails, rollback withdrawal
            self._balance += amount
            raise e
    
    def __calculate_interest(self) -> float:
        """Private method to calculate interest (compound monthly)"""
        monthly_rate = self.interest_rate / 100 / 12
        interest = self._balance * monthly_rate
        return interest
    
    def apply_monthly_interest(self) -> None:
        """Apply monthly interest to account"""
        interest = self.__calculate_interest()
        self._balance += interest
        self._add_transaction("interest", interest, 
                            f"Monthly interest at {self.interest_rate}% p.a.")
        print(f" Interest credited: ${interest:.2f}. New balance: ${self._balance:.2f}")


# ============== CURRENT ACCOUNT ==============
class CurrentAccount(BankAccount):
    """Current account for businesses with overdraft facility"""
    
    def __init__(self, account_number: str, account_holder: str, initial_balance: float,
                 overdraft_limit: float = 100000.0, transaction_fee: float = 2.5):
        super().__init__(account_number, account_holder, initial_balance)
        self.overdraft_limit = overdraft_limit
        self.transaction_fee = transaction_fee
    
    def deposit(self, amount: float) -> None:
        """Deposit money into current account"""
        self._validate_amount(amount)
        self._balance += amount
        self._add_transaction("deposit", amount, "Deposit to Current Account")
        print(f" Deposited ${amount:.2f}. New balance: ${self._balance:.2f}")
    
    def withdraw(self, amount: float) -> None:
        """Withdraw money with overdraft facility"""
        self._validate_amount(amount)
        
        # Check if withdrawal exceeds balance + overdraft limit
        available_funds = self._balance + self.overdraft_limit
        if amount > available_funds:
            raise InsufficientFundsError(
                f"Insufficient funds including overdraft. Available: ${available_funds:.2f}"
            )
        
        # Deduct amount and transaction fee
        total_deduction = amount + self.transaction_fee
        self._balance -= total_deduction
        self._add_transaction("withdraw", amount, 
                            f"Withdrawal (Fee: ${self.transaction_fee:.2f})")
        print(f" Withdrawn ${amount:.2f} (Fee: ${self.transaction_fee:.2f}). "
              f"New balance: ${self._balance:.2f}")
    
    def transfer(self, recipient_account: BankAccount, amount: float) -> None:
        """Transfer money with transaction fee"""
        self._validate_amount(amount)
        
        try:
            self.withdraw(amount)
            recipient_account.deposit(amount)
            print(f" Transferred ${amount:.2f} to {recipient_account.account_holder}")
        except Exception as e:
            # Rollback on failure
            self._balance += (amount + self.transaction_fee)
            raise e


# ============== FIXED DEPOSIT ==============
class FixedDeposit(BankAccount):
    """Fixed deposit account with locked period and penalties"""
    
    def __init__(self, account_number: str, account_holder: str, initial_balance: float,
                 lock_period: int, interest_rate: float = 7.0, 
                 penalty_for_early_withdrawal: float = 2.0):
        super().__init__(account_number, account_holder, initial_balance)
        self.lock_period = lock_period  # in months
        self.interest_rate = interest_rate
        self.penalty_for_early_withdrawal = penalty_for_early_withdrawal
        self.maturity_amount = self.__calculate_maturity()
        self.maturity_date = datetime.now()
        self.creation_date = datetime.now()
    
    def __calculate_maturity(self) -> float:
        """Private method to calculate maturity amount"""
        # Simple interest calculation
        principal = self._balance
        rate = self.interest_rate / 100
        time = self.lock_period / 12  # Convert months to years
        maturity = principal * (1 + rate * time)
        return maturity
    
    def deposit(self, amount: float) -> None:
        """Fixed deposits don't allow additional deposits"""
        raise InvalidAmountError("Cannot deposit into Fixed Deposit after creation")
    
    def withdraw(self, amount: float) -> None:
        """Withdraw with penalty if before maturity"""
        self._validate_amount(amount)
        
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Insufficient funds. Available: ${self._balance:.2f}"
            )
        
        # Check if withdrawn before maturity
        months_elapsed = (datetime.now() - self.creation_date).days / 30
        
        if months_elapsed < self.lock_period:
            penalty = amount * (self.penalty_for_early_withdrawal / 100)
            total_deduction = amount + penalty
            
            if total_deduction > self._balance:
                raise InsufficientFundsError(
                    f"Insufficient funds including penalty. Required: ${total_deduction:.2f}"
                )
            
            self._balance -= total_deduction
            self._add_transaction("early_withdrawal", amount, 
                                f"Early withdrawal (Penalty: ${penalty:.2f})")
            print(f" Early withdrawal penalty applied: ${penalty:.2f}")
            print(f" Withdrawn ${amount:.2f}. New balance: ${self._balance:.2f}")
        else:
            # Mature withdrawal - no penalty
            self._balance -= amount
            self._add_transaction("withdraw", amount, "Maturity withdrawal")
            print(f" Withdrawn ${amount:.2f}. New balance: ${self._balance:.2f}")
    
    def transfer(self, recipient_account: BankAccount, amount: float) -> None:
        """Transfer not allowed for Fixed Deposits"""
        raise InvalidAmountError("Transfers not allowed from Fixed Deposit accounts")
    
    def check_maturity(self) -> None:
        """Check maturity status"""
        months_elapsed = (datetime.now() - self.creation_date).days / 30
        if months_elapsed >= self.lock_period:
            print(f" FD has matured! Maturity amount: ${self.maturity_amount:.2f}")
        else:
            remaining = self.lock_period - months_elapsed
            print(f" FD matures in {remaining:.1f} months. "
                  f"Expected maturity: ${self.maturity_amount:.2f}")


# ============== STUDENT ACCOUNT ==============
class StudentAccount(BankAccount):
    """Student account with free transactions and monthly allowance"""
    
    def __init__(self, account_number: str, account_holder: str, initial_balance: float,
                 parent_guardian: str, free_transactions: int = 10, 
                 monthly_allowance: float = 1000.0):
        super().__init__(account_number, account_holder, initial_balance)
        self.parent_guardian = parent_guardian
        self.free_transactions = free_transactions
        self.monthly_allowance = monthly_allowance
        self.transactions_this_month = 0
        self.transaction_fee = 1.0  # Fee after free transactions exhausted
    
    def deposit(self, amount: float) -> None:
        """Deposit money into student account"""
        self._validate_amount(amount)
        self._balance += amount
        self._add_transaction("deposit", amount, "Deposit to Student Account")
        print(f" Deposited ${amount:.2f}. New balance: ${self._balance:.2f}")
    
    def withdraw(self, amount: float) -> None:
        """Withdraw with free transaction limit"""
        self._validate_amount(amount)
        
        # Check monthly allowance limit
        if amount > self.monthly_allowance:
            raise WithdrawalLimitExceededError(
                f"Withdrawal ${amount:.2f} exceeds monthly allowance of ${self.monthly_allowance:.2f}"
            )
        
        # Calculate fee if free transactions exhausted
        fee = 0.0
        if self.transactions_this_month >= self.free_transactions:
            fee = self.transaction_fee
        
        total_deduction = amount + fee
        
        if total_deduction > self._balance:
            raise InsufficientFundsError(
                f"Insufficient funds. Available: ${self._balance:.2f}, Required: ${total_deduction:.2f}"
            )
        
        self._balance -= total_deduction
        self.transactions_this_month += 1
        
        fee_msg = f" (Fee: ${fee:.2f})" if fee > 0 else " (Free transaction)"
        self._add_transaction("withdraw", amount, f"Withdrawal{fee_msg}")
        print(f" Withdrawn ${amount:.2f}{fee_msg}. New balance: ${self._balance:.2f}")
        print(f"  Free transactions remaining: "
              f"{max(0, self.free_transactions - self.transactions_this_month)}")
    
    def transfer(self, recipient_account: BankAccount, amount: float) -> None:
        """Transfer money with transaction counting"""
        self._validate_amount(amount)
        
        try:
            self.withdraw(amount)
            recipient_account.deposit(amount)
            print(f" Transferred ${amount:.2f} to {recipient_account.account_holder}")
        except Exception as e:
            # Rollback on failure
            fee = self.transaction_fee if self.transactions_this_month > self.free_transactions else 0
            self._balance += (amount + fee)
            self.transactions_this_month -= 1
            raise e
    
    def receive_allowance(self) -> None:
        """Receive monthly allowance from parent/guardian"""
        self._balance += self.monthly_allowance
        self.transactions_this_month = 0  # Reset transaction counter
        self._add_transaction("allowance", self.monthly_allowance, 
                            f"Monthly allowance from {self.parent_guardian}")
        print(f" Monthly allowance received: ${self.monthly_allowance:.2f}")


# ============== DEMONSTRATION ==============
if __name__ == "__main__":
    print("=" * 70)
    print(" MODERN BANKING SYSTEM DEMONSTRATION")
    print("=" * 70)
    
    try:
        # Create different account types
        savings = SavingsAccount("SAV001", "Saynatn", 50000.0, interest_rate=5.0)
        current = CurrentAccount("CUR001", "Raju's Business", 19000.0)
        fixed = FixedDeposit("FD001", "Diya", 58090.0, lock_period=12, interest_rate=9.5)
        student = StudentAccount("STU001", "Priyanka", 500000.0, parent_guardian="Sayandeep")
        
        print("\n" + "="*70)
        print("1. SAVINGS ACCOUNT OPERATIONS")
        print("="*70)
        print(savings)
        savings.deposit(20000)
        savings.withdraw(1050)
        savings.apply_monthly_interest()
        
        print("\n" + "="*70)
        print("2. CURRENT ACCOUNT OPERATIONS")
        print("="*70)
        print(current)
        current.deposit(5400)
        current.withdraw(3070)
        
        print("\n" + "="*70)
        print("3. TRANSFER BETWEEN ACCOUNTS")
        print("="*70)
        savings.transfer(current, 5000)
        
        print("\n" + "="*70)
        print("4. FIXED DEPOSIT OPERATIONS")
        print("="*70)
        print(fixed)
        fixed.check_maturity()
        
        print("\n" + "="*70)
        print("5. STUDENT ACCOUNT OPERATIONS")
        print("="*70)
        print(student)
        student.deposit(2000)
        student.withdraw(500)
        student.receive_allowance()
        
        print("\n" + "="*70)
        print("6. TRANSACTION HISTORY")
        print("="*70)
        savings.print_statement(last_n=5)
        
        print("\n" + "="*70)
        print("7. ERROR HANDLING DEMONSTRATION")
        print("="*70)
        
        # Try to withdraw more than balance
        try:
            savings.withdraw(1000000)
        except InsufficientFundsError as e:
            print(f" Error: {e}")
        
        # Try to violate minimum balance
        try:
            savings.withdraw(70000)
        except MinimumBalanceError as e:
            print(f" Error: {e}")
        
        # Try to exceed withdrawal limit
        try:
            savings.withdraw(90000)
        except WithdrawalLimitExceededError as e:
            print(f" Error: {e}")
        
        # Try early FD withdrawal
        print("\nAttempting early FD withdrawal...")
        try:
            fixed.withdraw(20000)
        except Exception as e:
            print(f"Note: {e}")
        
        print("\n" + "="*70)
        print(" DEMONSTRATION COMPLETE")
        print("="*70)
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")