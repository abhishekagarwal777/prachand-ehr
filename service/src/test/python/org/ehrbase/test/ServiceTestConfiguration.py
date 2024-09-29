# Copyright (c) 2019-2024 vitasystems GmbH.
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

import os
from datetime import datetime
from injector import Binder, Module, provider
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from my_app.ehrbase_postgres_container import EhrbasePostgreSQLContainer  # Adjust according to your app structure
from my_app.service import TimeProvider  # Adjust according to your app structure

# Set system properties to suppress JOOQ logs
os.environ["org.jooq.no-logo"] = "true"
os.environ["org.jooq.no-tips"] = "true"

class ServiceTestConfiguration(Module):
    """Configuration for service tests."""

    def configure(self, binder: Binder) -> None:
        """Configures the bindings for the test context."""
        binder.bind(TimeProvider, to=self.time_provider)

    @provider
    def data_source(self) -> sessionmaker:
        """Provides a SQLAlchemy session connected to the PostgreSQL container."""
        # Reuse the same postgres container for all Integration tests
        ehrdb = EhrbasePostgreSQLContainer.shared_instance()

        # Create a SQLAlchemy engine
        engine = create_engine(ehrdb.get_jdbc_url())
        return sessionmaker(bind=engine)

    def time_provider(self) -> callable:
        """Returns the current time as OffsetDateTime."""
        return datetime.now

    def initialize_test_context(self):
        """Initializes the test context for authentication."""
        # Simulate authentication
        from my_app.security import SecurityContextHolder  # Adjust according to your app structure
        SecurityContextHolder.set_authentication(
            principal="integration-test-principal",
            authorities=["integration-test-authority"]
        )

# Usage in tests
def setup_module(module):
    config = ServiceTestConfiguration()
    config.initialize_test_context()

