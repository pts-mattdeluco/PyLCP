from jsonschema._utils import load_schema

REQUEST = {
    'type': 'object',
    'required': ['schema'],
    'properties': {
        'schema': load_schema("draft4")
    }
}

RESPONSE = {
    'type': 'object',
    'required': ['balance'],
    'properties': {
        'balance': {
            'type': 'integer',
            'minimum': 0,
        },
    },
}