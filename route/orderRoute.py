from flask import Blueprint, render_template, make_response, jsonify
from flask import current_app as app
from model.order import Order, OrderSchema
from model.transaction_type import TransactionType
from database.query import get_ordini_database

# Blueprint Configuration
order_bp = Blueprint('order_bp', __name__)


@order_bp.route('/orders', methods=['GET'])
def orders():
    transactions = get_ordini_database()
    schema = OrderSchema(many=True)
    orders = schema.dump(
        filter(lambda t: t.type == TransactionType.ORDER, transactions)
    )
    return make_response(jsonify(orders),200)


