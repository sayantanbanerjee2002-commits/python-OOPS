from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict

class ClaimStatus(Enum):
    """Status of insurance claims"""
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    SETTLED = "Settled"

class CoverageType(Enum):
    """Types of vehicle insurance coverage"""
    COMPREHENSIVE = "Comprehensive"  # Covers everything
    THIRD_PARTY = "Third Party"      # Covers only damage to others

class InsurancePolicy(ABC):
    """
    Abstract base class for all insurance policies.
    """
    
    def __init__(self, policy_number: str, holder_name: str, premium: float, coverage_amount: float):
        """
        Initialize common attributes for all policies.
        """
        self.policy_number = policy_number
        self.holder_name = holder_name
        self.premium = premium
        self.coverage_amount = coverage_amount
        self.start_date = datetime.now()
        self.end_date = self.start_date + timedelta(days=365)  # 1 year policy
        self.is_active = True
        self.claims_made = 0  # Track number of claims
    
    @abstractmethod
    def calculate_premium(self, risk_factors: Dict) -> float:
        """
        Abstract method - each policy type must implement its own premium calculation.
        """
        pass
    
    def renew_policy(self, no_claim_discount: float = 0) -> float:
        """
        Renew the policy for another year.
        Give discount if customer didn't make any claims.
        
        Returns:
            New premium amount after discount
        """
        # Calculate discount amount
        discount_amount = self.premium * (no_claim_discount / 100)
        # Apply discount
        new_premium = self.premium - discount_amount
        # Update premium and dates
        self.premium = new_premium
        self.start_date = datetime.now()
        self.end_date = self.start_date + timedelta(days=365)
        # Reset claim counter
        self.claims_made = 0
        return new_premium
    
    def __str__(self):
        """String representation for easy printing"""
        return f"Policy {self.policy_number} - {self.holder_name} - Premium: ${self.premium:.2f}"


class HealthInsurance(InsurancePolicy):
    """Health insurance policy with medical coverage details"""
    
    def __init__(self, policy_number: str, holder_name: str, premium: float, 
                 coverage_amount: float, covered_diseases: List[str], 
                 hospital_network: List[str], co_pay_percentage: float):
        """
        Initialize health insurance policy.
        
        Args:
            covered_diseases: List of diseases covered (e.g., ["Cancer", "Diabetes"])
            hospital_network: List of hospitals where policy is valid
            co_pay_percentage: Percentage customer pays from their pocket (rest is insurance)
        """
        super().__init__(policy_number, holder_name, premium, coverage_amount)
        self.covered_diseases = covered_diseases
        self.hospital_network = hospital_network
        self.co_pay_percentage = co_pay_percentage
    
    def calculate_premium(self, risk_factors: Dict) -> float:

        base_premium = self.coverage_amount * 0.05  # 5% of coverage as base
        
        # Age factor: charge more for older people
        age = risk_factors.get('age', 30)
        if age > 60:
            base_premium *= 1.5  # 50% more for seniors
        elif age > 45:
            base_premium *= 1.3  # 30% more for middle-aged
        elif age > 30:
            base_premium *= 1.1  # 10% more for adults
        
        # Pre-existing conditions: charge more for each disease
        pre_existing = risk_factors.get('pre_existing_diseases', 0)
        base_premium *= (1 + pre_existing * 0.2)  # 20% more per disease
        
        # Smoking: charge 25% more for smokers
        if risk_factors.get('smoking', False):
            base_premium *= 1.25
        
        self.premium = base_premium
        return base_premium

