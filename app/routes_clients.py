from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from .models import Client, Invoice
from . import db
from .utils import owner_required

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/clients')
@login_required
def clients_list():
    """
    Owner: view all clients
    Client: view only their record
    Adds total_invoiced and total_paid per client
    """
    if current_user.role == 'owner':
        clients = Client.query.all()
    else:
        clients = Client.query.filter_by(email=current_user.username).all()

    # Compute totals for each client for the dashboard/modal
    for c in clients:
        c.total_invoiced = sum(inv.amount for inv in c.invoices)
        c.total_paid = sum((inv.paid or 0) for inv in c.invoices)

    return render_template('clients.html', clients=clients)


@clients_bp.route('/clients/json')
@login_required
@owner_required
def clients_json():
    clients = Client.query.all()
    data = [
        {"id": c.id, "name": c.name, "email": c.email or '', "company": c.company or ''}
        for c in clients
    ]
    from flask import jsonify
    return jsonify(data)

@clients_bp.route('/clients/add', methods=['POST'])
@login_required
@owner_required
def add_client():
    """Add new client (Owner only)"""
    name = request.form.get('name')
    email = request.form.get('email')
    company = request.form.get('company')
    phone = request.form.get('phone')
    tax_id = request.form.get('tax_id')
    address = request.form.get('address')

    if not name:
        flash('Client name is required.', 'danger')
        return redirect(url_for('clients.clients_list'))

    new_client = Client(
        name=name,
        email=email,
        company=company,
        phone=phone,
        tax_id=tax_id,
        address=address
    )
    db.session.add(new_client)
    db.session.commit()
    flash('Client added successfully!', 'success')
    return redirect(url_for('clients.clients_list'))

@clients_bp.route('/clients/edit/<int:id>', methods=['POST'])
@login_required
@owner_required
def edit_client(id):
    """Edit existing client (Owner only)"""
    client = Client.query.get_or_404(id)
    client.name = request.form.get('name')
    client.email = request.form.get('email')
    client.company = request.form.get('company')
    client.phone = request.form.get('phone')
    client.tax_id = request.form.get('tax_id')
    client.address = request.form.get('address')
    db.session.commit()
    flash('Client updated.', 'info')
    return redirect(url_for('clients.clients_list'))

@clients_bp.route('/clients/delete/<int:id>', methods=['POST'])
@login_required
@owner_required
def delete_client(id):
    """Delete client (Owner only)"""
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    flash('Client deleted.', 'danger')
    return redirect(url_for('clients.clients_list'))

@clients_bp.route('/client/<int:id>/details')
@login_required
def client_details(id):
    """Fetch client details and recent invoices (for modal view)"""
    client = Client.query.get_or_404(id)
    invoices = Invoice.query.filter_by(client_id=id).order_by(Invoice.due_date.desc()).limit(5).all()

    total_invoiced = sum(inv.amount for inv in invoices)
    total_paid = sum((inv.paid or 0) for inv in invoices)
    outstanding = total_invoiced - total_paid

    return {
        "name": client.name or "N/A",
        "company": client.company or "N/A",
        "email": client.email or "N/A",
        "phone": client.phone or "N/A",
        "tax_id": client.tax_id or "N/A",
        "address": client.address or "N/A",
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "outstanding": outstanding,
        "invoice_count": len(invoices),
        "recent_invoices": [
            {
                "invoice_no": inv.invoice_no,
                "description": inv.description or "No description",
                "amount": inv.amount,
                "status": inv.status
            } for inv in invoices
        ]
    }