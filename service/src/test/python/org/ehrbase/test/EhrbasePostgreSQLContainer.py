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

import logging
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from docker import from_env
from typing import Optional

class EhrbasePostgreSQLContainer:
    DEFAULT_IMAGE_NAME = "ehrbase/ehrbase-v2-postgres:16.2"
    POSTGRESQL_PORT = 5432

    _shared_container: Optional['EhrbasePostgreSQLContainer'] = None

    def __init__(self):
        self.database_name = "ehrbase"
        self.username = "ehrbase"
        self.password = "ehrbase"
        self.host = None
        self.port = None
        self.container = None
        self.logger = logging.getLogger("📦 psql")

    @classmethod
    def shared_instance(cls):
        if cls._shared_container is None:
            cls._shared_container = cls()
            cls._shared_container.start()
        return cls._shared_container

    def start(self):
        client = from_env()
        self.logger.info("Starting PostgreSQL container...")
        self.container = client.containers.run(
            self.DEFAULT_IMAGE_NAME,
            detach=True,
            ports={f"{self.POSTGRESQL_PORT}/tcp": None},
            environment={
                "POSTGRES_DB": self.database_name,
                "POSTGRES_USER": self.username,
                "POSTGRES_PASSWORD": self.password,
            },
            auto_remove=True,
        )
        self.host = self.container.attrs['NetworkSettings']['IPAddress']
        self.port = self.POSTGRESQL_PORT

        self.wait_until_ready()

    def wait_until_ready(self):
        self.logger.info("Waiting for PostgreSQL to be ready...")
        while True:
            try:
                self.get_connection()
                break
            except OperationalError:
                self.logger.info("PostgreSQL is not ready yet. Retrying...")
                time.sleep(1)

    def get_connection(self):
        engine = create_engine(self.jdbc_url())
        return engine.connect()

    def jdbc_url(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}"

    def get_database_name(self) -> str:
        return self.database_name

    def get_username(self) -> str:
        return self.username

    def get_password(self) -> str:
        return self.password

    def get_test_query_string(self) -> str:
        return "SELECT 1"

    def with_database_name(self, database_name: str) -> 'EhrbasePostgreSQLContainer':
        self.database_name = database_name
        return self

    def with_username(self, username: str) -> 'EhrbasePostgreSQLContainer':
        self.username = username
        return self

    def with_password(self, password: str) -> 'EhrbasePostgreSQLContainer':
        self.password = password
        return self

    def run_init_script_if_required(self):
        # Implement Flyway migrations or equivalent initialization logic here
        pass

# Example usage:
# container = EhrbasePostgreSQLContainer.shared_instance()
