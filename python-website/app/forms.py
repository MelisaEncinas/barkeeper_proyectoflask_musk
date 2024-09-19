# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class SimpleForm(FlaskForm):
    field1 = StringField('Field 1', validators=[DataRequired()])
    field2 = StringField('Field 2', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'placeholder': 'email'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'password'})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    contrasena = PasswordField('Contraseña', validators=[DataRequired()])
    contrasena2 = PasswordField('Repetir Contraseña', validators=[DataRequired(), EqualTo('contrasena')])
    direccion = StringField('Dirección', validators=[DataRequired()])
    ciudad = StringField('Ciudad', validators=[DataRequired()])
    pais = StringField('País', validators=[DataRequired()])
    dni = StringField('DNI', validators=[DataRequired()])
    celular = StringField('Celular', validators=[DataRequired()])
    submit = SubmitField('Registrarse')

class ContactForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    phone = StringField('Teléfono', validators=[DataRequired()])
    message = TextAreaField('Mensaje', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Enviar Mensaje')
    
class CocktailForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    ingredients = TextAreaField('Ingredientes', validators=[DataRequired()])
    preparation = TextAreaField('Preparación', validators=[DataRequired()])
    image_url = StringField('URL de la Imagen')
    category = StringField('Categoría')
    submit = SubmitField('Guardar Cóctel')
