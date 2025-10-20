
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
from typing import List, Dict, Optional, Deque, Tuple
import uuid
import random

#  Helper functions 

def generate_qr_code() -> str:
    """Simulate a QR code payload with UUID."""
    return str(uuid.uuid4())

#  Domain classes 

@dataclass
class Venue:
    name: str
    location: str
    capacity: int
    amenities: List[str] = field(default_factory=list)
    rental_cost: float = 0.0
    availability: Dict[datetime, bool] = field(default_factory=dict)

    def is_available(self, date: datetime) -> bool:
        return self.availability.get(date, True)

    def reserve(self, date: datetime) -> None:
        self.availability[date] = False


@dataclass
class Organizer:
    name: str
    company: str
    events_organized: List[str] = field(default_factory=list)  # store event ids
    rating: Optional[float] = None

    def add_event(self, event_id: str) -> None:
        self.events_organized.append(event_id)


@dataclass
class Attendee:
    name: str
    email: str
    ticket_type: str  # 'VIP' | 'regular' | 'student'
    registration_date: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Ticket:
    ticket_id: str
    event_id: str
    attendee_email: str
    seat_number: Optional[str]
    purchase_price: float
    qr_code: str
    purchased_at: datetime = field(default_factory=datetime.utcnow)
    checked_in: bool = False
    refunded: bool = False

    def validate_qr(self, qr: str) -> bool:
        return (not self.refunded) and (self.qr_code == qr)

#  Event class 