class VehicleInsurance(InsurancePolicy):
    """Vehicle insurance policy for cars/bikes"""
    
    def __init__(self, policy_number: str, holder_name: str, premium: float,
                 coverage_amount: float, vehicle_details: Dict, 
                 coverage_type: CoverageType, no_claim_bonus: float = 0):
   
        super().__init__(policy_number, holder_name, premium, coverage_amount)
        self.vehicle_details = vehicle_details
        self.coverage_type = coverage_type
        self.no_claim_bonus = no_claim_bonus
    
    def calculate_premium(self, risk_factors: Dict) -> float:
        """
        Calculate vehicle insurance premium based on risk factors.
        
        Risk factors:
        - vehicle_age: Older vehicles = lower premium
        - driver_age: Young drivers = higher risk
        - accident_history: More accidents = higher premium
        - vehicle_value: Expensive vehicles = higher premium
        """
        # Base premium depends on coverage type
        if self.coverage_type == CoverageType.COMPREHENSIVE:
            base_premium = self.coverage_amount * 0.04  # 4% for full coverage
        else:
            base_premium = self.coverage_amount * 0.02  # 2% for third-party only
        
        # Vehicle age: newer vehicles cost more to insure
        vehicle_age = risk_factors.get('vehicle_age', 5)
        if vehicle_age < 2:
            base_premium *= 1.2  # 20% more for new vehicles
        elif vehicle_age > 10:
            base_premium *= 0.8  # 20% discount for old vehicles
        
        # Driver age: young drivers are risky
        driver_age = risk_factors.get('driver_age', 30)
        if driver_age < 25:
            base_premium *= 1.4  # 40% more for young drivers
        elif driver_age > 60:
            base_premium *= 1.2  # 20% more for senior drivers
        
        # Accident history: charge more for each previous accident
        accidents = risk_factors.get('accident_history', 0)
        base_premium *= (1 + accidents * 0.15)  # 15% more per accident
        
        # Apply no-claim bonus (discount for safe drivers)
        base_premium *= (1 - self.no_claim_bonus / 100)
        
        self.premium = base_premium
        return base_premium
    
    def update_no_claim_bonus(self):
        """
        Increase no-claim bonus if customer didn't make claims.
        Maximum bonus is capped at 50%.
        """
        if self.claims_made == 0:
            self.no_claim_bonus = min(self.no_claim_bonus + 10, 50)  # Add 10%, max 50%
        else:
            self.no_claim_bonus = 0  # Reset if claim was made

class LifeInsurance(InsurancePolicy):
    """Life insurance policy with beneficiary details"""
    
    def __init__(self, policy_number: str, holder_name: str, premium: float,
                 coverage_amount: float, beneficiaries: List[Dict], 
                 term_years: int, maturity_amount: float, riders: List[str]):
        """
        Initialize life insurance policy.
        
        Args:
            beneficiaries: List of people who get money (with their share %)
            term_years: How many years the policy runs
            maturity_amount: Amount paid if person survives the term
            riders: Additional benefits (e.g., "Accidental Death", "Critical Illness")
        """
        super().__init__(policy_number, holder_name, premium, coverage_amount)
        self.beneficiaries = beneficiaries  # [{"name": "John", "share": 50}, ...]
        self.term_years = term_years
        self.maturity_amount = maturity_amount
        self.riders = riders
    
    def calculate_premium(self, risk_factors: Dict) -> float:
        """
        Calculate life insurance premium based on risk factors.
        
        Risk factors:
        - age: Older = higher mortality risk
        - health_condition: Poor health = higher risk
        - occupation: Dangerous jobs = higher risk
        - term_years: Longer term = lower annual premium
        """
        # Base premium: coverage divided by term years
        base_premium = self.coverage_amount / self.term_years * 0.02  # 2% per year
        
        # Age factor: older people have higher mortality risk
        age = risk_factors.get('age', 30)
        if age > 60:
            base_premium *= 2.0  # Double for seniors
        elif age > 50:
            base_premium *= 1.6
        elif age > 40:
            base_premium *= 1.3
        
        # Health condition: poor health = higher premium
        health_score = risk_factors.get('health_score', 5)  # Scale 1-10
        base_premium *= (11 - health_score) / 5  # Lower health = higher premium
        
        # Occupation risk: dangerous jobs cost more
        occupation_risk = risk_factors.get('occupation_risk', 'low')  # low/medium/high
        if occupation_risk == 'high':
            base_premium *= 1.5
        elif occupation_risk == 'medium':
            base_premium *= 1.2
        
        # Add cost for riders (additional benefits)
        rider_cost = len(self.riders) * 500  # $500 per rider per year
        base_premium += rider_cost
        
        self.premium = base_premium
        return base_premium

