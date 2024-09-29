from enum import Enum

class OperationalTemplateFormat(Enum):
    XML = "XML"
    JSON = "JSON"

# Example usage
def get_template_format(template_format: OperationalTemplateFormat):
    if template_format == OperationalTemplateFormat.XML:
        print("Template is in XML format")
    elif template_format == OperationalTemplateFormat.JSON:
        print("Template is in JSON format")

get_template_format(OperationalTemplateFormat.JSON)
