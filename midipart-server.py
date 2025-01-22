from flask import Flask
from src.main.controller.analyzer_controller import analyzer_blueprint

app = Flask(__name__)

# Register the blueprint for the analyzer controller
app.register_blueprint(analyzer_blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)