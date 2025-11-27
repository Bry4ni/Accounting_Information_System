from flask import Blueprint, render_template, session, current_app, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from .models import Client, Invoice, Payment
from . import db
from .utils import owner_required
from datetime import datetime

portal_bp = Blueprint('portal', __name__)


def get_effective_client():
    # If owner impersonating a client via session
    imp = session.get('impersonate_client_id')
    if imp and current_user.is_authenticated and current_user.role == 'owner':
        return Client.query.get(imp)

    # If logged-in client user, match by username (email)
    if current_user.is_authenticated and current_user.role == 'client':
        return Client.query.filter_by(email=current_user.username).first()

    return None


@portal_bp.route('/portal')
@login_required
def portal_dashboard():
    client = get_effective_client()
    if not client:
        abort(403)

    invoices = Invoice.query.filter_by(client_id=client.id).all()
    payments = Payment.query.join(Invoice).filter(Invoice.client_id == client.id).order_by(Payment.date.desc()).all()
    return render_template('portal/dashboard.html', client=client, invoices=invoices, payments=payments)


@portal_bp.route('/portal/invoices')
@login_required
def portal_invoices():
    client = get_effective_client()
    if not client:
        abort(403)
    invoices = Invoice.query.filter_by(client_id=client.id).all()
    return render_template('portal/invoices.html', client=client, invoices=invoices)


@portal_bp.route('/portal/invoices/<int:id>')
@login_required
def portal_invoice_detail(id):
    client = get_effective_client()
    if not client:
        abort(403)
    inv = Invoice.query.get_or_404(id)
    if inv.client_id != client.id:
        abort(403)
    return render_template('portal/invoice_detail.html', client=client, invoice=inv)


@portal_bp.route('/portal/payments/add', methods=['POST'])
@login_required
def portal_add_payment():
    client = get_effective_client()
    if not client:
        abort(403)

    invoice_id = int(request.form.get('invoice_id'))
    amount = float(request.form.get('amount') or 0)
    method = request.form.get('method')
    date_str = request.form.get('date')
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()

    invoice = Invoice.query.get_or_404(invoice_id)
    if invoice.client_id != client.id:
        abort(403)

    # reuse the payments logic but ensure client-scope
    payment = Payment(invoice_id=invoice_id, amount=amount, method=method, date=date_obj)
    db.session.add(payment)

    invoice.paid = (invoice.paid or 0) + amount
    if invoice.paid >= invoice.amount:
        invoice.status = 'paid'
    else:
        invoice.status = 'partial'

    # backfill installment numbers if installment plan
    if invoice.payment_type and invoice.payment_type.lower().startswith('install'):
        try:
            per_inst = float(invoice.installment_amount or 0)
        except Exception:
            per_inst = 0.0

        if per_inst > 0:
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

    db.session.commit()
    flash('Payment recorded.', 'success')
    return redirect(url_for('portal.portal_invoice_detail', id=invoice.id))


@portal_bp.route('/portal/payments')
@login_required
def portal_payments():
    client = get_effective_client()
    if not client:
        abort(403)
    payments = Payment.query.join(Invoice).filter(Invoice.client_id == client.id).order_by(Payment.date.desc()).all()
    return render_template('portal/payments.html', client=client, payments=payments)