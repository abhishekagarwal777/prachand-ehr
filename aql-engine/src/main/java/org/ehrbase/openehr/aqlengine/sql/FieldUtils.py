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

from sqlalchemy import Column
from sqlalchemy.sql import table
from .asl_model.field import AslColumnField, AslComplexExtractedColumnField
from .asl_model.query import AslQuery, AslDataQuery

class FieldUtils:
    
    @staticmethod
    def field(sql_provider, asl_provider, owner, field_name, field_type, aliased):
        """
        Returns a SQLAlchemy column based on the ASL field and whether it is aliased.
        """
        asl_field = FieldUtils.find_field_by_owner_and_name(asl_provider, owner, field_name)
        return FieldUtils.create_field(sql_provider, asl_field, field_type, aliased)

    @staticmethod
    def find_field_by_owner_and_name(src, owner, column_name):
        """
        Finds the field in ASLQuery by owner and column name.
        """
        fields = [
            f for f in src.get_select()
            if isinstance(f, AslColumnField) and f.get_owner() == owner and f.get_column_name() == column_name
        ]
        if not fields:
            raise ValueError(f"field with columnName {column_name} not present")
        if len(fields) > 1:
            raise ValueError(f"found multiple fields with columnName {column_name}")
        return fields[0]

    @staticmethod
    def create_field(sql_provider, asl_field, field_type=None, aliased=False):
        """
        Creates a SQLAlchemy column from ASLField with optional aliasing and field type.
        """
        field_name = asl_field.get_name(aliased)
        if field_type:
            return Column(field_name, field_type)
        else:
            return Column(field_name)

    @staticmethod
    def field_from_complex(table_obj, asl_field, field_name, aliased):
        """
        Returns a column from a complex extracted ASL field, with optional aliasing.
        """
        return table_obj.c[asl_field.aliased_name(field_name) if aliased else field_name]

    @staticmethod
    def field_from_column(table_obj, asl_field, aliased):
        """
        Returns a column from an ASLColumnField with optional aliasing.
        """
        return table_obj.c[asl_field.get_name(aliased)]

    @staticmethod
    def aliased_field(target, asl_data, field_template):
        """
        Returns an aliased field based on template and ASL data query.
        """
        return FieldUtils.field(
            target, asl_data.get_base(), asl_data.get_base(), field_template.name, field_template.type, True
        )

    @staticmethod
    def aliased_field_with_type(target, asl_data, field_name, field_type):
        """
        Returns an aliased field with a specific type based on ASL data query.
        """
        return FieldUtils.field(target, asl_data.get_base(), asl_data.get_base(), field_name, field_type, True)
