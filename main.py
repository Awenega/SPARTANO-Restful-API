from flask import Flask
from route import orderRoute



def create_app():
    """Create Flask application."""
    app = Flask(__name__, instance_relative_config=False)

    with app.app_context():

        app.register_blueprint(orderRoute.order_bp)

        return app

app = create_app()
if __name__ == "__main__":
    app.run()