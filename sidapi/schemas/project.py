# -*- coding: utf-8 -*-

""" This module contains body schema for project management handlers. """

PROJECT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
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
        "name"
    ],
    "additionalProperties": False
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
