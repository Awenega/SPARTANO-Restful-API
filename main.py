from flask import Flask
from route import orderRoute
from route import refundRoute

def create_app():
    app = Flask(__name__, instance_relative_config=False)

    with app.app_context():
        app.register_blueprint(orderRoute.order_bp)
        app.register_blueprint(refundRoute.refund_bp)
        return app

app = create_app()
if __name__ == "__main__":
    app.run()