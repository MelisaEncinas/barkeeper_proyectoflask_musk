from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import RegistrationForm, LoginForm, ContactForm, CocktailForm, SimpleForm
from app.models import User
from recommender.cocktailRecommender import CocktailRecommender
import json

# Crear una instancia del recomendador
recommender = CocktailRecommender(
    cocktail_file='data/ccc_cocktails.xml',
    taxonomy_file='data/taxonomy_taste.csv',
    general_taxonomy_file='data/general_taxonomy.csv'
)

@app.route('/')
def index():
    return render_template('home.html', title='Inicio')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # Redirige a la página principal si ya está autenticado
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('¡Has iniciado sesión con éxito!', 'success')
            return redirect(url_for('home'))  # Redirige después del inicio de sesión exitoso
        else:
            flash('Email o contraseña incorrectos.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/registrarse', methods=['GET', 'POST'])
def registrarse():
    if current_user.is_authenticated:
        return redirect(url_for('iniciar_sesion'))  # Redirige a iniciar sesión si ya está autenticado
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.nombre.data, email=form.email.data)
        user.set_password(password=form.contrasena.data)
        db.session.add(user)
        db.session.commit()
        flash('Registro exitoso. Por favor, inicie sesión.', 'success')
        return redirect(url_for('iniciar_sesion'))
    
    return render_template('registro.html', form=form)

@app.route('/contact', methods=['GET', 'POST'])
def contacto():
    form = ContactForm()
    if form.validate_on_submit():
        flash('Mensaje enviado exitosamente', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/cocktails')
@login_required
def cocktails():
    try:
        with open('data/cocktails.json', 'r') as f:
            cocktails_data = json.load(f)
        return render_template('cocktails.html', cocktails=cocktails_data)
    except FileNotFoundError:
        flash('El archivo de cócteles no se encontró.', 'danger')
        return redirect(url_for('index'))

@app.route('/cocktail/<cocktail_name>')
def cocktail_detail(cocktail_name):
    try:
        with open('data/cocktails.json') as f:
            cocktails = json.load(f)
        cocktail = next((c for c in cocktails if c['nombre'] == cocktail_name), None)
        if cocktail:
            return render_template('cocktail_detail.html', cocktail=cocktail)
        else:
            flash('Cóctel no encontrado.', 'danger')
            return redirect(url_for('cocktails'))
    except FileNotFoundError:
        flash('El archivo de cócteles no se encontró.', 'danger')
        return redirect(url_for('index'))

@app.route('/cocktails/search')
def search_cocktails():
    ingrediente = request.args.get('ingrediente', '')
    try:
        with open('data/cocktails.json') as f:
            cocktails = json.load(f)
        resultados = [c for c in cocktails if ingrediente.lower() in (i.lower() for i in c['ingredientes'])]
        return jsonify(resultados)
    except FileNotFoundError:
        return jsonify([])

@app.route('/cerrar_sesion')
def cerrar_sesion():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('index'))
