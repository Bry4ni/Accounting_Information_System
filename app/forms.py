# app/forms.py
from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, PasswordField, FloatField, SelectField, DateField, SubmitField # type: ignore
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange # type: ignore

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')
    ])
    role = SelectField('Role', choices=[('client', 'Client'), ('owner', 'Owner')], validators=[DataRequired()])
    submit = SubmitField('Register')

class ClientForm(FlaskForm):
    name = StringField('Client Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Length(max=20)])
    submit = SubmitField('Save Client')

class InvoiceForm(FlaskForm):
    invoice_no = StringField('Invoice #', validators=[DataRequired()])
    description = StringField('Description')
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    due_date = DateField('Due Date', validators=[DataRequired()])
    payment_type = SelectField('Payment Type', choices=[('Full Payment', 'Full Payment'), ('Installment', 'Installment')])
    submit = SubmitField('Create Invoice')

class PaymentForm(FlaskForm):
    invoice_id = SelectField('Invoice', coerce=int, validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    method = SelectField('Payment Method', choices=[
        ('Cash', 'Cash'), ('Bank Transfer', 'Bank Transfer'), ('Credit Card', 'Credit Card')
    ])
    submit = SubmitField('Record Payment')