class Event:
    EARLY_BIRD_DAYS = 30
    EARLY_BIRD_DISCOUNT = 0.20  # 20%

    def __init__(self,
                 event_id: str,
                 title: str,
                 date: datetime,
                 venue: Venue,
                 organizer: Organizer,
                 max_attendees: int,
                 ticket_price: float,
                 pricing_tiers: Optional[Dict[str, float]] = None):
        self.event_id = event_id
        self.title = title
        self.date = date
        self.venue = venue
        self.organizer = organizer
        self.max_attendees = max_attendees
        self.base_ticket_price = ticket_price
        # pricing_tiers: multiplier relative to base price
        # e.g. {'VIP': 2.0, 'regular': 1.0, 'student': 0.5}
        self.pricing_tiers = pricing_tiers or {'VIP': 2.0, 'regular': 1.0, 'student': 0.5}

        # Composition
        self.attendees: Dict[str, Attendee] = {}  # key: email
        self.tickets: Dict[str, Ticket] = {}  # key: ticket_id

        # track seat assignments if needed
        self.seats_taken: Dict[str, str] = {}  # seat_number -> ticket_id

        # Waitlist
        self.waitlist: Deque[Attendee] = deque()

        # Refunds ledger
        self.refunds: List[Tuple[str, float, datetime]] = []  # (ticket_id, amount, timestamp)

        # Organizer register
        organizer.add_event(event_id)

    # Registration & Ticketing 

    def _calculate_price(self, ticket_type: str, registration_date: datetime) -> float:
        multiplier = self.pricing_tiers.get(ticket_type, 1.0)
        price = self.base_ticket_price * multiplier
        # early bird
        days_before = (self.date - registration_date).days
        if days_before >= Event.EARLY_BIRD_DAYS:
            price *= (1.0 - Event.EARLY_BIRD_DISCOUNT)
        # round to 2 decimals
        return round(price, 2)

    def seats_available(self) -> int:
        return max(0, self.max_attendees - len(self.attendees))

    def register_attendee(self, attendee: Attendee, preferred_seat: Optional[str] = None) -> Tuple[Optional[Ticket], str]:
        """
        Register an attendee and produce a Ticket if there is capacity.
        If full, place the attendee on the waitlist.
        Returns (Ticket or None, message)
        """
        if attendee.email in self.attendees:
            return None, "Attendee already registered."

        if len(self.attendees) >= self.max_attendees:
            # add to waitlist
            self.waitlist.append(attendee)
            return None, "Event full — added to waitlist."

        # proceed to create ticket
        price = self._calculate_price(attendee.ticket_type, attendee.registration_date)
        ticket_id = str(uuid.uuid4())
        qr_code = generate_qr_code()
        ticket = Ticket(ticket_id=ticket_id,
                        event_id=self.event_id,
                        attendee_email=attendee.email,
                        seat_number=preferred_seat,
                        purchase_price=price,
                        qr_code=qr_code)

        # store
        self.attendees[attendee.email] = attendee
        self.tickets[ticket_id] = ticket
        if preferred_seat:
            self.seats_taken[preferred_seat] = ticket_id

        return ticket, "Registered and ticket issued."

    def promote_waitlist(self) -> List[Ticket]:
        """Try to move waitlisted attendees onto the main list when seats free up."""
        created = []
        while self.waitlist and len(self.attendees) < self.max_attendees:
            attendee = self.waitlist.popleft()
            ticket, msg = self.register_attendee(attendee)
            if ticket:
                created.append(ticket)
        return created

    # --- Check-in ---

    def check_in_by_qr(self, qr: str) -> Tuple[bool, str]:
        """Validate QR and mark ticket as checked-in."""
        for ticket in self.tickets.values():
            if ticket.validate_qr(qr):
                if ticket.checked_in:
                    return False, "Ticket already checked in."
                ticket.checked_in = True
                return True, f"Checked in: {ticket.attendee_email}"
        return False, "Invalid or refunded QR code."

    # -- Cancellation & Refunds --

    def cancel_ticket(self, ticket_id: str, request_date: Optional[datetime] = None) -> Tuple[bool, str]:
    
        request_date = request_date or datetime.utcnow()
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return False, "Ticket not found."
        if ticket.refunded:
            return False, "Ticket already refunded."

        days_before = (self.date - request_date).days
        if days_before >= 30:
            refund_pct = 1.0
        elif days_before >= 7:
            refund_pct = 0.5
        else:
            refund_pct = 0.0

        refund_amount = round(ticket.purchase_price * refund_pct, 2)
        ticket.refunded = True
        self.refunds.append((ticket_id, refund_amount, datetime.utcnow()))

        # remove attendee and free seat
        attendee_email = ticket.attendee_email
        if attendee_email in self.attendees:
            del self.attendees[attendee_email]

        if ticket.seat_number and ticket.seat_number in self.seats_taken:
            del self.seats_taken[ticket.seat_number]

        # try to promote waitlist
        self.promote_waitlist()

        return True, f"Refund processed: ${refund_amount:.2f}."

    # ---Contains ---

    def __contains__(self, attendee: Attendee) -> bool:
        return attendee.email in self.attendees

    # ---Analytics ---

    def attendance_rate(self) -> float:
        """Return the attendance rate as (checked_in / max_attendees).
        If max_attendees is 0 return 0.0"""
        if self.max_attendees == 0:
            return 0.0
        checked_in = sum(1 for t in self.tickets.values() if t.checked_in and not t.refunded)
        return round(checked_in / self.max_attendees, 4)

    def revenue(self) -> float:
        """Calculate net revenue = sum(all purchase prices for non-refunded tickets) - refunds recorded."""
        total_received = sum(t.purchase_price for t in self.tickets.values())
        total_refunds = sum(r[1] for r in self.refunds)
        return round(total_received - total_refunds, 2)

    def revenue_breakdown_by_tier(self) -> Dict[str, float]:
        breakdown = defaultdict(float)
        for t in self.tickets.values():
            if t.refunded:
                continue
            # We need attendee -> ticket_type; look up attendee
            attendee = self.attendees.get(t.attendee_email)
            if attendee:
                breakdown[attendee.ticket_type] += t.purchase_price
            else:
                # If attendee not found (e.g., removed after refund) attribute to 'unknown'
                breakdown['unknown'] += t.purchase_price
        return dict(breakdown)

    def demographics(self) -> Dict[str, int]:
        """Return counts by ticket_type and other simple demographics."""
        counts = defaultdict(int)
        for a in self.attendees.values():
            counts[a.ticket_type] += 1
        return dict(counts)

    def summary(self) -> Dict[str, object]:
        """Return a summary of key analytics."""
        total_registered = len(self.attendees)
        total_tickets = len([t for t in self.tickets.values() if not t.refunded])
        checked_in = sum(1 for t in self.tickets.values() if t.checked_in and not t.refunded)
        return {
            'event_id': self.event_id,
            'title': self.title,
            'date': self.date.isoformat(),
            'venue': self.venue.name,
            'max_attendees': self.max_attendees,
            'registered': total_registered,
            'tickets_issued': total_tickets,
            'checked_in': checked_in,
            'attendance_rate': self.attendance_rate(),
            'revenue': self.revenue(),
            'revenue_by_tier': self.revenue_breakdown_by_tier(),
            'demographics': self.demographics(),
            'waitlist_length': len(self.waitlist),
        }

