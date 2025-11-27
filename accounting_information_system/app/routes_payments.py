from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from .models import Payment, Invoice, Client
from . import db
from .utils import owner_required
from datetime import datetime

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/payments')
@login_required
def payments_list():
    if current_user.role == 'owner':
        payments = Payment.query.order_by(Payment.date.desc()).all()
        invoices = Invoice.query.all()
    else:
        client_rec = Client.query.filter_by(email=current_user.username).first()
        # payments for this client's invoices
        payments = Payment.query.join(Invoice).filter(Invoice.client_id == (client_rec.id if client_rec else None)).order_by(Payment.date.desc()).all()
        invoices = []
    return render_template('payments.html', payments=payments, invoices=invoices, now=datetime.utcnow().date())

@payments_bp.route('/payments/add', methods=['POST'])
@login_required
@owner_required
def add_payment():
    invoice_id = int(request.form.get('invoice_id'))
    amount = float(request.form.get('amount') or 0)
    method = request.form.get('method')
    date_str = request.form.get('date')  # optional
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()

    invoice = Invoice.query.get_or_404(invoice_id)
    payment = Payment(invoice_id=invoice_id, amount=amount, method=method, date=date_obj)
    db.session.add(payment)

    # Update invoice paid amount
    invoice.paid = (invoice.paid or 0) + amount

    # If the invoice is an installment plan, compute per-installment amount and
    # backfill installment numbers for all payments in chronological order.
    if invoice.payment_type and invoice.payment_type.lower().startswith('install'):
        try:
            per_inst = float(invoice.installment_amount or 0)
        except Exception:
            per_inst = 0.0

        if per_inst > 0:
            # Retrieve payments ordered by date then id to have stable ordering
            payments = Payment.query.filter_by(invoice_id=invoice.id).order_by(Payment.date, Payment.id).all()
            running = 0.0
            try:
                from math import ceil
                max_inst = int(invoice.installments or 0)
            except Exception:
                max_inst = 0

            for p in payments:
                running += (p.amount or 0)
                inst_num = int(max(1, min(max_inst, int(ceil(running / per_inst))))) if max_inst else int(ceil(running / per_inst))
                p.installment_number = inst_num
    if invoice.paid >= invoice.amount:
        invoice.status = 'paid'
    else:
        invoice.status = 'partial'

    db.session.commit()
    flash('Payment recorded.', 'success')
    return redirect(url_for('payments.payments_list'))

@payments_bp.route('/payments/delete/<int:id>', methods=['POST'])
@login_required
@owner_required
def delete_payment(id):
    pay = Payment.query.get_or_404(id)
    invoice = pay.invoice
    invoice.paid = max((invoice.paid or 0) - (pay.amount or 0), 0)
    if invoice.paid <= 0:
        invoice.status = 'pending'
    elif invoice.paid < invoice.amount:
        invoice.status = 'partial'
    db.session.delete(pay)
    db.session.commit()
    flash('Payment deleted.', 'danger')
    return redirect(url_for('payments.payments_list'))
