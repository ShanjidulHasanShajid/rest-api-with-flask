import logging
from flask import Flask
from errors import register_error_handlers
from routes.api_bp import api_bp

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.register_blueprint(api_bp)

register_error_handlers(app) 

if __name__ == "__main__":
    app.run(debug=True)