import constants

POST_REQUEST_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'required': ['amount', 'memberValidation'],
    'properties': {
        'amount': {
            'type': 'integer',
            'minimum': 1
        },
        'memberValidation': {
            'type': 'string'
        }
    }
}


PATCH_REQUEST_SCHEMA = {
    'type': 'object',
    'required': ['status'],
    'additionalProperties': False,
    'properties': {
        'status': {
            'enum': [constants.STATUS_SUCCESS],
        },
    }
}
