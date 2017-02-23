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
        "data": {
            "type": "object",
            "additionalProperties": True
        }
    },
    "required": [
        "name",
        "data"
    ],
    "additionalProperties": False,
    "definitions": {
        "template-name": TEMPLATE_NAME
    }
}