class HomeInsurance(InsurancePolicy):
    """Home insurance policy for property protection"""
    
    def __init__(self, policy_number: str, holder_name: str, premium: float,
                 coverage_amount: float, property_value: float, 
                 covered_risks: List[str], deductible_amount: float):
        """
        Initialize home insurance policy.
        
        Args:
            property_value: Total value of the property
            covered_risks: List of risks covered (e.g., "Fire", "Theft", "Flood")
            deductible_amount: Amount customer pays before insurance kicks in
        """
        super().__init__(policy_number, holder_name, premium, coverage_amount)
        self.property_value = property_value
        self.covered_risks = covered_risks
        self.deductible_amount = deductible_amount
    
    def calculate_premium(self, risk_factors: Dict) -> float:
        """
        Calculate home insurance premium based on risk factors.
        
        Risk factors:
        - location_risk: High crime/flood areas = higher premium
        - property_age: Older buildings = higher risk
        - security_systems: Good security = discount
        - construction_type: Fire-resistant materials = discount
        """
        # Base premium: percentage of property value
        base_premium = self.property_value * 0.005  # 0.5% of property value
        
        # Location risk: high-risk areas cost more
        location_risk = risk_factors.get('location_risk', 'medium')  # low/medium/high
        if location_risk == 'high':
            base_premium *= 1.6
        elif location_risk == 'medium':
            base_premium *= 1.2
        
        # Property age: older buildings are riskier
        property_age = risk_factors.get('property_age', 10)
        if property_age > 50:
            base_premium *= 1.5
        elif property_age > 30:
            base_premium *= 1.3
        elif property_age < 5:
            base_premium *= 0.9  # 10% discount for new buildings
        
        # Security systems: give discount for good security
        has_security = risk_factors.get('has_security_system', False)
        if has_security:
            base_premium *= 0.85  # 15% discount
        
        # Construction type: fire-resistant = discount
        fire_resistant = risk_factors.get('fire_resistant', False)
        if fire_resistant:
            base_premium *= 0.9  # 10% discount
        
        # Add cost for each risk covered
        risk_cost = len(self.covered_risks) * 200  # $200 per risk type
        base_premium += risk_cost
        
        self.premium = base_premium
        return base_premium



class PolicyHolder:
    """Person who owns insurance policies"""
    
    def __init__(self, name: str, age: int):
        """
        Initialize a policy holder.
        
        Args:
            name: Full name of the person
            age: Current age
        """
        self.name = name
        self.age = age
        self.policies_owned: List[InsurancePolicy] = []  # List of policies they have
        self.claim_history: List['Claim'] = []  # List of claims they've made
    
    def add_policy(self, policy: InsurancePolicy):
        """Add a new policy to this person's portfolio"""
        self.policies_owned.append(policy)
    
    def get_total_coverage(self) -> float:
        """Calculate total coverage amount across all policies"""
        return sum(policy.coverage_amount for policy in self.policies_owned)
    
    def get_total_premium(self) -> float:
        """Calculate total premium paid annually for all policies"""
        return sum(policy.premium for policy in self.policies_owned)
    
    def get_claim_count(self) -> int:
        """Get total number of claims made by this person"""
        return len(self.claim_history)
    
    def __str__(self):
        return f"PolicyHolder: {self.name}, Age: {self.age}, Policies: {len(self.policies_owned)}"


