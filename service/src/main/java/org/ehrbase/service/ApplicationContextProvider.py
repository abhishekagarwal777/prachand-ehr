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

from typing import Optional
from flask import Flask
from flask import current_app

class ApplicationContextProvider:
    _application_context: Optional[Flask] = None

    @classmethod
    def set_application_context(cls, application_context: Flask) -> None:
        cls._application_context = application_context

    @classmethod
    def get_application_context(cls) -> Optional[Flask]:
        return cls._application_context

# Example usage:
app = Flask(__name__)
ApplicationContextProvider.set_application_context(app)

# Accessing the application context elsewhere in your code:
with app.app_context():
    context = ApplicationContextProvider.get_application_context()
    if context:
        print("Application context is set.")
    else:
        print("Application context is not set.")
