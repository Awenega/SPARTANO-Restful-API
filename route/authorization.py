from flask import request, make_response, jsonify, current_app

def authorize_request():
    if 'Spartano-Api-Secret' not in request.headers or request.headers['Spartano-Api-Secret'] != current_app.config['SECRET_TOKEN']:
        return make_response(jsonify({"message": "Unauthorized access."}), 401)