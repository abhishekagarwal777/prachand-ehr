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

import json
from collections import OrderedDict
from io import StringIO
from typing import Optional
import re

class CompositionCleanup:

    @staticmethod
    def cleanup(composition_str: str, remove_structure_nodes: bool, remove_data_values: bool) -> str:
        """Clean up the composition structure."""
        comp = json.loads(composition_str)
        CompositionCleanup._cleanup(comp, remove_structure_nodes, remove_data_values)

        with StringIO() as sb:
            json.dump(comp, sb, indent=4, sort_keys=True)
            return sb.getvalue()

    @staticmethod
    def _cleanup(node, remove_structure_nodes: bool, remove_data_values: bool):
        """Recursive method to clean up the composition JSON."""
        if isinstance(node, list):
            for i, child in enumerate(node):
                CompositionCleanup._cleanup(child, remove_structure_nodes, remove_data_values)
                # Flatten simple child locatables
                if isinstance(child, dict) and len(child) == 1 and '_class' in child:
                    node[i] = child['_class']
        elif isinstance(node, dict):
            # Remove archetype_details but keep template_id
            if 'archetype_details' in node:
                archetyped = node.pop('archetype_details')
                if archetyped['archetype_id']['value'].startswith("openEHR-EHR-COMPOSITION"):
                    node['template_id'] = archetyped['template_id']
            
            fields = list(node.items())
            for key, value in fields:
                match key:
                    case 'language' | 'territory' | 'category' | 'composer' | 'context' | 'subject' | \
                         'rm_version' | 'encoding' | 'origin' | 'time' | 'math_function' | 'uid' | 'width':
                        node.pop(key)
                    case 'name' | 'template_id' | 'archetype_id':
                        node[key] = value['value']
                    case 'data' | 'state' | 'description' | 'wfDetails':
                        if remove_structure_nodes:
                            node.pop(key)
                        else:
                            CompositionCleanup._cleanup(value, remove_structure_nodes, remove_data_values)
                    case 'archetype_details':
                        if not value['archetype_id']['value'].startswith("openEHR-EHR-COMPOSITION"):
                            node.pop(key)
                        else:
                            CompositionCleanup._cleanup(value, remove_structure_nodes, remove_data_values)
                    case _:
                        CompositionCleanup._cleanup(value, remove_structure_nodes, remove_data_values)

            CompositionCleanup._remove_data_values(node, remove_data_values)
            CompositionCleanup._consolidate_to_class_exp(node)
            CompositionCleanup._reorder_attributes(node)

    @staticmethod
    def _remove_data_values(node: dict, remove_whole_attribute: bool):
        """Remove data values or attributes with DV_ type."""
        fields = list(node.items())
        for key, value in fields:
            if isinstance(value, dict) and value.get('_type', '').startswith('DV_'):
                if remove_whole_attribute:
                    node.pop(key)
                else:
                    node[key] = value['_type']

    @staticmethod
    def _consolidate_to_class_exp(node: dict):
        """Consolidate archetype_node_id into a _class field."""
        if 'archetype_node_id' in node:
            _type = node.pop('_type', '')
            archetype_node_id = node.pop('archetype_node_id', None)
            name = node.pop('name', None)

            sb = [_type]
            sb.append("[")

            if archetype_node_id:
                cleaned_archetype = re.sub(r'^openEHR-EHR-', '', archetype_node_id)
                sb.append(cleaned_archetype)

            if name:
                if archetype_node_id:
                    sb.append(",")
                sb.append(f"'{name}'")

            sb.append("]")
            node['_class'] = "".join(sb)

    @staticmethod
    def _reorder_attributes(node: dict):
        """Reorder the attributes of the object."""
        # Define the preferred order of fields
        field_order = OrderedDict()

        for field in ["_class", "archetype_node_id", "name", "_type"]:
            if field in node:
                field_order[field] = node.pop(field)

        # Add simple fields
        for key, value in list(node.items()):
            if not isinstance(value, dict) and not isinstance(value, list):
                field_order[key] = node.pop(key)

        # Add objects and lists
        for key, value in list(node.items()):
            if isinstance(value, dict) or isinstance(value, list):
                field_order[key] = node.pop(key)

        # Add remaining fields
        for key, value in node.items():
            field_order[key] = value

        node.clear()
        node.update(field_order)
