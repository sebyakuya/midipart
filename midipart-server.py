from flask import Flask
from flask_cors import CORS
from src.main.controller.analyzer_controller import analyzer_blueprint

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://web.midirating.com", "https://ntok5eh8dg.execute-api.eu-south-2.amazonaws.com", "http://midiloadbalancer-33bc8d136623c566.elb.eu-south-2.amazonaws.com"]}})

# Register the blueprint for the analyzer controller
app.register_blueprint(analyzer_blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)