class Claim:
    """Represents an insurance claim request"""
    
    def __init__(self, policy: InsurancePolicy, claim_amount: float, 
                 claim_date: datetime, documents: List[str]):
        """
        Initialize a claim.
        
        Args:
            policy: The insurance policy being claimed against
            claim_amount: Amount of money being requested
            claim_date: When the incident happened
            documents: List of supporting documents (e.g., bills, photos)
        """
        self.policy = policy
        self.claim_amount = claim_amount
        self.claim_date = claim_date
        self.status = ClaimStatus.PENDING  # Start as pending
        self.documents = documents
        self.settlement_amount = 0.0  # Amount actually paid (0 until approved)
        self.rejection_reason = None  # Why it was rejected (if rejected)
    
    def validate_claim(self) -> tuple[bool, str]:
        """
        Validate if the claim is eligible for processing.
        
        Returns:
            (is_valid, reason) - True/False and explanation
        """
        # Check 1: Policy must be active
        if not self.policy.is_active:
            return False, "Policy is not active"
        
        # Check 2: Claim must be within policy period
        if self.claim_date < self.policy.start_date or self.claim_date > self.policy.end_date:
            return False, "Claim date is outside policy coverage period"
        
        # Check 3: Claim amount can't exceed coverage
        if self.claim_amount > self.policy.coverage_amount:
            return False, f"Claim amount exceeds coverage limit of ${self.policy.coverage_amount}"
        
        # Check 4: Must have supporting documents
        if len(self.documents) == 0:
            return False, "No supporting documents provided"
        
        return True, "Claim is valid"
    
    def approve_claim(self, settlement_percentage: float = 100):
        """
        Approve the claim and calculate settlement amount.
        
        Args:
            settlement_percentage: What % of claim amount to pay (default 100%)
        """
        # Validate first
        is_valid, reason = self.validate_claim()
        if not is_valid:
            self.reject_claim(reason)
            return
        
        # Calculate settlement based on policy type
        if isinstance(self.policy, HealthInsurance):
            # For health insurance, apply co-pay
            customer_pays = self.claim_amount * (self.policy.co_pay_percentage / 100)
            insurance_pays = self.claim_amount - customer_pays
            self.settlement_amount = insurance_pays
        
        elif isinstance(self.policy, HomeInsurance):
            # For home insurance, deduct deductible
            after_deductible = max(0, self.claim_amount - self.policy.deductible_amount)
            self.settlement_amount = after_deductible * (settlement_percentage / 100)
        
        else:
            # For other policies, pay the settlement percentage
            self.settlement_amount = self.claim_amount * (settlement_percentage / 100)
        
        # Update status
        self.status = ClaimStatus.APPROVED
        self.policy.claims_made += 1  # Increment claim counter
        
        print(f" Claim approved! Settlement: ${self.settlement_amount:.2f}")
    
    def reject_claim(self, reason: str):
        """Reject the claim with a reason"""
        self.status = ClaimStatus.REJECTED
        self.rejection_reason = reason
        self.settlement_amount = 0.0
        print(f" Claim rejected: {reason}")
    
    def settle_claim(self):
        """Mark claim as settled (payment completed)"""
        if self.status == ClaimStatus.APPROVED:
            self.status = ClaimStatus.SETTLED
            print(f"Payment of ${self.settlement_amount:.2f} has been processed.")
        else:
            print("Cannot settle claim - not approved yet")
    
    def __str__(self):
        return f"Claim for {self.policy.policy_number} - ${self.claim_amount:.2f} - {self.status.value}"



