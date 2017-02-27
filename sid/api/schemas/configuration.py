CONFIGURATION_SCHEMA = {
    "type": "object",
    "properties": {
        "app": {
            "type": "object",
            "properties": {
                "workspace_dir": {
                    "type": "string"
                },
                "remote_url": {
                    "type": "string"
                }
            },
            "required": [
                "workspace_dir",
                "remote_url"
            ]
        },
        "auth": {
            "type": "object",
            "properties": {
                "public_key_file": {
                    "type": "string"
                },
                "username_field": {
                    "type": "string"
                },
                "audience": {
                    "type": "string"
                },
                "algorithm": {
                    "type": "string"
                }
            },
            "required": [
                "public_key_file"
            ],
            "additionalProperties": False
        },
        "http": {
            "type": "object",
            "properties": {
                "port": {
                    "type": "string"
                }
            }
        }
    },
    "required": [
        "app",
        "auth"
    ]
}
