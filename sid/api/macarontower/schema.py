MACARONTOWER_SCHEMA = {
    "type": "object",
    "properties": {
        "version": {
            "type": "string",
            "pattern": "^\d*\.\d*\.\d*$"
        }
    },
    "required": [
        "version"
    ],
    "additionalProperties": True
}


MACARONTOWER_SCHEMA_1_0_0 = {
    "type": "object",
    "properties": {
        "version": {
            "type": "string",
            "pattern": "^\d*\.\d*\.\d*$"
        },
        "configs": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string"
                    },
                    "format": {
                        "enum": ["yml", "yaml", "json", "ini"]
                    },
                    "schema": {
                        "type": "string"
                    }
                },
                "required": [
                    "file",
                    "format"
                ]
            }
        }
    },
    "required": [
        "version",
        "configs"
    ],
    "additionalProperties": False
}
