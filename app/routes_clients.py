from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from .models import Client, Invoice, Payment # <-- Ensure all models are imported
from . import db
from .utils import owner_required
from datetime import datetime
from decimal import Decimal # Import Decimal for safe rounding if needed, although float is used below

clients_bp = Blueprint('clients', __name__)

# --- Helper Functions for JSON Serialization (ROBUST VERSION) ---

def serialize_invoice(inv):
    """Helper to serialize a single Invoice object (Robust Version)."""
    
    # Safely format date
    due_date_str = inv.due_date.strftime('%Y-%m-%d') if inv.due_date else 'N/A'
    
    # Safely access the property (using getattr as a defense, though direct access is intended)
    # The property itself is defined in models.py to handle division by zero.
    installment_amount_val = getattr(inv, 'installment_amount', 0.0) 
    
    return {
        "id": inv.id,
        "invoice_no": inv.invoice_no or 'N/A',
        "description": inv.description or 'No Description',
        "amount": inv.amount or 0.0,
        "paid": inv.paid or 0.0,
        "status": inv.status or 'pending',
        "due_date": due_date_str,
        "payment_type": inv.payment_type or 'Full Payment',
        "installments": inv.installments or 1,
        "installment_amount": installment_amount_val,
        # Get remaining balance for display
        "remaining_amount": inv.remaining_amount
    }

def serialize_payment(pay):
    """Helper to serialize a single Payment object (Robust Version)."""
    
    # Safely format date
    date_str = pay.date.strftime('%Y-%m-%d') if pay.date else 'N/A'
    
    # Safely get the related invoice number
    invoice_no = pay.invoice.invoice_no if pay.invoice and pay.invoice.invoice_no else 'N/A'
    
    return {
        "id": pay.id,
        "amount": pay.amount or 0.0,
        "method": pay.method or 'N/A',
        "date": date_str,
        "invoice_no": invoice_no,
        "installment_number": pay.installment_number if pay.installment_number is not None else 'N/A'
    }

# --- End Helper Functions ---


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
        c.total_invoiced = sum((inv.amount or 0) for inv in c.invoices)
        c.total_paid = sum((inv.paid or 0) for inv in c.invoices)

    return render_template('clients.html', clients=clients)


@clients_bp.route('/clients/json')
@login_required
@owner_required
def clients_json():
    """Returns a list of all clients as JSON for the owner's 'Switch Client' modal."""
    clients = Client.query.all()
    data = [
        {"id": c.id, "name": c.name, "email": c.email or '', "company": c.company or ''}
        for c in clients
    ]
    return jsonify(data)


@clients_bp.route('/clients/add', methods=['POST'])
@login_required
@owner_required
def add_client():
    """Add new client (Owner only)"""
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    company = request.form.get('company')
    tax_id = request.form.get('tax_id')
    address = request.form.get('address')
    
    if Client.query.filter_by(email=email).first():
        flash('A client with this email already exists.', 'warning')
        return redirect(url_for('clients.clients_list'))

    client = Client(
        name=name, email=email, phone=phone, 
        company=company, tax_id=tax_id, address=address
    )
    db.session.add(client)
    db.session.commit()
    flash('Client added.', 'success')
    return redirect(url_for('clients.clients_list'))


@clients_bp.route('/clients/edit/<int:id>', methods=['POST'])
@login_required
@owner_required
def edit_client(id):
    """Edit existing client (Owner only)"""
    client = Client.query.get_or_404(id)
    
    client.name = request.form.get('name')
    client.email = request.form.get('email')
    client.phone = request.form.get('phone')
    client.company = request.form.get('company')
    client.tax_id = request.form.get('tax_id')
    client.address = request.form.get('address')
    
    # Simple check for existing email (excluding the current client)
    if Client.query.filter(Client.email == client.email, Client.id != id).first():
        flash('A client with this email already exists.', 'warning')
        return redirect(url_for('clients.clients_list'))

    db.session.commit()
    flash('Client updated.', 'success')
    return redirect(url_for('clients.clients_list'))


@clients_bp.route('/clients/delete/<int:id>', methods=['POST'])
@login_required
@owner_required
def delete_client(id):
    """Delete client (Owner only)"""
    client = Client.query.get_or_404(id)
    
    # In a real application, you would need to handle (delete or reassign) 
    # all associated Invoices and Payments before deleting the client.
    
    db.session.delete(client)
    db.session.commit()
    flash('Client deleted.', 'danger')
    return redirect(url_for('clients.clients_list'))


# routes_clients.py

@clients_bp.route('/client/<int:id>/details')
@login_required
def client_details(id):
    """Fetch client details, ALL invoices, and ALL payments (for modal view)"""
    client = Client.query.get_or_404(id)
    
    # SECURITY CHECK: A client user should only be able to view their OWN details
    if current_user.role == 'client':
        effective_client = Client.query.filter_by(email=current_user.username).first()
        if not effective_client or effective_client.id != client.id:
            abort(403)
            
    # Fetch ALL data needed for the detailed profile modal
    # Use Invoice.id.desc() for consistent sorting when date is the same
    # ******************************************************************************************
    # FIX: Change Invoice.date to Invoice.due_date
    all_invoices = Invoice.query.filter_by(client_id=id).order_by(Invoice.due_date.desc(), Invoice.id.desc()).all()
    # ******************************************************************************************
    
    # Fetch ALL payments associated with this client's invoices
    all_payments = Payment.query.join(Invoice).filter(
        Invoice.client_id == client.id
    ).order_by(Payment.date.desc()).all()


    total_invoiced = sum((inv.amount or 0) for inv in all_invoices)
    # ... rest of the function ...
    total_paid = sum((inv.paid or 0) for inv in all_invoices)
    outstanding = total_invoiced - total_paid

    # Return data as JSON response
    return jsonify({
        "id": client.id,
        "name": client.name or "N/A",
        "company": client.company or "N/A",
        "email": client.email or "N/A",
        "phone": client.phone or "N/A",
        "tax_id": client.tax_id or "N/A",
        "address": client.address or "N/A",
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "outstanding": outstanding,
        "invoice_count": len(all_invoices),
        
        # New serialized lists for the modal tabs
        "all_invoices": [serialize_invoice(inv) for inv in all_invoices],
        "all_payments": [serialize_payment(pay) for pay in all_payments]
    })