# --- Demo / Example usage ---

if __name__ == "__main__":
    # Setup
    venue = Venue(name="Grand Hall",
                  location="Downtown",
                  capacity=100,
                  amenities=["Parking", "WiFi", "Projector"],
                  rental_cost=2000.0)

    org = Organizer(name="Priya Kumar", company="EventsRUs", rating=4.8)

    event_date = datetime.utcnow() + timedelta(days=45)
    event = Event(event_id="E-1001",
                  title="Tech Symposium",
                  date=event_date,
                  venue=venue,
                  organizer=org,
                  max_attendees=5,  # small for demo
                  ticket_price=50.0,
                  pricing_tiers={'VIP': 2.5, 'regular': 1.0, 'student': 0.6})

    # Register some attendees (some early, some late)
    attendees = [
        Attendee("Alice", "alice@example.com", "VIP", registration_date=datetime.utcnow()),
        Attendee("Bob", "bob@example.com", "regular", registration_date=datetime.utcnow() - timedelta(days=40)),
        Attendee("Carol", "carol@example.com", "student", registration_date=datetime.utcnow() - timedelta(days=31)),
        Attendee("Dave", "dave@example.com", "regular", registration_date=datetime.utcnow()),
        Attendee("Eve", "eve@example.com", "regular", registration_date=datetime.utcnow()),
        Attendee("Frank", "frank@example.com", "student", registration_date=datetime.utcnow()),
    ]

    tickets = []
    for a in attendees:
        ticket, msg = event.register_attendee(a)
        print(f"Register {a.email}: {msg}")
        if ticket:
            print(f"  Ticket {ticket.ticket_id} price ${ticket.purchase_price}")
            tickets.append(ticket)

    print('\nWaitlist length:', len(event.waitlist))

    # Cancel one ticket and observe waitlist promotion
    if tickets:
        to_cancel = tickets[0]
        ok, msg = event.cancel_ticket(to_cancel.ticket_id, request_date=datetime.utcnow())
        print(f"\nCancel ticket {to_cancel.ticket_id}: {msg}")

    print('\nAfter cancellation:')
    print('Registered:', len(event.attendees))
    print('Waitlist length:', len(event.waitlist))

    # Simulate check-ins (use valid and invalid QR)
    if tickets:
        valid_qr = tickets[1].qr_code
        ok, msg = event.check_in_by_qr(valid_qr)
        print(f"\nCheck-in with valid QR: {msg}")

        fake_qr = 'invalid-qr-token'
        ok, msg = event.check_in_by_qr(fake_qr)
        print(f"Check-in with invalid QR: {msg}")

    # Show analytics
    print('\nEvent Summary:')
    summary = event.summary()
    for k, v in summary.items():
        print(f"{k}: {v}")

    print('\nRevenue breakdown by tier:')
    print(event.revenue_breakdown_by_tier())

    print('\nDemographics:')
    print(event.demographics())
