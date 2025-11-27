# OPTIONAL: run to populate sample data
from app import create_app, db
from app.models import User, Client, Invoice, Payment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()

    owner = User(username='admin@accounting.com', role='owner')
    owner.set_password('admin123')

    client_user = User(username='client1@example.com', role='client')
    client_user.set_password('clientpass')

    db.session.add_all([owner, client_user])
    db.session.commit()

    client1 = Client(
        name='Alice Johnson',
        email='client1@example.com',
        company='AJ Trading',
        phone='09171234567',
        tax_id='TX123456',
        address='Makati City'
    )
    client2 = Client(
        name='Bob Reyes',
        email='bob.reyes@business.com',
        company='Reyes Supplies',
        phone='09987654321',
        tax_id='TX654321',
        address='Quezon City'
    )
    db.session.add_all([client1, client2])
    db.session.commit()

    inv1 = Invoice(
        invoice_no='INV-001',
        client_id=client1.id,
        description='Website Development',
        amount=50000.00,
        payment_type='Installment',
        paid=20000.00,
        due_date=(datetime.utcnow() + timedelta(days=15)).date(),
        status='partial'
    )
    inv2 = Invoice(
        invoice_no='INV-002',
        client_id=client1.id,
        description='Maintenance Fee',
        amount=10000.00,
        payment_type='Full Payment',
        paid=10000.00,
        due_date=(datetime.utcnow() - timedelta(days=5)).date(),
        status='paid'
    )
    inv3 = Invoice(
        invoice_no='INV-003',
        client_id=client2.id,
        description='Software License',
        amount=30000.00,
        payment_type='Full Payment',
        paid=0.0,
        due_date=(datetime.utcnow() + timedelta(days=30)).date(),
        status='pending'
    )
    db.session.add_all([inv1, inv2, inv3])
    db.session.commit()

    pay1 = Payment(invoice_id=inv1.id, amount=20000.00, method='Bank Transfer', date=(datetime.utcnow() - timedelta(days=2)).date())
    pay2 = Payment(invoice_id=inv2.id, amount=10000.00, method='Cash', date=(datetime.utcnow() - timedelta(days=10)).date())
    db.session.add_all([pay1, pay2])
    db.session.commit()

    print("Seed complete. Admin: admin@accounting.com/admin123 | Client: client1@example.com/clientpass")