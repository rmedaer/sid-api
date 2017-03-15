"""
This module contains schema for template handlers.
"""

TEMPLATE_NAME = {
    "type": "string",
    "minLength": 2,
    "pattern": "^[A-Za-z0-9-_]*$"
}

TEMPLATE_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "$ref": "#/definitions/template-name"
        },
        "version": {
            "type": "string"
        },
        "data": {
            "type": "object",
            "additionalProperties": True
        }
    },
    "required": [
        "name",
        "version",
        "data"
    ],
    "additionalProperties": False,
    "definitions": {
        "template-name": TEMPLATE_NAME
    }
}