class Agent:
    """Insurance agent who sells policies and earns commission"""
    
    def __init__(self, agent_id: str, name: str, commission_rate: float):
        """
        Initialize an insurance agent.
        
        Args:
            agent_id: Unique agent ID
            name: Agent's name
            commission_rate: Percentage commission on premiums sold (e.g., 10 for 10%)
        """
        self.agent_id = agent_id
        self.name = name
        self.commission_rate = commission_rate
        self.policies_sold: List[InsurancePolicy] = []  # Track policies sold
        self.total_commission = 0.0
    
    def sell_policy(self, policy: InsurancePolicy):
        """
        Record a policy sale and calculate commission.
        
        Args:
            policy: The policy that was sold
        """
        self.policies_sold.append(policy)
        # Commission is percentage of first year premium
        commission = policy.premium * (self.commission_rate / 100)
        self.total_commission += commission
        print(f"Agent {self.name} sold policy {policy.policy_number} and earned ${commission:.2f}")
    
    def calculate_monthly_commission(self) -> float:
        """Calculate commission earned in current month"""
        # In real system, would filter by date
        # For simplicity, divide annual commission by 12
        return self.total_commission / 12
    
    def get_performance_summary(self) -> Dict:
        """Get agent's performance statistics"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "policies_sold": len(self.policies_sold),
            "total_commission": self.total_commission,
            "average_policy_value": sum(p.premium for p in self.policies_sold) / len(self.policies_sold) if self.policies_sold else 0
        }
    
    def __str__(self):
        return f"Agent {self.name} (ID: {self.agent_id}) - Policies Sold: {len(self.policies_sold)}, Commission: ${self.total_commission:.2f}"



def main():
    """Demonstrate the insurance system with examples"""
    
    print("=" * 60)
    print("INSURANCE POLICY MANAGEMENT SYSTEM - DEMO")
    print("=" * 60)
    
    # Create an insurance agent
    print("\n1. Creating Insurance Agent...")
    agent = Agent("AGT001", "John Smith", commission_rate=10)
    print(f"   {agent}")
    
    # Create a policy holder
    print("\n2. Creating Policy Holder...")
    holder = PolicyHolder("Alice Johnson", age=35)
    print(f"   {holder}")
    
    # Create a health insurance policy
    print("\n3. Creating Health Insurance Policy...")
    health_policy = HealthInsurance(
        policy_number="HLTH001",
        holder_name="Alice Johnson",
        premium=0,  # Will be calculated
        coverage_amount=500000,
        covered_diseases=["Cancer", "Heart Disease", "Diabetes"],
        hospital_network=["City Hospital", "Metro Clinic", "Care Center"],
        co_pay_percentage=20
    )
    
    # Calculate premium based on risk factors
    health_risk_factors = {
        'age': 35,
        'pre_existing_diseases': 1,  # Has diabetes
        'smoking': False
    }
    premium = health_policy.calculate_premium(health_risk_factors)
    print(f"   Premium calculated: ${premium:.2f}")
    print(f"   Coverage: ${health_policy.coverage_amount}")
    print(f"   Co-pay: {health_policy.co_pay_percentage}%")
    
    # Agent sells the policy
    agent.sell_policy(health_policy)
    holder.add_policy(health_policy)
    
    # Create a vehicle insurance policy
    print("\n4. Creating Vehicle Insurance Policy...")
    vehicle_policy = VehicleInsurance(
        policy_number="VEH001",
        holder_name="Alice Johnson",
        premium=0,
        coverage_amount=50000,
        vehicle_details={
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "registration": "ABC123"
        },
        coverage_type=CoverageType.COMPREHENSIVE,
        no_claim_bonus=10  # 10% existing bonus
    )
    
    vehicle_risk_factors = {
        'vehicle_age': 4,
        'driver_age': 35,
        'accident_history': 0
    }
    premium = vehicle_policy.calculate_premium(vehicle_risk_factors)
    print(f"   Premium calculated: ${premium:.2f}")
    print(f"   Coverage Type: {vehicle_policy.coverage_type.value}")
    print(f"   No-Claim Bonus: {vehicle_policy.no_claim_bonus}%")
    
    agent.sell_policy(vehicle_policy)
    holder.add_policy(vehicle_policy)
    
    # Display policy holder summary
    print("\n5. Policy Holder Summary...")
    print(f"   Total Policies: {len(holder.policies_owned)}")
    print(f"   Total Coverage: ${holder.get_total_coverage():,.2f}")
    print(f"   Total Annual Premium: ${holder.get_total_premium():.2f}")
    
    # Create and process a claim
    print("\n6. Filing a Health Insurance Claim...")
    claim = Claim(
        policy=health_policy,
        claim_amount=10000,
        claim_date=datetime.now(),
        documents=["hospital_bill.pdf", "prescription.pdf", "doctor_report.pdf"]
    )
    
    print(f"   Claim Amount: ${claim.claim_amount}")
    print(f"   Documents: {len(claim.documents)} files")
    
    # Validate and approve claim
    print("\n7. Processing Claim...")
    is_valid, reason = claim.validate_claim()
    print(f"   Validation: {reason}")
    
    if is_valid:
        claim.approve_claim()
        print(f"   Customer pays (20% co-pay): ${claim.claim_amount * 0.2:.2f}")
        print(f"   Insurance pays: ${claim.settlement_amount:.2f}")
        claim.settle_claim()
        holder.claim_history.append(claim)
    
    # Policy renewal with no-claim bonus
    print("\n8. Renewing Vehicle Insurance...")
    vehicle_policy.update_no_claim_bonus()  # Update bonus before renewal
    print(f"   Updated No-Claim Bonus: {vehicle_policy.no_claim_bonus}%")
    
    old_premium = vehicle_policy.premium
    new_premium = vehicle_policy.renew_policy(no_claim_discount=vehicle_policy.no_claim_bonus)
    print(f"   Old Premium: ${old_premium:.2f}")
    print(f"   New Premium: ${new_premium:.2f}")
    print(f"   Savings: ${old_premium - new_premium:.2f}")
    
    # Agent performance summary
    print("\n9. Agent Performance Summary...")
    performance = agent.get_performance_summary()
    print(f"   Agent: {performance['name']}")
    print(f"   Policies Sold: {performance['policies_sold']}")
    print(f"   Total Commission Earned: ${performance['total_commission']:.2f}")
    print(f"   Average Policy Value: ${performance['average_policy_value']:.2f}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)

# Run the demonstration
if __name__ == "__main__":
    main()