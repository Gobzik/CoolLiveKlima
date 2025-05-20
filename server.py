import os
import base64 as b

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, flash, url_for, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from bytes import image_to_bytes
from data import db_session
from data.orders import Order
from data.users import User
from forms.order import RegisterOrder
from forms.user import RegisterForm, LoginForm
from load_prices import load_prices

load_dotenv()

db_session.global_init('database/CoolLiveKlima.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', '98322e62bcc47477d8bba4ee54e30ac04890beeccef5725a33941a08d7eb0cb3')
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}
c = b.b64decode
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

login_manager = LoginManager()
login_manager.init_app(app)


@app.template_filter('b64encode')
def b64encode_filter(data):
    if data:
        return b.b64encode(data).decode('utf-8')
    return ''


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, int(user_id))


@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File size is too large. Please upload a smaller file.', 'error')
    return redirect(url_for('installation_request'))


@app.route('/')
@app.route('/index')
def index():
    param = {
        'title': 'CoolLiveKlima'}
    return render_template('index.html', **param)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="Passwords incorrect")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message='We have that user')
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            address=form.address.data,
            phone_number=form.phone_number.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Register', form=form,
                           yandex_maps_api_key=os.getenv('YANDEX_MAPS_API_KEY'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message='Неправильный логин или пароль',
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/install', methods=['GET', 'POST'])
def installation_request():
    form = RegisterOrder()

    if request.method == 'POST':
        image = None

        if not form.validate():
            return render_template('order.html', title='Installation', form=form,
                                   yandex_maps_api_key=os.getenv('YANDEX_MAPS_API_KEY'))

        try:
            db_sess = db_session.create_session()

            if form.photo.data:
                image = image_to_bytes(form.photo.data)

            order = Order(
                user_name=form.name.data,
                user_surname=form.surname.data,
                phone_number=form.phone_number.data,
                description=form.description.data,
                address=form.address.data,
                picture=image,
                user_id=current_user.get_id()
            )
            db_sess.add(order)
            db_sess.commit()

            flash('Данные успешно получены!', 'success')
            return render_template('index.html')

        except Exception:
            flash('Ошибка обработки данных', 'error')

    return render_template('order.html', title='Installation', form=form,
                           yandex_maps_api_key=os.getenv('YANDEX_MAPS_API_KEY'))


@app.route('/user_account')
@login_required
def user_account():
    db_sess = db_session.create_session()
    orders = db_sess.query(Order).filter(Order.user_id == current_user.get_id())
    return render_template("user_account.html", orders=orders)


@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    prices_data = load_prices()

    prices = {
        'route': prices_data['route_price'],
        'groove': prices_data['groove_price'],
        'ac': {
            'standard': prices_data['ac_standard'],
            'inverter': prices_data['ac_inverter'],
            'premium': prices_data['ac_premium']
        },
        'extra_mounting': prices_data['extra_mounting_percent'],
        'warranty': prices_data['warranty_percent']
    }

    if request.method == 'POST':
        try:
            route_length = float(request.form.get('route_length', 0))
            groove_length = float(request.form.get('groove_length', 0))
            ac_count = int(request.form.get('ac_count', 1))
            ac_type = request.form.get('ac_type', 'standard')
            extra_mounting = 'extra_mounting' in request.form
            warranty = 'warranty' in request.form

            if route_length < 0 or groove_length < 0 or ac_count < 1:
                raise ValueError('Некорректные значения')

            if ac_type not in prices['ac']:
                raise ValueError('Неизвестный тип кондиционера')

            base_ac_cost = prices['ac'][ac_type] * ac_count
            route_cost = prices['route'] * route_length
            groove_cost = prices['groove'] * groove_length

            extra_cost = 0
            if extra_mounting:
                extra_cost += base_ac_cost * prices['extra_mounting']
            if warranty:
                extra_cost += base_ac_cost * prices['warranty']

            total_cost = base_ac_cost + route_cost + groove_cost + extra_cost

            return render_template('calculator.html',
                                   calculation={
                                       'base_cost': base_ac_cost,
                                       'route_cost': route_cost,
                                       'groove_cost': groove_cost,
                                       'extra_cost': extra_cost,
                                       'ac_count': ac_count,
                                       'total_cost': total_cost
                                   },
                                   prices=prices)

        except Exception as e:
            flash(str(e), 'error')
            return render_template('calculator.html', prices=prices)

    return render_template('calculator.html', prices=prices)


@app.route('/about_us')
def about_us():
    return render_template('about_us.html')


@app.route('/admin_orders')
@login_required
def _():
    if not getattr(current_user, c(b.b64encode(b'admin')).decode()):
        return abort(403)
    d = getattr(db_session, c(b'Y3JlYXRlX3Nlc3Npb24=').decode())()
    q = getattr(d, c(b'cXVlcnk=').decode())(Order)
    return render_template(c(b'YWRtaW4uaHRtbA==').decode(), orders=q)


@app.route('/change_status/<int:order_id>', methods=['POST'])
@login_required
def change_status(order_id):
    db_sess = db_session.create_session()
    if not current_user.admin:
        abort(403)
    order = db_sess.query(Order).get(order_id)
    if order:
        order.is_ready = not order.is_ready
        db_sess.commit()
    return redirect(request.referrer or url_for('admin_orders'))


@app.route('/delete_order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    if current_user.id not in [1, 2]:
        abort(403)
    session = db_session.create_session()
    order = session.query(Order).get(order_id)
    if order:
        session.delete(order)
        session.commit()
    return redirect(request.referrer or url_for('admin_orders'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
