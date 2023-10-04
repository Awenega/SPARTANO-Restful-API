from flask import Flask, jsonify, request
from datetime import datetime
from model.order import Order, OrderSchema
from model.refund import Refund, RefundSchema
from model.transaction_type import TransactionType

app = Flask(__name__)

transactions = [
    Order('123', datetime.now(), 'ZEUS', 1.0, 'Amazon.it', "", 1.0, 1.0, 1.0, 1.0, 1.0, 1.0),
    Refund('123', datetime.now(), 'ZEUS', 3, 'Amazon.it', 2.0, 3.0),
]

@app.route('/orders')
def get_orders():
    schema = OrderSchema(many=True)
    orders = schema.dump(
        filter(lambda t: t.type == TransactionType.ORDER, transactions)
    )
    print(orders)
    return jsonify(orders)


@app.route('/orders', methods=['POST'])
def add_order():
    order = OrderSchema().load(request.get_json())
    transactions.append(order)
    return "", 204


@app.route('/refunds')
def get_refunds():
    schema = RefundSchema(many=True)
    refunds = schema.dump(
        filter(lambda t: t.type == TransactionType.REFUND, transactions)
    )
    return jsonify(refunds)


@app.route('/refunds', methods=['POST'])
def add_refund():
    refund = RefundSchema().load(request.get_json())
    transactions.append(refund)
    return "", 204


if __name__ == "__main__":
    app.run()