from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from .models import Invoice, Client
from . import db
from .utils import owner_required
from datetime import datetime

invoices_bp = Blueprint('invoices', __name__)

@invoices_bp.route('/invoices')
@login_required
def invoices_list():
    if current_user.role == 'owner':
        invoices = Invoice.query.all()
        clients = Client.query.all()
    else:
        client_rec = Client.query.filter_by(email=current_user.username).first()
        invoices = Invoice.query.filter_by(client_id=client_rec.id).all() if client_rec else []
        clients = []
    return render_template('invoices.html', invoices=invoices, clients=clients)

@invoices_bp.route('/invoices/add', methods=['POST'])
@login_required
@owner_required
def add_invoice():
    invoice_no = request.form.get('invoice_no')
    client_id = int(request.form.get('client_id'))
    description = request.form.get('description')
    amount = float(request.form.get('amount') or 0)
    payment_type = request.form.get('payment_type')
    # Normalize incoming values from the form (radio values can be 'full'/'installment')
    if payment_type:
        pt = payment_type.strip().lower()
        if pt.startswith('install'):
            payment_type = 'Installment'
        else:
            payment_type = 'Full Payment'
    else:
        payment_type = 'Full Payment'

    # Read optional installment fields when an installment plan is selected
    installments = 1
    frequency = 'monthly'
    if payment_type == 'Installment':
        try:
            installments = int(request.form.get('installments') or 1)
        except Exception:
            installments = 1
        frequency = request.form.get('frequency') or 'monthly'
    due_date = request.form.get('due_date')
    due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None

    inv = Invoice(
        invoice_no=invoice_no, client_id=client_id, description=description,
        amount=amount, payment_type=payment_type, due_date=due_date_obj,
        status='pending', installments=installments, frequency=frequency
    )
    db.session.add(inv)
    db.session.commit()
    flash('Invoice created.', 'success')
    return redirect(url_for('invoices.invoices_list'))

@invoices_bp.route('/invoices/delete/<int:id>', methods=['POST'])
@login_required
@owner_required
def delete_invoice(id):
    inv = Invoice.query.get_or_404(id)
    db.session.delete(inv)
    db.session.commit()
    flash('Invoice deleted.', 'danger')
    return redirect(url_for('invoices.invoices_list'))

@invoices_bp.route('/invoices/mark_paid/<int:id>', methods=['POST'])
@login_required
@owner_required
def mark_invoice_paid(id):
    inv = Invoice.query.get_or_404(id)
    inv.paid = inv.amount
    inv.status = 'paid'
    db.session.commit()
    flash('Invoice marked as paid.', 'success')
    return redirect(url_for('invoices.invoices_list'))