from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# Enabling CORS for all routes (if needed)
CORS(app)

# Module configuration
class RestEHRScapeModuleConfiguration:
    def __init__(self):
        self.base_package = "org.ehrbase.rest.ehrscape"

    def configure(self):
        # Any additional configuration can be added here
        pass

# Initialize the module configuration
module_configuration = RestEHRScapeModuleConfiguration()

# Application routes can be defined here
@app.route('/')
def index():
    return "Welcome to the EHRbase API"

if __name__ == "__main__":
    app.run(debug=True)
