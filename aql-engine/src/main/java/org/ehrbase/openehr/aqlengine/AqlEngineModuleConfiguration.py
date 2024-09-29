# Copyright (c) 2024 vitasystems GmbH.
#
# This file is part of project EHRbase
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask
from flask_injector import FlaskInjector
from injector import singleton, inject

# Assuming a module-level scan (mimicking @ComponentScan in Java)
# We define components/modules below

class AqlEngineModule:
    # This would be where you configure your module's services
    pass

# Configuration class, analogous to @Configuration in Spring
class AqlEngineModuleConfiguration:
    
    def __init__(self, app: Flask):
        self.app = app
        self.configure_app()

    def configure_app(self):
        """
        Configures the application, equivalent to @ComponentScan and other annotations.
        """
        # Register the module or services (mimicking component scanning)
        FlaskInjector(app=self.app, modules=[AqlEngineModule])

# Create the Flask app and apply the configuration
def create_app():
    app = Flask(__name__)

    # Apply the configuration to the app
    AqlEngineModuleConfiguration(app)

    return app

# Run the Flask app
if __name__ == "__main__":
    app = create_app()
    app.run()





from fastapi import FastAPI, Depends
from fastapi_injector import Inject

class AqlEngineModule:
    def __init__(self):
        # Initialize module dependencies
        pass

# Dependency injection in FastAPI
def get_aql_engine_module():
    return AqlEngineModule()

# FastAPI app creation
app = FastAPI()

# Dependency injection using the 'Depends' mechanism in FastAPI
@app.get("/some-endpoint")
def some_endpoint(aql_module: AqlEngineModule = Depends(get_aql_engine_module)):
    # Use the AQL module logic
    return {"message": "Endpoint logic goes here"}

# To run: `uvicorn <module_name>:app --reload`
