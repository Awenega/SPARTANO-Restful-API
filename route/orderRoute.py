from flask import Blueprint, make_response, jsonify, request
from model.order import OrderSchema, OrderDbSchema
from database.query import get_orders_database, insert_orders_database, delete_orders_database, delete_all_orders_database

order_bp = Blueprint('order_bp', __name__)

@order_bp.route('/orders', methods=['GET','POST', 'DELETE'])
def orders():
    if request.method == 'GET':
        from_date = request.args.get('from_date')
        if from_date is None:
            return make_response(jsonify({'error': 'from_date parameter is missing'}), 400)
        to_date = request.args.get('to_date', None)
        asin = request.args.get('asin', None)

        transactions = get_orders_database(from_date, to_date, asin)
        schema = OrderDbSchema(many=True)
        orders = schema.dump(transactions)
        return make_response(jsonify(orders),200)
    
    elif request.method == 'POST':
        orders_json = request.json
        orders = OrderSchema(many=True).load(orders_json)

        msg, code = insert_orders_database(orders)
        return make_response(jsonify(msg), code)
    
    elif request.method == 'DELETE':
        order_ids = request.json['order_ids']
        msg, code = delete_orders_database(order_ids)

        return make_response(jsonify(msg), code)

@order_bp.route('/orders-all', methods=['DELETE'])
def delete_all_orders():
    if request.method == 'DELETE':
        msg, code = delete_all_orders_database()
        return make_response(jsonify(msg), code)
