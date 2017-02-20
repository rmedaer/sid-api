# -*- coding: utf-8 -*-

""" This module contains body schema for project management handlers. """

PROJECT_NAME = {
    "type": "string",
    "minLength": 2,
    "pattern": "^[A-Za-z0-9-_]*$"
}

PROJECT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "$ref": "#/definitions/project-name"
        },
        "rules": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "users": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "string"
                        }
                    },
                    "perm": {
                        "enum": ["RW", "C", "R"]
                    }
                },
                "required": [
                    "users",
                    "perm"
                ],
                "additionalProperties": False
            }
        }
    },
    "required": [
        "name",
        "rules"
    ],
    "additionalProperties": False,
    "definitions": {
        "project-name": PROJECT_NAME
    }
}

PROJECT_PATCH_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "op": {
                "enum": ["add", "replace", "remove"]
            },
            "path": {
                "type": "string",
                "pattern": r"^(\/name)|(\/rules\/[0-9]*)$"
            },
            "value": {
            }
        },
        "required": [
            "op",
            "path"
        ],
        "additionalProperties": False
    }
}
