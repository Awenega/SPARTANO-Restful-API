from flask import Blueprint, make_response, jsonify, request
from model.refund import RefundSchema, RefundDbSchema
from database.query import get_refunds_database, insert_refunds_database, delete_refunds_database, delete_all_refunds_database

refund_bp = Blueprint('refund_bp', __name__)

@refund_bp.route('/refunds', methods=['GET', 'POST', 'DELETE'])
def refunds():
    if request.method == 'GET':
        from_date = request.args.get('from_date')
        if from_date is None:
            return make_response(jsonify({'error': 'from_date parameter is missing'}), 400)
        to_date = request.args.get('to_date', None)
        asin = request.args.get('asin', None)

        transactions = get_refunds_database(from_date, to_date, asin)
        schema = RefundDbSchema(many=True)
        refunds = schema.dump(transactions)

        return make_response(jsonify(refunds),200)
    
    elif request.method == 'POST':
        refunds_json = request.json
        refunds = RefundSchema(many=True).load(refunds_json)

        msg, code = insert_refunds_database(refunds)
        return make_response(jsonify(msg), code)
    
    elif request.method == 'DELETE':
        order_ids = request.json['order_ids']
        msg, code = delete_refunds_database(order_ids)

        return make_response(jsonify(msg), code)

@refund_bp.route('/refunds-all', methods=['DELETE'])
def delete_all_refunds():
    if request.method == 'DELETE':
        msg, code = delete_all_refunds_database()
        return make_response(jsonify(msg), code)