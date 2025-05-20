from flask import jsonify
from flask_restful import abort, Resource, reqparse

from data import db_session
from data.orders import Order


def abort_if_news_not_found(news_id):
    session = db_session.create_session()
    order = session.query(Order).get(news_id)
    if not order:
        abort(404, message=f'News {news_id} not found')


parser = reqparse.RequestParser()
parser.add_argument('id', required=True, type=int)
parser.add_argument('user_name', required=True)
parser.add_argument('user_surname', required=True)
parser.add_argument('phone_number', required=True)
parser.add_argument('description', required=True)
parser.add_argument('address', required=True)
parser.add_argument('is_ready', required=True, type=bool)
parser.add_argument('created_date', required=True)
parser.add_argument('user_id', required=True, type=int)


class OrderResource(Resource):
    def get(self, order_id):
        abort_if_news_not_found(order_id)
        session = db_session.create_session()
        order = session.query(Order).get(order_id)
        return jsonify({'order': order.to_dict(
            only=('user_name', 'user_surname', 'phone_number', 'description', 'address', 'is_ready',
                  'created_date', 'user_id'))})

    def delete(self, order_id):
        abort_if_news_not_found(order_id)
        session = db_session.create_session()
        order = session.query(Order).get(order_id)
        session.delete(order)
        session.commit()
        return jsonify({'success': 'OK'})


class OrdersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        orders = session.query(Order).all()
        return jsonify({'orders': [item.to_dict(
            only=('id', 'user_name', 'user_surname', 'phone_number', 'description', 'address', 'is_ready',
                  'created_date', 'user_id')) for item in orders]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        order = Order(
            user_name=args['user_name'],
            user_surname=args['user_surname'],
            phone_number=args['phone_number'],
            description=args['description'],
            address=args['address'],
            user_id=args['user_id']
        )
        session.add(order)
        session.commit()
        return jsonify({'id': order.id})