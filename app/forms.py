# app/forms.py
from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, PasswordField, FloatField, SelectField, DateField, SubmitField, TextAreaField, IntegerField # type: ignore
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional # type: ignore
from .models import Client # Import Client model to check for uniqueness

# --- Helper Validators ---
class UniqueUsername:
    """Validator to ensure the username/email is unique."""
    def __init__(self, message=None):
        if not message:
            message = 'This username/email is already in use.'
        self.message = message

    def __call__(self, form, field):
        if Client.query.filter_by(email=field.data).first():
            raise ValueError(self.message)
            
# --- Forms ---

class LoginForm(FlaskForm):
    username = StringField('Username (Email)', validators=[DataRequired(), Length(min=3, max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    # Note: Using 'username' field to capture the user's Full Name
    username = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')
    ])
    role = SelectField('Role', choices=[('client', 'Client'), ('owner', 'Owner')], validators=[DataRequired()])
    submit = SubmitField('Register')

class ClientForm(FlaskForm):
    """
    Form for adding/editing a Client profile.
    Updated to include all fields defined in the Client model.
    """
    name = StringField('Client Name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    company = StringField('Company Name', validators=[Optional(), Length(max=120)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=50)])
    tax_id = StringField('Tax ID / TIN', validators=[Optional(), Length(max=50)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=250)])
    submit = SubmitField('Save Client')

class InvoiceForm(FlaskForm):
    """
    Form for creating a new Invoice.
    Updated to handle Installment plans (installments & frequency).
    """
    # The client_id dropdown will be populated dynamically in the route (routes_invoices.py)
    client_id = SelectField('Client', coerce=int, validators=[DataRequired()])
    
    # Invoice details
    invoice_no = StringField('Invoice #', validators=[DataRequired(), Length(max=50)])
    description = StringField('Description / Service Provided', validators=[DataRequired(), Length(max=250)])
    amount = FloatField('Total Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    
    # Payment type selection (radio buttons in HTML, but defined here for logic/data)
    payment_type = SelectField('Payment Type', choices=[
        ('Full Payment', 'Full Payment'), 
        ('Installment', 'Installment')
    ], validators=[DataRequired()])
    
    # Installment fields (Optional)
    installments = IntegerField('Number of Installments', validators=[Optional(), NumberRange(min=1)], default=1)
    frequency = SelectField('Installment Frequency', choices=[
        ('monthly', 'Monthly'),
        ('biweekly', 'Bi-Weekly'),
        ('weekly', 'Weekly')
    ], validators=[Optional()])

    submit = SubmitField('Create Invoice')

class PaymentForm(FlaskForm):
    """Form for recording a payment."""
    # This must be populated in the route with only outstanding invoices
    invoice_id = SelectField('Invoice', coerce=int, validators=[DataRequired()])
    amount = FloatField('Amount Paid', validators=[DataRequired(), NumberRange(min=0.01)])
    method = SelectField('Payment Method', choices=[
        ('Cash', 'Cash'), 
        ('Bank Transfer', 'Bank Transfer'), 
        ('Credit Card', 'Credit Card'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    date = DateField('Payment Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Record Payment')
