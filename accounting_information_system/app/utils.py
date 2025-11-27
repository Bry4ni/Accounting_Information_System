from flask import abort
from flask_login import current_user
from functools import wraps

def owner_required(f):
    """Decorator that restricts access to owners/admins only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'owner':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def calculate_totals(invoices):
    """Calculate total revenue, total paid and outstanding for given invoice list."""
    total_revenue = sum((inv.amount or 0) for inv in invoices)
    total_paid = sum((inv.paid or 0) for inv in invoices)
    outstanding = total_revenue - total_paid
    return total_revenue, total_paid, outstanding