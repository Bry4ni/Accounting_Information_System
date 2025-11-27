from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date, timedelta
from .models import Invoice, Payment, Client
from .utils import calculate_totals

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'owner':
        invoices = Invoice.query.all()
        payments = Payment.query.order_by(Payment.date.desc()).all()
        clients = Client.query.all()
    else:
        client_rec = Client.query.filter_by(email=current_user.username).first()
        invoices = Invoice.query.filter_by(client_id=client_rec.id).all() if client_rec else []
        payments = Payment.query.join(Invoice).filter(
            Invoice.client_id == (client_rec.id if client_rec else None)
        ).all()
        clients = [client_rec] if client_rec else []

    # Totals
    total_revenue, total_paid, outstanding = calculate_totals(invoices)

    # Overdue invoices
    overdue_invoices = [
        inv for inv in invoices
        if inv.status != 'paid' and inv.due_date and inv.due_date < date.today()
    ]

    # Installment invoices
    installment_invoices = [inv for inv in invoices if inv.payment_type and inv.payment_type.lower().startswith('install')]

    # ✅ Pre-compute progress_percent for each installment invoice
    for inv in installment_invoices:
        if inv.installments and inv.installments > 0:
            inv.progress_percent = (inv.installments_paid() / inv.installments) * 100
        else:
            inv.progress_percent = 0

    # Recent payments
    recent_payments = payments[:5]

    return render_template(
        'dashboard.html',
        total_revenue=total_revenue,
        total_paid=total_paid,
        outstanding=outstanding,
        clients_count=len(clients),
        invoices=invoices,
        payments=payments,
        overdue_invoices=overdue_invoices,
        installment_invoices=installment_invoices,
        recent_payments=recent_payments
    )
