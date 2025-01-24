from flask import Flask
from flask_cors import CORS
from src.main.controller.analyzer_controller import analyzer_blueprint

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Register the blueprint for the analyzer controller
app.register_blueprint(analyzer_blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)