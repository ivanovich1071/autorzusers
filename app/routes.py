from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateProfileForm
from app.models import User

# Создание Blueprint
routes = Blueprint('routes', __name__)

@routes.route("/")
@routes.route("/home")
def home():
    return render_template('base.html')

@routes.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Ваш аккаунт был создан! Вы теперь можете войти в систему.', 'success')
        return redirect(url_for('routes.login'))
    return render_template('register.html', title='Регистрация', form=form)

@routes.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            flash('Вы успешно вошли в систему.', 'success')
            return redirect(url_for('routes.home'))
        else:
            flash('Вход не удался. Пожалуйста, проверьте почту и пароль.', 'danger')
    return render_template('login.html', title='Вход', form=form)

@routes.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('routes.home'))

@routes.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password
        db.session.commit()
        flash('Ваш профиль был обновлен!', 'success')
        return redirect(url_for('routes.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('profile.html', title='Профиль', form=form)

@routes.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        print("Форма валидна, данные обновляются...")  # Отладочное сообщение
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password
        try:
            db.session.commit()
            flash('Ваш профиль был обновлен!', 'success')
            print("Профиль обновлен успешно!")  # Отладочное сообщение
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при обновлении профиля.', 'danger')
            print(f"Ошибка при обновлении профиля: {str(e)}")  # Отладочное сообщение
        return redirect(url_for('routes.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        print("Загрузка профиля пользователя...")  # Отладочное сообщение
    return render_template('edit_profile.html', title='Редактировать Профиль', form=form)

