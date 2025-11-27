from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from sqlalchemy import event


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)  # can be email
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='client')  # 'owner' or 'client'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True)
    company = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    tax_id = db.Column(db.String(50))
    address = db.Column(db.String(250))
    invoices = db.relationship('Invoice', backref='client', lazy=True)

    def total_outstanding(self):
        return sum(inv.amount - (inv.paid or 0) for inv in self.invoices)


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.String(50), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    description = db.Column(db.String(250))
    amount = db.Column(db.Float, nullable=False, default=0.0)
    payment_type = db.Column(db.String(50), default='Full Payment')  # 'Full Payment' or 'Installment'
    paid = db.Column(db.Float, default=0.0)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='pending')  # pending/partial/paid/overdue
    # When an invoice is deleted we want its payments removed as well to avoid
    # leaving orphaned Payment rows with a NULL `invoice_id` (which violates
    # the NOT NULL constraint). Use cascade so SQLAlchemy deletes payments
    # in the same transaction instead of attempting to NULL their FK.
    payments = db.relationship('Payment', backref='invoice', lazy=True,
                               cascade='all, delete-orphan')

    # Installment fields
    installments = db.Column(db.Integer, default=1)   # total number of installments
    frequency = db.Column(db.String(20), default='monthly')   # weekly/biweekly/monthly

    @property
    def installment_amount(self):
        """Calculate per-installment amount dynamically."""
        if self.installments and self.installments > 0:
            return round(self.amount / self.installments, 2)
        return 0.0

    def installments_paid(self):
        """Estimate how many installments have been paid.

        Logic:
        - If payments explicitly include `installment_number`, count them.
        - Otherwise, fall back to dividing total paid by the per-installment amount
          and flooring the result (bounded by `self.installments`).
        This makes the method tolerant to payments created as plain amounts
        (no installment_number) while still supporting explicit numbering.
        """
        # Count explicit installment numbers (unique, non-null)
        explicit = {int(n) for n in (p.installment_number for p in self.payments) if n}
        explicit_count = len(explicit)

        # Compute amount-based coverage (how many installments are covered by total paid)
        try:
            per_inst = float(self.installment_amount or 0)
        except Exception:
            per_inst = 0.0

        total_paid = sum((p.amount or 0) for p in self.payments)
        amount_based = 0
        if per_inst > 0 and self.installments and self.installments > 0 and total_paid > 0:
            from math import ceil
            amount_based = int(ceil(total_paid / per_inst))

        # Use the larger of explicit_count and amount_based to avoid under-reporting when
        # historical payments exist without installment_number values.
        counted = max(explicit_count, amount_based)
        # Do not exceed configured number of installments
        if self.installments and self.installments > 0:
            counted = max(0, min(counted, int(self.installments)))
        return counted

    @property
    def installments_display(self):
        """Return a display-friendly count for installments paid.

        Ensures that if any payment exists toward an installment plan the UI
        shows at least 1 (e.g., 1/4) instead of 0/4 when there is a small partial
        payment recorded. Prefers explicit installment numbering when available.
        """
        paid_count = self.installments_paid()
        # If none recorded but some money has been paid, show 1 for UX clarity
        total_paid = sum((p.amount or 0) for p in self.payments) or (self.paid or 0)
        if paid_count == 0 and total_paid > 0:
            return 1
        return paid_count

    def installments_remaining(self):
        """Remaining installments based on total vs paid."""
        return max(self.installments - self.installments_paid(), 0)

    def remaining_balance(self):
        return max(self.amount - (self.paid or 0), 0.0)

    @property
    def remaining_amount(self):
        """Backward-compatible alias used in templates for remaining balance."""
        return self.remaining_balance()
    
    def is_overdue(self):
        return self.status != 'paid' and self.due_date and self.due_date < date.today()

    @staticmethod
    def generate_invoice_no():
        """Generate sequential invoice numbers like INV-2025-001."""
        year = date.today().year
        last_invoice = Invoice.query.filter(Invoice.invoice_no.like(f"INV-{year}-%")) \
                                    .order_by(Invoice.id.desc()).first()
        if last_invoice:
            try:
                last_number = int(last_invoice.invoice_no.split('-')[-1])
            except ValueError:
                last_number = 0
            new_number = last_number + 1
        else:
            new_number = 1
        return f"INV-{year}-{new_number:03d}"


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    method = db.Column(db.String(50))
    date = db.Column(db.Date, default=date.today)

    # Track installment number (optional for full payments)
    installment_number = db.Column(db.Integer, nullable=True)


# --- Event listener to auto-generate invoice_no before insert ---
def set_invoice_no(mapper, connection, target):
    if not target.invoice_no:
        target.invoice_no = Invoice.generate_invoice_no()

event.listen(Invoice, 'before_insert', set_invoice_no)