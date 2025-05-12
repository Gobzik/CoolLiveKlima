import base64
import os

import pandas as pd
from flask import Flask, render_template, redirect, flash, url_for, request, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api

from bytes import image_to_bytes

from data import db_session, orders_resources
from data.orders import Order
from forms.order import RegisterOrder
from forms.user import RegisterForm, LoginForm
from data.users import User

db_session.global_init("database/CoolLiveKlima.db")

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'super_secret_key_otvetov_net'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
app.config['PER_PAGE'] = 5
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

api.add_resource(orders_resources.OrdersListResource, '/api/orders')
api.add_resource(orders_resources.OrderResource, '/api/order/<int:order_id>')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
PRICES_FILE = 'prices.xlsx'

login_manager = LoginManager()
login_manager.init_app(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.template_filter('b64encode')
def b64encode_filter(data):
    if data:
        return base64.b64encode(data).decode('utf-8')
    return None


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
                                   message="We have that user")
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
    return render_template('register.html', title='Register', form=form, yandex_maps_api_key='5ea5f410-6745-408e-be04-5ccd1a9bca7e')


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
                               message="Неправильный логин или пароль",
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
        print("Форма получена! Данные:", request.form)
        print("Файлы:", request.files)
        image = None

        if not form.validate():
            print("Ошибки валидации:", form.errors)
            return render_template('order.html', title='Installation', form=form, yandex_maps_api_key='5ea5f410-6745-408e-be04-5ccd1a9bca7e')

        try:
            db_sess = db_session.create_session()
            print("Данные формы:", form.data)

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
            print(image)

            flash('Данные успешно получены!', 'success')
            return render_template('index.html')

        except Exception as e:
            print("Ошибка обработки:", str(e))
            flash('Ошибка обработки данных', 'error')

    return render_template('order.html', title='Installation', form=form, yandex_maps_api_key='5ea5f410-6745-408e-be04-5ccd1a9bca7e')


@app.route('/user_account')
@login_required
def user_account():
    db_sess = db_session.create_session()
    orders = db_sess.query(Order).filter(Order.user_id == current_user.get_id())
    return render_template("user_account.html", orders=orders)


DEFAULT_PRICES = {
    'route_price': 500,       # цена за метр трассы
    'groove_price': 300,      # цена за метр штробы
    'ac_standard': 15000,     # стандартный кондиционер
    'ac_inverter': 20000,     # инверторный кондиционер
    'ac_premium': 25000,      # премиум кондиционер
    'extra_mounting': 0.2,    # 20% за сложный монтаж
    'warranty': 0.15          # 15% за гарантию
}


def load_prices():
    try:
        if not os.path.exists(PRICES_FILE):
            return DEFAULT_PRICES

        prices_df = pd.read_excel(PRICES_FILE, engine='openpyxl')
        prices_dict = prices_df.set_index('Название')['Цена'].to_dict()

        return {
            'route_price': float(prices_dict.get('route_price', DEFAULT_PRICES['route_price'])),
            'groove_price': float(prices_dict.get('groove_price', DEFAULT_PRICES['groove_price'])),
            'ac_standard': float(prices_dict.get('ac_standard', DEFAULT_PRICES['ac_standard'])),
            'ac_inverter': float(prices_dict.get('ac_inverter', DEFAULT_PRICES['ac_inverter'])),
            'ac_premium': float(prices_dict.get('ac_premium', DEFAULT_PRICES['ac_premium'])),
            'extra_mounting': float(prices_dict.get('extra_mounting', DEFAULT_PRICES['extra_mounting'])),
            'warranty': float(prices_dict.get('warranty', DEFAULT_PRICES['warranty']))
        }
    except Exception as e:
        print(f"Ошибка загрузки цен: {str(e)}")
        return DEFAULT_PRICES


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
        'extra_mounting': prices_data['extra_mounting'],
        'warranty': prices_data['warranty']
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
                raise ValueError("Некорректные значения")

            if ac_type not in prices['ac']:
                raise ValueError("Неизвестный тип кондиционера")

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
def admin_orders():
    if current_user.id not in [1, 2]:
        return abort(403)
    db_sess = db_session.create_session()
    orders = db_sess.query(Order)
    return render_template("admin.html", orders=orders)


@app.route('/change_status/<int:order_id>', methods=['POST'])
@login_required
def change_status(order_id):
    db_sess = db_session.create_session()
    if current_user.id not in [1, 2]:
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
