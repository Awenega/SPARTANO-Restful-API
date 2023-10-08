from flask import Blueprint, make_response, jsonify, request
from model.setting import SettingSchema, SettingDbSchema
from database.query import get_settings_database, insert_settings_database, delete_settings_database, delete_all_settings_database

setting_bp = Blueprint('setting_bp', __name__)

@setting_bp.route('/settings', methods=['GET', 'POST', 'DELETE'])
def refunds():
    if request.method == 'GET':
        asin = request.args.get('asin', None)
        from_date = request.args.get('from_date', None)
        to_date = request.args.get('to_date', None)
        sales_channel= request.args.get('sales_channel', None)

        if any(variable is None for variable in (from_date, to_date, asin)):
            return make_response(jsonify({'error': 'a required parameter is missing'}), 400)

        transactions = get_settings_database(from_date, to_date, asin, sales_channel)
        schema = SettingDbSchema(many=True)
        refunds = schema.dump(transactions)

        return make_response(jsonify(refunds),200)
    
    elif request.method == 'POST':
        settings_json = request.json
        settings = SettingSchema(many=True).load(settings_json)

        msg, code = insert_settings_database(settings)
        return make_response(jsonify(msg), code)
    
    elif request.method == 'DELETE':
        final_msg = {'msg' : ''}
        request_parameters = request.json
        for refund in request_parameters:
            asin = refund['asin']
            sales_channel = refund['sales_channel']
            from_date = refund['from_date']
            msg, code = delete_settings_database(asin, sales_channel, from_date)
            final_msg['msg'] = final_msg['msg'] + " " + msg['msg']
        

        return make_response(jsonify(final_msg), code)

@setting_bp.route('/settings-all', methods=['DELETE'])
def delete_all_refunds():
    if request.method == 'DELETE':
        msg, code = delete_all_settings_database()
        return make_response(jsonify(msg), code)