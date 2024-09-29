# Copyright (c) 2024 vitasystems GmbH.
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      https://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum

class AuditDetailsTargetType(Enum):
    CONTRIBUTION = "CT"
    COMPOSITION = "CO"
    EHR_STATUS = "ES"
    EHR_FOLDER = "EF"

    def __init__(self, alias: str):
        self.alias = alias

    @property
    def get_alias(self) -> str:
        return self.alias

# Example usage
if __name__ == "__main__":
    # Print all target types and their aliases
    for target in AuditDetailsTargetType:
        print(f"{target.name}: {target.value}, Alias: {target.get_alias}")
