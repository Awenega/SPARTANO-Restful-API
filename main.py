from flask import Flask, request
from route import orderRoute
from route import refundRoute
from route.authorization import authorize_request
import json

app = Flask(__name__, instance_relative_config=False)
    
with open("credentials.json", "r") as f:
    secret_token = json.load(f)
app.config['SECRET_TOKEN'] = secret_token['SECRET_TOKEN']

with app.app_context():
    app.register_blueprint(orderRoute.order_bp)
    app.register_blueprint(refundRoute.refund_bp)

@app.before_request
def before_request():
    return authorize_request()

if __name__ == "__main__":
    app.run()